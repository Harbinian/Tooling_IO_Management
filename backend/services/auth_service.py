# -*- coding: utf-8 -*-
"""
Authentication and RBAC helpers for the Tooling IO Management System.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import os
from typing import Dict, Optional

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from backend.services.rbac_service import build_permission_context, has_permission
from config.settings import settings
from database import DatabaseManager

logger = logging.getLogger(__name__)

TOKEN_SALT = "tooling-io-auth"
TOKEN_MAX_AGE_SECONDS = 8 * 60 * 60
PBKDF2_ITERATIONS = 390000


class AuthError(Exception):
    """Base authentication error."""


class InvalidCredentialsError(AuthError):
    """Raised when login credentials are invalid."""


class AuthenticationRequiredError(AuthError):
    """Raised when authentication is required."""


class PermissionDeniedError(AuthError):
    """Raised when permission validation fails."""


def _validate_new_password(new_password: str) -> str:
    """Validate new password complexity and return stripped value."""
    password = (new_password or "").strip()
    if not password:
        raise ValueError("new_password is required")
    if len(password) < 8:
        raise ValueError("new_password must be at least 8 characters")

    has_upper = any(ch.isupper() for ch in password)
    has_lower = any(ch.islower() for ch in password)
    has_digit = any(ch.isdigit() for ch in password)
    if not (has_upper and has_lower and has_digit):
        raise ValueError("new_password must include uppercase, lowercase, and digit characters")
    return password


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(settings.SECRET_KEY, salt=TOKEN_SALT)


def hash_password(password: str, salt: Optional[bytes] = None) -> str:
    """Create a PBKDF2 password hash string."""
    if not isinstance(password, str) or not password:
        raise ValueError("password must be a non-empty string")

    salt_bytes = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt_bytes,
        PBKDF2_ITERATIONS,
    )
    salt_encoded = base64.b64encode(salt_bytes).decode("ascii")
    digest_encoded = base64.b64encode(digest).decode("ascii")
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt_encoded}${digest_encoded}"


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a PBKDF2 password hash."""
    if not password or not password_hash:
        return False

    try:
        algorithm, iteration_text, salt_encoded, digest_encoded = password_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iteration_text)
        salt_bytes = base64.b64decode(salt_encoded.encode("ascii"))
        expected_digest = base64.b64decode(digest_encoded.encode("ascii"))
    except (ValueError, TypeError, base64.binascii.Error):
        return False

    actual_digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt_bytes,
        iterations,
    )
    return hmac.compare_digest(actual_digest, expected_digest)


def issue_auth_token(user_id: str) -> str:
    """Create a signed authentication token."""
    return _serializer().dumps({"user_id": user_id})


def parse_auth_token(token: str) -> Dict:
    """Decode and validate an authentication token."""
    try:
        return _serializer().loads(token, max_age=TOKEN_MAX_AGE_SECONDS)
    except SignatureExpired as exc:
        raise AuthenticationRequiredError("authentication token expired") from exc
    except BadSignature as exc:
        raise AuthenticationRequiredError("invalid authentication token") from exc


def _load_user_record_by_login_name(login_name: str) -> Optional[Dict]:
    from backend.services.rbac_service import ensure_rbac_tables
    ensure_rbac_tables()
    
    sql = """
    SELECT TOP 1
        user_id,
        login_name,
        display_name,
        employee_no,
        password_hash,
        status,
        default_org_id
    FROM sys_user
    WHERE login_name = ?
    """
    rows = DatabaseManager().execute_query(sql, (login_name,))
    return rows[0] if rows else None


def _load_user_record_by_user_id(user_id: str) -> Optional[Dict]:
    sql = """
    SELECT TOP 1
        user_id,
        login_name,
        display_name,
        employee_no,
        password_hash,
        status,
        default_org_id
    FROM sys_user
    WHERE user_id = ?
    """
    rows = DatabaseManager().execute_query(sql, (user_id,))
    return rows[0] if rows else None


def _update_last_login(user_id: str) -> None:
    sql = """
    UPDATE sys_user
    SET last_login_at = GETDATE(),
        updated_at = GETDATE(),
        updated_by = ?
    WHERE user_id = ?
    """
    DatabaseManager().execute_query(sql, (user_id, user_id), fetch=False)


def _write_password_change_audit_log(
    *,
    user_id: str,
    changed_by: str,
    change_result: str,
    remark: str = "",
    client_ip: str = "",
) -> None:
    """Persist one password-change audit log row, without affecting main flow."""
    if not user_id:
        return

    try:
        DatabaseManager().execute_query(
            """
            INSERT INTO sys_user_password_change_log (
                user_id, changed_by, change_result, remark, client_ip, changed_at
            )
            VALUES (?, ?, ?, ?, ?, SYSDATETIME())
            """,
            (
                user_id,
                changed_by or user_id,
                change_result,
                remark or "",
                client_ip or "",
            ),
            fetch=False,
        )
    except Exception as exc:
        logger.warning("failed to write password change audit log for user %s: %s", user_id, exc)


