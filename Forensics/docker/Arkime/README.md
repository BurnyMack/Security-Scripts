# Arkime stack

Runs [Arkime](https://arkime.com/) (full-packet-capture indexing and search)
with an OpenSearch backend for its session index.

## Usage

```
docker compose -f Forensics/docker/Arkime/docker-compose.yml up -d
```

First-run setup (once OpenSearch is healthy) typically requires initialising
the Arkime database and creating an admin user inside the container:

```
docker exec -it arkime /opt/arkime/db/db.pl http://opensearch:9200 init
docker exec -it arkime /opt/arkime/bin/arkime_add_user.sh admin "Admin" <password> --admin
```

Then browse the viewer at <http://localhost:8005>.

## Hardening

- **Digest-pinned** images (Arkime and its OpenSearch backend).
- **Healthchecks** on both services; Arkime waits for OpenSearch to be healthy.
- OpenSearch demo security is disabled for a local lab — do not expose it.

## Caveats

Validated with `docker compose config`, not run end-to-end here. The exact
`ARKIME_*` environment keys and the DB-init/user-creation commands depend on the
image version — check the image's documentation. Capturing live traffic needs
additional interface/capability configuration not enabled here.
