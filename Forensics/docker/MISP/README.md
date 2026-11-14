# MISP stack

Runs a [MISP](https://www.misp-project.org/) threat-intelligence platform:
`misp-core` (web app) + `misp-modules` (enrichment) + MariaDB + Valkey (Redis).

## Usage

```
MYSQL_PASSWORD='strong-db-pw' MYSQL_ROOT_PASSWORD='strong-root-pw' \
MISP_BASE_URL='https://localhost:8443' \
  docker compose -f Forensics/docker/MISP/docker-compose.yml up -d
# Web UI: https://localhost:8443  (first boot takes a few minutes; self-signed TLS)
# Default MISP login after init: admin@admin.test / admin — change it immediately.
```

## Hardening

- **Digest-pinned** images for all four services (no floating tags).
- **Healthchecks** on every service; `misp-core` waits for the DB and Redis to
  be healthy (`start_period` allows for MISP's slow first boot).
- MariaDB and Valkey run as **non-root** by default. Credentials come from env
  vars — **set strong passwords**; the defaults are placeholders.

## Caveats

Validated with `docker compose config`, not run end-to-end here. The official
`misp-docker` project occasionally changes env-var names between releases — if a
service fails to start, check its documentation for the current variables. Put
the UI behind proper TLS and change all default credentials before any real use.
