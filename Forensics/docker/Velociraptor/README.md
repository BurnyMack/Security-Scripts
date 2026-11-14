# Velociraptor stack

Runs a [Velociraptor](https://docs.velociraptor.app/) endpoint-DFIR server with
its web GUI, for hunting and collecting artefacts from deployed agents.

## Usage

```
VELOX_USER=admin VELOX_PASSWORD='choose-a-strong-one' \
  docker compose -f Forensics/docker/Velociraptor/docker-compose.yml up -d
# GUI: https://localhost:8889  (self-signed TLS)
```

Agents connect to the frontend on port 8000. Server config and datastore
persist in the `velociraptor-data` volume.

## Hardening

- **Digest-pinned** image (no floating tag).
- **Healthcheck** on the GUI port (self-signed TLS, so the check uses `-k`).
- Credentials come from `VELOX_USER`/`VELOX_PASSWORD` env vars — **set a strong
  password**; the defaults are placeholders.

## Caveats

Validated with `docker compose config`, not run end-to-end here. This is a
community image (`wlambert/velociraptor`); review its documented environment
variables and generate a proper server config before any non-lab use, and put
the GUI behind TLS/a reverse proxy rather than exposing it directly.
