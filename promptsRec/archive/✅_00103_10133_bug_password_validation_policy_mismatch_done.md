Primary Executor: Gemini
Task Type: Bug Fix
Priority: P2
Stage: 133
Goal: Align frontend password change validation with backend policy
Dependencies: None
Execution: RUNPROMPT

---

## Context

The password change form in SettingsPage.vue allows users to set passwords with only 6 characters minimum. However, the backend password policy (defined in `backend/services/auth_service.py:50-56`) requires:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

This mismatch causes users to pass client-side validation but fail server-side validation when attempting to change passwords, resulting in poor UX.

## Required References

- **Frontend file**: `frontend/src/pages/settings/SettingsPage.vue` lines 316-328
- **Backend file**: `backend/services/auth_service.py` lines 47-57
- Backend validation logic:
  ```python
  if len(password) < 8:
      raise ValueError("new_password must be at least 8 characters")
  has_upper = any(ch.isupper() for ch in password)
  has_lower = any(ch.islower() for ch in password)
  has_digit = any(ch.isdigit() for ch in password)
  if not (has_upper and has_lower and has_digit):
      raise ValueError("new_password must include uppercase, lowercase, and digit characters")
  ```

## Core Task

Update the client-side password validation in SettingsPage.vue to match the backend password policy.

## Required Work

1. **Inspect the codebase**: Read `frontend/src/pages/settings/SettingsPage.vue` around lines 316-328 to understand current validation logic
2. **Update validation rules**:
   - Change minimum length from 6 to 8 characters
   - Add validation for at least one uppercase letter
   - Add validation for at least one lowercase letter
   - Add validation for at least one digit
3. **Update error messages** to match backend validation messages:
   - `新密码长度至少为 8 位` (change from 6 to 8)
   - `新密码必须包含大小写字母和数字` (new message for composition check)
4. **Consider UX**: Show specific feedback for which requirement is not met (length, uppercase, lowercase, digit)
5. **Verify**: Ensure frontend builds successfully after changes

## Constraints

- Only modify the password validation logic in SettingsPage.vue
- Do not change backend validation
- Error messages should be in Chinese (consistent with project language)
- Preserve existing form structure and other validation rules

## Completion Criteria

1. Frontend password validation accepts passwords with 8+ characters containing uppercase, lowercase, and digits
2. Error messages clearly indicate which password requirement is not met
3. Client-side validation now matches backend validation at `backend/services/auth_service.py:50-56`
4. Frontend builds successfully: `cd frontend && npm run build` passes
5. The change improves UX by preventing submission of passwords that will fail server-side validation
