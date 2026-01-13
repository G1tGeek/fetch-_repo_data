import os
import yaml
from logger import log


def load_config(config_file="config.yaml", token_env="BITBUCKET_API_TOKEN"):
    """
    Loads application configuration and reads Bitbucket API token
    from an environment variable.

    Required ENV:
      BITBUCKET_API_TOKEN
    """

    log("Loading configuration")

    # Load YAML config
    with open(config_file) as f:
        config = yaml.safe_load(f)

    # Read API token from environment variable
    api_token = os.getenv(token_env)
    if not api_token:
        raise RuntimeError(
            f"Missing required environment variable: {token_env}"
        )

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
