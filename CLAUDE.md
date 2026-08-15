# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## About

A grab-bag of standalone cybersecurity IR/forensics/malware-research scripts and CLI tools, organized by discipline rather than by language or shared framework. There is no single application here — each script/tool under a category folder is independent and typically has its own `argparse` CLI. Don't assume changes in one tool affect another.

## Commands

```
pip install -r requirements.txt
python <path/to/script.py> [args]
```

There is one repo-wide `requirements.txt` (cryptography, docx, dpkt_fix, Faker, pandas, pipreqs, pynput, pytsk3, Requests, scapy, volatility) — no per-folder requirements files, no virtualenv convention enforced, and no test suite, linter, or CI beyond the issue/PR templates in `.github/`. Verify changes by running the affected script directly with `-h`/sample input rather than expecting automated checks.

To regenerate `requirements.txt` from actual imports: `python Automations/update_dependencies.py` (wraps `pipreqs --force`).

Bash forensic scripts (`Forensics/Bash/*.sh`) and PowerShell scripts (`Forensics/Powershell/*.ps1`) are meant to be run directly on the OS they target (Linux/macOS vs Windows) — read the script header before running since several (e.g. `evidence_collector.sh`, `collectEvidence.ps1`) expect to be run with elevated privileges on a live or mounted target system.

## Structure

- **Forensics/** — triage and evidence-collection tooling, split by execution environment:
  - `Bash/` — Linux/macOS live-response and triage scripts (evidence collectors, auditd setup, journal/cron/docker triage, disk carving).
  - `Powershell/` — Windows equivalents (evidence collection, timestamp collection, audit/logging setup, botnet checks).
  - `Python/` — cross-platform analysis scripts (EXIF, fast-flux domain detection, ext4 inode reading).
  - `Volatility Plugins/` — custom plugins for the Volatility memory-forensics framework (cmdline, VAD scan, path check, RAM scan, triage check). These are loaded into a Volatility installation, not run standalone.
  - `EvidenceGenerator/` — synthetic test-data generator (`generate_data.py`, `webgen.py`) for building fake evidence sets to practice against; see its README for the multi-step workflow (generate → filter fake access log with the documented `grep -Ev` private/reserved-IP exclusion pattern → rename).
  - `docker/` — self-contained Docker Compose environments: `Analysis_ELK/` spins up Elasticsearch/Kibana/Filebeat for rapid log ingestion during IR (expects logs in `/cases/logfiles`, UI on `localhost:8889`); `webtesting/` spins up a deliberately vulnerable PHP/MySQL app for attack practice.
- **Tools/** — standalone analyzers/crackers, each a small class + `argparse` CLI: `HashCrack` (crypt-hash brute force against a wordlist), `ZipCrack` (zip password brute force), `XLanalyser` (CSV/XLSX inspection), `TSS_Python`.
- **LogParse/** — log-parsing CLI. `CLIParse.py` is the entry point (`python LogParse/CLIParse.py <format> -p <path> [-o <output_dir>]`); `LogParser` auto-detects format (apache/iis/syslog/cef/yara) via regex against `log_patterns` and writes parsed output to `<format>_parsed_data.xlsx`. Only the `apache` format has a working parse method (`Apache()`) — other formats will fail at `getattr(self, log_format.capitalize())` until implemented.
- **Malware/** — intentionally offensive-style samples (`arpspoof.py`, `keylogger.py`, `ransomware.py`). Per the repo's README disclaimer, these exist to test security control boundaries and are for research/testing only — treat as defensive-research/educational code, not material to weaponize or make more evasive.
- **Automations/** — repo maintenance scripts (currently just `update_dependencies.py`).
- **specs/** — feature specs created via the `spec` skill (`~/.claude/skills/spec/`); each spec follows `specs/TEMPLATE.md` (Executive Summary / User Stories / Technical Requirements / Acceptance Criteria) and is paired with a `claude/feature/<slug>` branch. Implementation planning, checkpointed execution, and final review/merge are handled by the companion `spec-plan` / `spec-execute` / `spec-review` skills (also user-level, in `~/.claude/skills/`). `specs/plans/*.local.md` holds the approved implementation plan per feature — these are git-ignored and must never be committed. The legacy `.claude/commands/spec-v1.md` command is superseded by the `spec` skill and now just points to it.

## Working conventions

- Scripts here are one-file, dependency-light, and use stdlib `argparse` for CLIs — match that style rather than introducing new frameworks for a single script.
- Because folders map to independent tools with no shared imports (aside from the top-level `requirements.txt`), prefer self-contained fixes over cross-folder abstractions.
- Code style/lint conventions (headers, CLI parsing, error handling, per-language format/lint commands) are documented in `CONTRIBUTING.md` — follow it when adding or editing any script.
