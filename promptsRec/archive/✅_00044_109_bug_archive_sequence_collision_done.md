Primary Executor: Claude Code
Task Type: Bug Fix
Stage: 109
Goal: Fix duplicate archive sequence numbers in prompt task pipeline
Execution: RUNPROMPT

---

# Context

The repository workflow documents (`docs/AI_PIPELINE.md`, `docs/PROMPT_TASK_CONVENTION.md`) define archive sequence numbers as sequential lifecycle artifacts.

Currently, there are duplicate archive sequence numbers which breaks the convention.

---

# Problem

**Files**:
- `promptsRec/✅_00037_030_rbac_permission_enforcement.md`
- `promptsRec/✅_00037_033_login_page_and_auth_flow_ui_done.md`

**Current Behavior**:
- Two archived prompt files share the same archive sequence `00037`
- The workflow documents describe the archive number as a sequencing convention
- Duplicate archive sequence numbers undermine ordering and dashboard assumptions

**Impact**:
- Any tooling that sorts by archive sequence can report wrong completion order
- Pipeline-dashboard skill depends on prompt archive naming conventions
- Creates non-canonical prompt history

---

# References

- `docs/AI_PIPELINE.md` - AI pipeline documentation
- `docs/PROMPT_TASK_CONVENTION.md` - Prompt task convention

---

# Requirements

1. Reassign one of the duplicate archive numbers (e.g., change 00037_033 to 00038)
2. Ensure all archive numbers are sequential and unique
3. Add a pre-archive validation step to catch duplicate sequence numbers in future

---

# Verification

After fix:
- All archive files should have unique sequence numbers
- Archive sequence should be sequential
- Pipeline-dashboard should work correctly
