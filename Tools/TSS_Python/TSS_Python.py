#!/usr/bin/env python3
"""
Authenticate to and read/update secrets in a Thycotic/Delinea Secret Server
instance over its REST API.

Usage:
    # Credentials come from the environment, never the command line:
    export TSS_USERNAME=... TSS_PASSWORD=...
    python TSS_Python.py get --token-url https://ss/oauth2/token \\
        --server-url https://ss/api/v1/secrets --id 42
    export TSS_NEW_VALUE='new password'
    python TSS_Python.py update --token-url ... --server-url ... --id 42

Requirements:
    requests; secscripts (pip install -e .).

Importable as a library (GetToken/GetSecret/UpdateSecret) or run as a CLI.
Endpoint URLs are supplied by the caller (flags or TSS_TOKEN_URL /
TSS_SERVER_URL env vars); nothing is hardcoded.
"""

import os
import sys
from pathlib import Path

import requests

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from secscripts.cli import EXIT_ERROR, EXIT_OK, build_parser  # noqa: E402
from secscripts.log import configure  # noqa: E402
from secscripts.output import emit  # noqa: E402

_SECRET_FIELD_MAP = {
    "Username": "user",
    "Password": "pass",
    "Location": "location",
    "Notes": "notes",
    "Directory (tenant) ID": "tenantid",
    "Application (client) ID": "clientid",
    "Client Secret": "clientsecret",
}


class TSSError(Exception):
    """Raised on an authentication or API error (so callers can handle it)."""


def GetToken(token_url, username, password):
    """Return an OAuth access token, or raise TSSError."""
    headers = {
        "Accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
    }
    payload = {"username": username, "password": password, "grant_type": "password"}
    auth = requests.post(token_url, data=payload, headers=headers)
    if auth.status_code == 200 and "An error has occurred" not in auth.text:
        try:
            return auth.json()["access_token"]
        except (ValueError, KeyError) as exc:
            raise TSSError(f"token response missing access_token: {exc}") from exc
    raise TSSError(f"error retrieving token (status {auth.status_code})")


def GetSecret(server_url, token, secret_id):
    """Fetch a secret by id and return a normalised dict, or raise TSSError."""
    headers = {"Authorization": f"Bearer {token}", "content-type": "application/json"}
    url = f"{server_url.rstrip('/')}/{secret_id}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise TSSError(f"error retrieving secret {secret_id} (status {response.status_code})")
    body = response.json()
    data = {"name": body.get("name", "")}
    data.update(dict.fromkeys(_SECRET_FIELD_MAP.values(), ""))
    for item in body.get("items", []):
        key = _SECRET_FIELD_MAP.get(item.get("fieldName"))
        if key is not None:
            data[key] = item.get("itemValue", "")
    return data


def UpdateSecret(server_url, token, secret_id, new_secret_value):
    """Set a secret's Password field. Return True, or raise TSSError."""
    url = f"{server_url.rstrip('/')}/{secret_id}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "SecretId": secret_id,
        "Items": [{"FieldName": "Password", "Value": new_secret_value}],
    }
    response = requests.put(url, headers=headers, json=payload)
    if response.status_code == 200:
        return True
    raise TSSError(f"failed to update secret {secret_id} (status {response.status_code})")


def _require(value, name, logger):
    if not value:
        logger.error("%s is required (set it or pass the matching flag)", name)
        raise TSSError(name)
    return value


def main(argv=None):
    parser = build_parser(
        "Read or update secrets in a Thycotic/Delinea Secret Server.",
        prog="TSS_Python",
    )
    parser.add_argument(
        "action", choices=["get", "update"], help="get a secret or update its password"
    )
    parser.add_argument("--id", required=True, help="secret id")
    parser.add_argument(
        "--token-url", default=os.getenv("TSS_TOKEN_URL"), help="OAuth token endpoint"
    )
    parser.add_argument(
        "--server-url", default=os.getenv("TSS_SERVER_URL"), help="secrets API base URL"
    )
    args = parser.parse_args(argv)
    logger = configure(args, name="TSS_Python")

    try:
        token_url = _require(args.token_url, "--token-url/TSS_TOKEN_URL", logger)
        server_url = _require(args.server_url, "--server-url/TSS_SERVER_URL", logger)
        username = _require(os.getenv("TSS_USERNAME"), "TSS_USERNAME", logger)
        password = _require(os.getenv("TSS_PASSWORD"), "TSS_PASSWORD", logger)

        token = GetToken(token_url, username, password)
        if args.action == "get":
            emit([GetSecret(server_url, token, args.id)], args.output_format)
        else:
            new_value = _require(os.getenv("TSS_NEW_VALUE"), "TSS_NEW_VALUE", logger)
            UpdateSecret(server_url, token, args.id, new_value)
            logger.info("secret %s updated", args.id)
    except TSSError as exc:
        logger.error("%s", exc)
        return EXIT_ERROR
    except requests.RequestException as exc:
        logger.error("request failed: %s", exc)
        return EXIT_ERROR

    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
