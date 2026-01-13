#  Bitbucket Inventory Fetch Script

## 1. Purpose
This script collects a complete inventory of Bitbucket repositories in a workspace and exports the data to CSV and Excel formats.

It is used for:
- Repository auditing
- Access review (users, tokens, webhooks)
- Branch & protection analysis
- CI/CD and governance assessments

## 2. Scope
The script fetches the following details per repository:
- Workspace & project
- Repository name
- Default branch
- All branches
- Protected branches
- Tags & releases
- User access & permissions
- Repository access tokens
- Pipelines
- Webhooks

## 3. Preconditions
### System Requirements
- Python 3.9+
- Internet access to Bitbucket Cloud
- Read permissions on Bitbucket workspace

### Python Dependencies
```bash
pip install requests pyyaml openpyxl
```

## 4. Configuration
### config.yaml (Non-Secret)
```yaml
bitbucket:
  workspace: opstree-pinelabs
  base_url: https://api.bitbucket.org/2.0
  email: user@example.com

output:
  csv_file: bitbucket_inventory.csv
```

### Environment Variable (Secret)
```bash
export BITBUCKET_API_TOKEN=<bitbucket_app_password>
```

## 5. Execution Procedure
```bash
python3 main.py
```

### Execution Flow
1. Logger initializes
2. Configuration is loaded
3. Bitbucket repositories are discovered
4. Each repository is processed sequentially
5. API pagination is handled
6. CSV and Excel reports are generated

## 6. Output Artifacts
- CSV report
- Excel report
- Execution logs

## 7. Error Handling
- 403: Permission skipped
- 404: Feature not enabled
- 402: Plan restriction
- Missing token: Script exits

## 8. Security & Compliance
- No secrets stored in code or files
- Tokens loaded only from environment
- Logs do not expose credentials

## 9. Best Practices
- Use read-only Bitbucket app passwords
- Rotate tokens periodically
- Archive reports for audits
