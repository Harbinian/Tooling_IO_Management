# G1-4 Detect Secrets Setup

## Prerequisite

G1-4 requires `detect-secrets` tool from Yelp:

```bash
pip install detect-secrets
```

## One-time Setup

1. **Install detect-secrets**:
   ```bash
   pip install detect-secrets==1.4.0
   ```

2. **Generate baseline** (one-time per repository):
   ```bash
   detect-secrets scan > .secrets.baseline
   ```

3. **Review and update baseline**:
   - Remove false positives (e.g., test credentials)
   - Add entries marked as `whitelist`

4. **Commit baseline**:
   ```bash
   git add .secrets.baseline
   git commit -m "chore: add detect-secrets baseline"
   ```

## Usage

The pre-commit hook will automatically check for secrets on commit.

To scan manually:
```bash
detect-secrets scan .
```

To audit:
```bash
detect-secrets audit .secrets.baseline
```

## Whitelist Format

Add to `.secrets.baseline` in the `exclude` section:
```json
{
  "exclude": {
    "files": "tests/fixtures/.*",
    "lines": "password = 'test'"
  }
}
```

## Notes

- Baseline file must be committed for CI to work
- False positives can be added to `whitelist` array in baseline
- Run `detect-secrets scan --update .secrets.baseline` to refresh after auditing
