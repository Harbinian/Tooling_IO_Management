# E2E Runner Agent

## Purpose
Executes end-to-end testing for the DocOps system, verifying full pipeline execution.

## E2E Test Flow

### Required Pipeline Sequence
All E2E tests MUST execute in this exact order:

1. **mine** - Term mining
   ```bash
   python scripts/mine_terms.py --docs ./outputs
   ```

2. **promote** - Promote candidates to glossary
   ```bash
   python scripts/promote_terms.py
   ```

3. **validate** - Data integrity check (GATEKEEPER)
   ```bash
   python scripts/validate_data.py
   ```
   **BLOCKER**: If validation fails, stop pipeline immediately

4. **export** - Export to system formats
   ```bash
   python scripts/export_to_system.py
   python scripts/export_for_tooling_app.py
   ```

### Output Verification
After each step, verify:
- Exit code is 0
- Expected output files exist
- JSON output is valid (parseable)

### Expected Output Files
| Step | Output File | Location |
|------|-------------|----------|
| mine | `term_candidates.csv` | Root |
| promote | `glossary.yaml` | Root |
| validate | (no output, exit 0 = pass) | - |
| export | `dist/tooling_system_init_data.json` | dist/ |
| export | `dist/tooling_master_data.json` | dist/ |

## Test Commands

```bash
# Full pipeline E2E
bash scripts/e2e_pipeline.sh

# Individual step tests
pytest tests/test_mine_terms.py -v
pytest tests/test_promote_terms.py -v
pytest tests/test_validate.py -v
pytest tests/test_export.py -v
```

## JSON Output Validation
All JSON exports must pass:
1. `json.load()` - Valid JSON syntax
2. Schema validation - Required fields present
3. Data integrity - No null required fields

## Error Handling
- Log all step outputs
- Capture stderr for debugging
- Fail fast on critical errors

## Trigger
Use for:
- Pre-release verification
- Post-deployment smoke tests
- Regression testing
