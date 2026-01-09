import requests
from logger import log


def get_all(url, auth, allow_403=False, allow_404=False, allow_402=False):
    results = []

    while url:
        r = requests.get(url, auth=auth)

        if r.status_code == 403 and allow_403:
            log(f"403 skipped (no permission): {url}", "WARN")
            return []

        if r.status_code == 404 and allow_404:
            log(f"404 skipped (feature not enabled): {url}", "WARN")
            return []

        if r.status_code == 402 and allow_402:
            log(f"402 skipped (plan restriction): {url}", "WARN")
            return []

        r.raise_for_status()

        data = r.json()
        results.extend(data.get("values", []))
        url = data.get("next")

    return results


def fetch_repositories(base_url, workspace, auth):
    log("Fetching repositories")
    return get_all(f"{base_url}/repositories/{workspace}", auth)
