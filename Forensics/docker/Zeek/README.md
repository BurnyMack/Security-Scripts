# Zeek analysis stack

Runs [Zeek](https://zeek.org/) as a long-running live network-traffic analyser,
writing JSON logs to `./logs`. Complements the ELK/OpenSearch log stacks (point
Filebeat at `./logs`).

## Usage

```
# Choose the interface to monitor (default eth0):
ZEEK_IFACE=en0 docker compose -f Forensics/docker/Zeek/docker-compose.yml up -d
tail -f Forensics/docker/Zeek/logs/conn.log
```

To analyse a capture file instead of a live interface, run a one-shot container:

```
docker run --rm -v "$PWD/pcaps:/pcaps" -v "$PWD/logs:/logs" -w /logs \
  zeek/zeek:6.0 zeek -r /pcaps/capture.pcap LogAscii::use_json=T
```

## Hardening

- **Digest-pinned** image (`zeek/zeek:6.0@sha256:…`).
- **Healthcheck**: the service is healthy while the `zeek` capture process runs.
- **Capabilities**: all dropped except `NET_RAW`/`NET_ADMIN`, which live capture
  requires. `network_mode: host` is needed to see host interfaces.

## Caveats

Validated with `docker compose config`, not run end-to-end here. Live capture
requires host networking and the raw-socket capabilities above; set
`ZEEK_IFACE` to a real interface on your host.