def _build_user_identity(user_record: Dict) -> Dict:
    from backend.services.org_service import resolve_user_org_context

    permission_context = build_permission_context(user_record.get("user_id", ""))
    roles = permission_context["roles"]
    permissions = permission_context["permissions"]
    org_context = resolve_user_org_context(
        user_record.get("user_id", ""),
        user_record.get("default_org_id", ""),
    )

    return {
        "user_id": user_record.get("user_id", ""),
        "login_name": user_record.get("login_name", ""),
        "display_name": user_record.get("display_name", ""),
        "employee_no": user_record.get("employee_no", ""),
        "status": user_record.get("status", ""),
        "default_org_id": user_record.get("default_org_id", ""),
        "roles": roles,
        "role_codes": permission_context["role_codes"],
        "permissions": permissions,
        "default_org": org_context.get("default_org"),
        "current_org": org_context.get("current_org"),
        "role_orgs": org_context.get("role_orgs", []),
    }


def authenticate_user(login_name: str, password: str) -> Dict:
    """Authenticate a local account and return token plus identity."""
    login_name = (login_name or "").strip()
    if not login_name or not password:
        raise InvalidCredentialsError("login_name and password are required")

    user_record = _load_user_record_by_login_name(login_name)
    if not user_record or not verify_password(password, user_record.get("password_hash", "")):
        raise InvalidCredentialsError("invalid login credentials")

    status = (user_record.get("status") or "").lower()
    if status != "active":
        raise InvalidCredentialsError(f"user status does not allow login: {status or 'unknown'}")

    user = _build_user_identity(user_record)
    token = issue_auth_token(user["user_id"])
    _update_last_login(user["user_id"])
    return {"token": token, "user": user}


def get_current_user_from_token(token: str) -> Dict:
    """Resolve a signed token to the current user identity."""
    payload = parse_auth_token(token)
    user_id = payload.get("user_id", "")
    if not user_id:
        raise AuthenticationRequiredError("authentication token payload is invalid")

    user_record = _load_user_record_by_user_id(user_id)
    if not user_record:
        raise AuthenticationRequiredError("authenticated user no longer exists")

    status = (user_record.get("status") or "").lower()
    if status != "active":
        raise AuthenticationRequiredError("authenticated user is not active")

    return _build_user_identity(user_record)


def require_permission(user: Dict, permission_code: str) -> None:
    """Validate that the resolved user has one permission."""
    if not user:
        raise AuthenticationRequiredError("authentication required")

    if not has_permission(user, permission_code):
        raise PermissionDeniedError(f"missing required permission: {permission_code}")


def change_current_user_password(
    *,
    user_id: str,
    old_password: str,
    new_password: str,
    client_ip: str = "",
) -> None:
    """Change the current authenticated user's password."""
    from backend.services.rbac_service import ensure_rbac_tables

    ensure_rbac_tables()
    normalized_user_id = (user_id or "").strip()
    if not normalized_user_id:
        raise AuthenticationRequiredError("authentication required")

    old_password_value = (old_password or "").strip()
    if not old_password_value:
        raise ValueError("old_password is required")

    validated_new_password = _validate_new_password(new_password)
    if old_password_value == validated_new_password:
        raise ValueError("new_password must be different from old_password")

    user_record = _load_user_record_by_user_id(normalized_user_id)
    if not user_record:
        raise AuthenticationRequiredError("authenticated user no longer exists")

    if not verify_password(old_password_value, user_record.get("password_hash", "")):
        _write_password_change_audit_log(
            user_id=normalized_user_id,
            changed_by=normalized_user_id,
            change_result="failed",
            remark="old_password_mismatch",
            client_ip=client_ip,
        )
        raise InvalidCredentialsError("old_password is incorrect")

    DatabaseManager().execute_query(
        """
        UPDATE sys_user
        SET password_hash = ?,
            updated_at = SYSDATETIME(),
            updated_by = ?
        WHERE user_id = ?
        """,
        (
            hash_password(validated_new_password),
            normalized_user_id,
            normalized_user_id,
        ),
        fetch=False,
    )
    _write_password_change_audit_log(
        user_id=normalized_user_id,
        changed_by=normalized_user_id,
        change_result="success",
        remark="password_changed",
        client_ip=client_ip,
    )


def get_bootstrap_admin_sql(login_name: str = "admin", password_hash: str = "") -> str:
    """Return SQL that can create the first admin account."""
    return f"""
INSERT INTO sys_user (
    user_id, login_name, display_name, password_hash, status, created_at, created_by
)
VALUES (
    'U_ADMIN',
    '{login_name}',
    'System Administrator',
    '{password_hash}',
    'active',
    SYSDATETIME(),
    'bootstrap'
);

INSERT INTO sys_user_role_rel (
    user_id, role_id, org_id, is_primary, status, created_at, created_by
)
VALUES (
    'U_ADMIN',
    'ROLE_SYS_ADMIN',
    NULL,
    1,
    'active',
    SYSDATETIME(),
    'bootstrap'
);
""".strip()
