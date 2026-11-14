# Forensics / Bash

Linux/macOS live-response and triage scripts. **Read each script's header
before running** — several (e.g. `evidence_collector.sh`, `macos_evidence.sh`)
expect to run with root/elevated privileges on a live or mounted target, and
some are tailored to a specific environment.

Conventions (see repo `CONTRIBUTING.md`): `#!/bin/bash` header with Purpose /
Requirements / Usage, quoted expansions, `[[ ]]` tests, and **ShellCheck must
pass**. `macos_evidence.sh` has a zsh shebang (macOS) but a `# shellcheck
shell=bash` directive so it lints as bash.

## Notable scripts

| Script | Purpose |
|--------|---------|
| `evidence_collector.sh` | Linux live-response collector (system info, history, network, disk image) with a SHA-256 evidence manifest. |
| `macos_evidence.sh` | macOS equivalent collector. |
| `triage_template.sh`, `triageScan.sh` | Triage collection templates/scanners. |
| `VMDK_Carver.sh` | Carve/analyse partitions from a raw/VMDK image. |
| `setAuditD.sh`, `setAuditD_RHEL.sh` | Configure auditd baselines. |
| `journalTriage.sh`, `cron_collector.sh`, `docker_triage.sh` | Targeted artefact collectors. |
| `fileshred.sh`, `ext4_inode_extractor.sh` | Single-purpose utilities (use `set -euo pipefail`). |

## Running

```
shellcheck Forensics/Bash/*.sh        # lint (must be clean)
sudo ./Forensics/Bash/evidence_collector.sh /path/to/storage/device
```

## Evidence integrity

`evidence_collector.sh` writes `manifest.sha256` (SHA-256 of every collected
file) plus a hashed logfile, following RFC 3227 order-of-volatility guidance.

## Known limitations

- Multi-step collectors deliberately omit `set -e` so a single missing optional
  tool doesn't abort the whole run; they use `set -uo pipefail` and check
  critical steps explicitly.
- Scripts assume their documented target OS/tooling; read the header first.
