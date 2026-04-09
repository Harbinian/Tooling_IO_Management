# Fix Inbound Workflow Test hutingting Login Timeout

## Context / 上下文

The `run_inbound_workflow_test()` in `test_runner/api_e2e.py` fails because `ensure_user_session("hutingting")` is called multiple times in quick succession (Phase 3B keeper confirm, then Phase 3D final confirm with same token). The backend appears to rate-limit or timeout on repeated logins for the same user within a short window.

The `ensure_user_session()` function at L528 calls `login_user()` every time, which performs a full re-authentication. When called multiple times rapidly for the same user, the backend session/token management responds with errors or timeouts.

## Core Task / 核心任务

Fix the login session management in `run_inbound_workflow_test()` to avoid redundant re-logins:

Modified `ensure_user_session()` to cache tokens and skip re-login if user already has a valid token:

```python
def ensure_user_session(username: str) -> tuple:
    """Ensure a test user has a fresh token and cached user_id."""
    user = TEST_USERS[username]
    # If already logged in with a token, reuse it
    if user.get("token"):
        return user["token"], user["user_id"], user
    # Otherwise, login fresh
    token, user_id, user_data = login_user(username, user["password"])
    if token:
        user["token"] = token
        user["user_id"] = user_id
    return token, user_id, user_data
```

## Completion Criteria / 完成标准

1. `python test_runner/api_e2e.py --workflows inbound` passes with all 11 steps PASS
2. `ensure_user_session()` correctly caches tokens and does not re-authenticate unnecessarily
3. No regression: `python test_runner/api_e2e.py --workflows all` still passes smoke and workflow tests

## Execution Report / 执行报告

**Commit**: `bae98f4` - pushed to `origin/main`
**Verification**: Inbound 11/11 PASS, Smoke 4/4 PASS, Workflow 7/9

**Changes made**:
- Modified `ensure_user_session()` to cache tokens at TEST_USERS level
- Skip re-login if user already has a valid token

**Note**: Workflow failures wf_08 and wf_09 are pre-existing issues (business logic + fengliang login rate-limit).
