import csv
import requests
import yaml
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Alignment

# --------------------------------------------------
# Logging
# --------------------------------------------------
def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")

# --------------------------------------------------
# Load config
# --------------------------------------------------
log("Loading configuration")

with open("config.yaml") as f:
    config = yaml.safe_load(f)

WORKSPACE = config["bitbucket"]["workspace"]
BASE_URL = config["bitbucket"]["base_url"].rstrip("/")
EMAIL = config["bitbucket"]["email"]
CSV_FILE = config["output"]["csv_file"]
EXCEL_FILE = CSV_FILE.replace(".csv", ".xlsx")

with open("api_token") as f:
    API_TOKEN = f.read().strip()

AUTH = (EMAIL, API_TOKEN)

# --------------------------------------------------
# Helpers
# --------------------------------------------------
def get_all(url, allow_403=False, allow_404=False, allow_402=False):
    """
    Generic GET-only paginator with Bitbucket-safe error handling
    """
    results = []
    while url:
        r = requests.get(url, auth=AUTH)

        if r.status_code == 403 and allow_403:
            log(f"403 skipped (no permission): {url}")
            return []

        if r.status_code == 404 and allow_404:
            log(f"404 skipped (feature not enabled): {url}")
            return []

        if r.status_code == 402 and allow_402:
            log(f"402 skipped (plan restriction): {url}")
            return []

        r.raise_for_status()

        data = r.json()
        results.extend(data.get("values", []))
        url = data.get("next")

    return results


def numbered_list(items):
    """
    Convert list into Excel-friendly numbered multiline string
    """
    return "\n".join(f"{i+1}. {v}" for i, v in enumerate(items)) if items else ""

# --------------------------------------------------
# Fetch repositories
# --------------------------------------------------
log("Fetching repositories")
repos = get_all(f"{BASE_URL}/repositories/{WORKSPACE}")

rows = []

for idx, repo in enumerate(repos, start=1):
    slug = repo["slug"]
    log(f"[{idx}/{len(repos)}] Processing repo: {slug}")

    project = repo.get("project", {}).get("name", "")
    default_branch = repo.get("mainbranch", {}).get("name", "")

    # ---------------- Branches ----------------
    branches = get_all(
        f"{BASE_URL}/repositories/{WORKSPACE}/{slug}/refs/branches"
    )
    branch_names = [b["name"] for b in branches]

    # ---------------- Protected Branches ----------------
    protections = get_all(
        f"{BASE_URL}/repositories/{WORKSPACE}/{slug}/branch-restrictions",
        allow_403=True
    )
    protected = [
        f'{p.get("kind")}:{p.get("pattern","")}'
        for p in protections
    ]

    # ---------------- Tags (Releases source #1) ----------------
    tags = get_all(
        f"{BASE_URL}/repositories/{WORKSPACE}/{slug}/refs/tags"
    )
    tag_names = [t["name"] for t in tags]

    # ---------------- Downloads (Releases source #2, optional) ----------------
    downloads = get_all(
        f"{BASE_URL}/repositories/{WORKSPACE}/{slug}/downloads",
        allow_402=True,
        allow_404=True
    )
    download_names = [d["name"] for d in downloads]

    releases = tag_names + download_names

    # ---------------- User Access ----------------
    permissions = get_all(
        f"{BASE_URL}/repositories/{WORKSPACE}/{slug}/permissions-config/users",
        allow_403=True
    )
    users = [
        f'{u["user"]["display_name"]}:{u["permission"]}'
        for u in permissions
    ]

    # ---------------- Repo Tokens ----------------
    tokens = get_all(
        f"{BASE_URL}/repositories/{WORKSPACE}/{slug}/access-tokens",
        allow_403=True,
        allow_404=True
    )
    token_details = [
        f'{t["label"]}({"|".join(t.get("permissions", []))})'
        for t in tokens
    ]

    # ---------------- Pipelines ----------------
    pipelines = get_all(
        f"{BASE_URL}/repositories/{WORKSPACE}/{slug}/pipelines/",
        allow_403=True
    )
    pipeline_states = [p["state"]["name"] for p in pipelines]

    # ---------------- Webhooks ----------------
    hooks = get_all(
        f"{BASE_URL}/repositories/{WORKSPACE}/{slug}/hooks",
        allow_403=True
    )
    webhook_names = [h.get("description", "") for h in hooks]

    rows.append({
        "workspace": WORKSPACE,
        "project": project,
        "repository": slug,
        "default_branch": default_branch,
        "branches": numbered_list(branch_names),
        "protected_branches": numbered_list(protected),
        "tags": numbered_list(tag_names),
        "releases": numbered_list(releases),
        "users_access": numbered_list(users),
        "repo_tokens": numbered_list(token_details),
        "pipelines": numbered_list(pipeline_states),
        "webhooks": numbered_list(webhook_names),
    })

# --------------------------------------------------
# Write CSV
# --------------------------------------------------
log("Writing CSV")
with open(CSV_FILE, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

# --------------------------------------------------
# Write Excel (formatted lists)
# --------------------------------------------------
log("Generating Excel")
wb = Workbook()
ws = wb.active
ws.title = "Bitbucket Inventory"

headers = list(rows[0].keys())
ws.append(headers)

for row in rows:
    ws.append(list(row.values()))

wrap_columns = {
    "branches", "protected_branches", "tags", "releases",
    "users_access", "repo_tokens", "pipelines", "webhooks"
}

for col_idx, col_name in enumerate(headers, start=1):
    if col_name in wrap_columns:
        for col in ws.iter_cols(min_col=col_idx, max_col=col_idx, min_row=2):
            for cell in col:
                cell.alignment = Alignment(wrap_text=True, vertical="top")

wb.save(EXCEL_FILE)

log(f"Done ✅ CSV: {CSV_FILE}, Excel: {EXCEL_FILE}")
