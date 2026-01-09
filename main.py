from logger import log, init_logger
from config_loader import load_config
from bitbucket_client import fetch_repositories
from repository_processor import process_repository
from writers import write_csv, write_excel


def main():
    init_logger()
    log("Starting Bitbucket Inventory Job")

    cfg = load_config()
    auth = (cfg["email"], cfg["api_token"])

    repos = fetch_repositories(
        cfg["base_url"],
        cfg["workspace"],
        auth
    )

    rows = []
    for idx, repo in enumerate(repos, start=1):
        rows.append(
            process_repository(
                repo,
                idx,
                len(repos),
                cfg["base_url"],
                cfg["workspace"],
                auth
            )
        )

    write_csv(rows, cfg["csv_file"])
    write_excel(rows, cfg["excel_file"])

    log(f"Done ✅ CSV: {cfg['csv_file']}, Excel: {cfg['excel_file']}")


if __name__ == "__main__":
    main()
