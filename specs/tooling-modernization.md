# Feature Specification: Tooling Modernization

## 1. Executive Summary

- **User Problem**: The tools in Security-Scripts are inconsistent, under-featured and
  unverified. CLIs differ tool to tool (no common `--version`, output-format or logging
  flags), several advertised capabilities do not work (LogParse only parses `apache`; the
  other four formats raise at dispatch), the crackers are single-threaded with no resume or
  progress, collectors do not prove evidence integrity, there are no tests or CI, and most
  tools lack usage docs. The repo is used on real IR cases, for learning/labs, as a portfolio
  piece for employers, and increasingly by other analysts — all four audiences are blocked by
  the same gaps in reliability, consistency, performance and documentation.
- **Success Criteria**: Every in-scope tool exposes a consistent CLI, is covered by automated
  tests and green CI, is documented, and meets a measured performance bar; LogParse parses all
  five formats; the crackers gain resume/rule/mask/progress; collectors prove evidence
  integrity; the Docker stacks are hardened. The nine acceptance criteria in section 4 are the
  definition of done.

### Scope

**In scope**

- **LogParse** — `LogParse/` (`CLIParse.py`, `LogParse.py`, `LogAnalyse.py`).
- **Tools** — `Tools/HashCrack`, `Tools/ZipCrack`, `Tools/XLanalyser`, `Tools/TSS_Python`.
- **Forensics scripts** — `Forensics/Bash/*.sh`, `Forensics/Powershell/*.ps1`,
  `Forensics/Python/*`, `Forensics/Volatility Plugins/*`, `Forensics/EvidenceGenerator/*`.
- **Forensics docker stacks** — `Forensics/docker/Analysis_ELK/`, `Forensics/docker/webtesting/`,
  and any other compose stacks under `Forensics/docker/`.

**Out of scope (non-goals)**

- `Malware/` — left entirely untouched.
- No safety / authorised-use guardrails, notices or restrictions are added to any tool
  (explicit decision; the crackers remain plain utilities).
- No new network-targeting or offensive capabilities.
- Other repos in the workspace.

### Decisions

- **Breaking changes are allowed.** CLIs and output formats may be redesigned for consistency;
  existing flags/invocations do not have to keep working.
- Python stays stdlib-first and dependency-light, per the repo conventions; new runtime
  dependencies must be justified and pinned in the repo-wide `requirements.txt`.

## 2. User Stories

- **As an IR analyst on a live case**, I want collectors that hash every artefact and write a
  manifest and audit log without touching the source, so the evidence I gather is defensible.
- **As an analyst parsing logs**, I want LogParse to handle apache, iis, syslog, cef and yara
  with auto-detection and my choice of json/csv/xlsx output, so I am not limited to apache.
- **As someone running a crack against a large wordlist**, I want multiprocessing, resume,
  mask/rule modes and a live progress/ETA display, so long runs are fast and survivable.
- **As any user of any tool here**, I want the same core flags (`-h`, `--version`,
  `--output-format`, `--quiet/--verbose`) and sane exit codes, so I can script them uniformly.
- **As an employer or new contributor reading the repo**, I want tests, green CI and a README
  per tool, so I can trust the code and run it without reverse-engineering it.
- **As anyone deploying the Docker stacks**, I want pinned images, healthchecks and non-root
  containers, so a stack comes up reproducibly and does not run as root.

## 3. Technical Requirements

### 3.1 Cross-cutting (all in-scope Python tools)

- [ ] **Common CLI contract**: `-h/--help`, `--version`, `--output-format {json,csv,text}`,
      `--quiet` and `--verbose`, and documented exit codes (0 = success, non-zero = error).
      Implemented via a shared, self-contained helper consistent with the repo's `argparse`
      style — no heavy new CLI framework.
- [ ] **Structured output**: each tool can emit valid JSON and CSV in addition to its
      human-readable text form. Schemas documented per tool.
- [ ] **Logging**: `--quiet`/`--verbose` control a stdlib `logging`-based logger; errors go to
      stderr, data output to stdout (so JSON/CSV piping is clean).
- [ ] **Tests**: a `pytest` suite per Python tool covering the success path and at least one
      error/invalid-input path.
- [ ] **CI**: a GitHub Actions workflow running `ruff` (Python lint), `shellcheck` (Bash),
      `PSScriptAnalyzer` (PowerShell) and `pytest`, on push and PR.
- [ ] **Docs**: a README per in-scope tool (usage, examples, sample output, known limitations),
      authored with the `user-docs` skill where it fits.
- [ ] Any new runtime dependency is added to the repo-wide `requirements.txt`, pinned, and
      reflected by `Automations/update_dependencies.py`.

### 3.2 LogParse

- [ ] Working parsers for **apache, iis, syslog, cef, yara**, each turning a valid sample into
      the common record schema.
- [ ] Format **auto-detection** when the format is not given, with a clear error when detection
      is ambiguous.
