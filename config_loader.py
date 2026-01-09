import yaml
from logger import log


def load_config(config_file="config.yaml", token_file="api_token"):
    log("Loading configuration")

    with open(config_file) as f:
        config = yaml.safe_load(f)

    with open(token_file) as f:
        api_token = f.read().strip()

    bitbucket = config["bitbucket"]
    output = config["output"]

    return {
        "workspace": bitbucket["workspace"],
        "base_url": bitbucket["base_url"].rstrip("/"),
        "email": bitbucket["email"],
        "api_token": api_token,
        "csv_file": output["csv_file"],
        "excel_file": output["csv_file"].replace(".csv", ".xlsx"),
    }
