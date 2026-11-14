# TSS_Python

Read or update secrets in a Thycotic/Delinea **Secret Server** over its REST
API. Usable as a library (`GetToken`, `GetSecret`, `UpdateSecret`) or a CLI.

## Install

```
pip install -e .        # from the repo root (installs secscripts)
pip install requests
```

## Credentials and endpoints

Credentials are read from the **environment**, never the command line (so they
never appear in a process list or shell history):

| Variable | Meaning |
|----------|---------|
| `TSS_USERNAME`, `TSS_PASSWORD` | Secret Server login. |
| `TSS_NEW_VALUE` | New password value (for `update`). |
| `TSS_TOKEN_URL` | OAuth token endpoint (or `--token-url`). |
| `TSS_SERVER_URL` | Secrets API base URL (or `--server-url`). |

Endpoint URLs are caller-supplied — nothing is hardcoded.

## Usage

```
export TSS_USERNAME=... TSS_PASSWORD=...
python Tools/TSS_Python/TSS_Python.py get    --id 42 --token-url URL --server-url URL
export TSS_NEW_VALUE='new password'
python Tools/TSS_Python/TSS_Python.py update --id 42 --token-url URL --server-url URL
```

`get` prints the secret via `--output-format` (`text`/`json`/`csv`). Exit
codes: `0` success, `1` auth/API error or missing config, `2` usage error.

## Known limitations

- The exact token and secrets endpoint paths vary by Secret Server version, so
  you supply the full URLs; this tool does not assume an API version.
- `get` output includes secret values by design — redirect/handle it carefully.
- No token caching; each invocation authenticates afresh.
