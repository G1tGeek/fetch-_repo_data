from bitbucket_client import get_all
from logger import log


def numbered_list(items):
    return "\n".join(f"{i+1}. {v}" for i, v in enumerate(items)) if items else ""


def process_repository(repo, idx, total, base_url, workspace, auth):
    slug = repo["slug"]
    log(f"[{idx}/{total}] Processing repo: {slug}")

    project = repo.get("project", {}).get("name", "")
    default_branch = repo.get("mainbranch", {}).get("name", "")

    branches = get_all(
        f"{base_url}/repositories/{workspace}/{slug}/refs/branches",
        auth
    )
    branch_names = [b["name"] for b in branches]

    protections = get_all(
        f"{base_url}/repositories/{workspace}/{slug}/branch-restrictions",
        auth,
        allow_403=True
    )
    protected = [
        f'{p.get("kind")}:{p.get("pattern","")}'
        for p in protections
    ]

    tags = get_all(
        f"{base_url}/repositories/{workspace}/{slug}/refs/tags",
        auth
    )
    tag_names = [t["name"] for t in tags]

    downloads = get_all(
        f"{base_url}/repositories/{workspace}/{slug}/downloads",
        auth,
        allow_402=True,
        allow_404=True
    )
    download_names = [d["name"] for d in downloads]

    permissions = get_all(
        f"{base_url}/repositories/{workspace}/{slug}/permissions-config/users",
        auth,
        allow_403=True
    )
    users = [
        f'{u["user"]["display_name"]}:{u["permission"]}'
        for u in permissions
    ]

    tokens = get_all(
        f"{base_url}/repositories/{workspace}/{slug}/access-tokens",
        auth,
        allow_403=True,
        allow_404=True
    )
    token_details = [
        f'{t["label"]}({"|".join(t.get("permissions", []))})'
        for t in tokens
    ]

    pipelines = get_all(
        f"{base_url}/repositories/{workspace}/{slug}/pipelines/",
        auth,
        allow_403=True
    )
    pipeline_states = [p["state"]["name"] for p in pipelines]

    hooks = get_all(
        f"{base_url}/repositories/{workspace}/{slug}/hooks",
        auth,
        allow_403=True
    )
    webhook_names = [h.get("description", "") for h in hooks]

    return {
        "workspace": workspace,
        "project": project,
        "repository": slug,
        "default_branch": default_branch,
        "branches": numbered_list(branch_names),
        "protected_branches": numbered_list(protected),
        "tags": numbered_list(tag_names),
        "releases": numbered_list(tag_names + download_names),
        "users_access": numbered_list(users),
        "repo_tokens": numbered_list(token_details),
        "pipelines": numbered_list(pipeline_states),
        "webhooks": numbered_list(webhook_names),
    }