- [ ] Output to **json, csv and xlsx** (xlsx preserved from today's behaviour).
- [ ] Streaming/line-oriented reading so a large log does not require loading the whole file
      into memory (supports the performance requirement in 3.6).

### 3.3 Tools (crackers and analysers)

- [ ] **HashCrack / ZipCrack**: multiprocessing across cores; **resume** from an interrupted
      run; **mask** and **rule** attack modes in addition to wordlist; live **progress bar with
      ETA**; broader hash-type coverage for HashCrack.
- [ ] **XLanalyser / TSS_Python**: brought up to the common CLI/output/logging/test/doc
      contract in 3.1 (no new attack features required).

### 3.4 Forensics scripts

- [ ] **Evidence integrity**: Python/Bash/PowerShell collectors compute **SHA-256** for every
      artefact collected, write a **manifest** (artefact path → hash, size, timestamps) and a
      **timestamped audit log** of actions, and never modify the source material.
- [ ] **Config-driven collection**: what gets collected is driven by a config file rather than
      hard-coded, with a sensible default profile.
- [ ] **Structured JSON reports** from collectors in addition to any human-readable output.
- [ ] Bash scripts pass `shellcheck`; PowerShell scripts pass `PSScriptAnalyzer`; Volatility
      plugins and EvidenceGenerator brought in line with the shared conventions where
      applicable.

### 3.5 Forensics docker stacks

- [ ] All images **pinned by digest** (no floating `latest`).
- [ ] **Healthchecks** on every long-running service.
- [ ] Containers run as a **non-root user** where the image permits.
- [ ] One **additional analysis stack** beyond the existing ELK and webtesting stacks.

### 3.6 Performance

- [ ] HashCrack, ZipCrack and LogParse are parallelised (multiprocessing) and/or streamed, and
      a **benchmark committed to the repo** demonstrates a **≥3× wall-clock speedup on a machine
      with 4 or more cores** versus the current single-threaded implementation, on a fixed
      reference input. The benchmark is runnable in CI or documented for local reproduction.

## 4. Acceptance Criteria

- [ ] **AC-1 — Tests + CI.** Every in-scope Python tool has a pytest suite; the GitHub Actions
      workflow runs ruff + shellcheck + PSScriptAnalyzer + pytest and passes.
      *Fail:* CI is red, or any in-scope tool ships without tests.
- [ ] **AC-2 — Consistent CLI.** Every in-scope tool supports `-h`, `--version`,
      `--output-format {json,csv,text}`, `--quiet/--verbose`, and returns 0 on success /
      non-zero on error. *Fail:* any tool is missing one of these or mis-uses exit codes.
- [ ] **AC-3 — Evidence integrity.** Running a collector produces a SHA-256 for every collected
      artefact, a manifest and a timestamped audit log, and leaves source mtimes/contents
      unchanged. *Fail:* a collected artefact has no hash, or any source file is modified.
- [ ] **AC-4 — Docs per tool.** Every in-scope tool has a README with usage, examples, sample
      output and known limitations. *Fail:* any in-scope tool is undocumented.
- [ ] **AC-5 — Performance.** The committed benchmark shows ≥3× speedup on 4+ cores for the
      parallelised tools versus the current single-threaded baseline. *Fail:* measured speedup
      is below 3×.
- [ ] **AC-6 — LogParse formats.** LogParse parses apache, iis, syslog, cef and yara with
      auto-detection and json/csv/xlsx output. *Fail:* any of the five formats errors on a valid
      sample input.
- [ ] **AC-7 — Crackers.** HashCrack and ZipCrack support resume, mask and rule modes, and show
      progress with ETA. *Fail:* resume does not continue an interrupted run, or mask mode is
      absent.
- [ ] **AC-8 — Collectors.** Forensic collection is config-driven and emits a valid structured
      JSON report. *Fail:* collection is not config-driven, or the report is not valid JSON.
- [ ] **AC-9 — Docker hardening.** Every compose stack uses digest-pinned images, defines
      healthchecks on long-running services, runs non-root where the image permits, and one new
      analysis stack is added. *Fail:* any unpinned `latest`, any long-running service without a
      healthcheck, or a container running as root where it need not.

## 5. Open Questions

| ID    | Question | Status |
|-------|----------|--------|
| OQ-01 | Which specific hash types must HashCrack add beyond its current set (e.g. bcrypt, sha256crypt, NTLM)? | open |
| OQ-02 | Rule-mode syntax: adopt a subset of an established format (e.g. hashcat rules) or define a minimal in-house rule language? | open |
| OQ-03 | What is the fixed reference input and target machine spec for the AC-5 benchmark baseline? | open |
| OQ-04 | Which additional Docker analysis stack to add (e.g. Zeek, Arkime, Velociraptor, a MISP instance)? | open |
| OQ-05 | Config file format for config-driven collection (YAML vs TOML vs JSON) and where profiles live. | open |
| OQ-06 | Do the Volatility plugins and EvidenceGenerator need the full CLI/output contract, or only lint + docs, given they are not standalone CLIs? | open |
