# Feature Specification: Repo-Wide Code Quality & Consistency

## 1. Executive Summary
- **User Problem**: SecurityScripts is a grab-bag of independent, standalone IR/forensics/malware-research tools written over time across multiple languages (Python, Bash, PowerShell) and categories (Forensics, Tools, LogParse, Malware, Automations). Because each script was authored independently with no shared conventions, the repo currently has inconsistent CLI argument patterns, inconsistent error handling (some scripts fail silently or use bare excepts), inconsistent logging/output (mixing `print` with ad-hoc formatting), inconsistent docstrings/headers, and no enforced style or lint standard. This makes tools slower and riskier to use during time-sensitive IR work, harder to review for correctness, and harder for new scripts to match existing conventions.
- **Success Criteria**: Every script in the repo follows a documented, consistent set of conventions for its language (argument parsing/help text, error handling and exit codes, logging/output style, and a standard header/docstring describing purpose, usage, and requirements). A repeatable check (lint/format command per language) exists and passes across the repo. No script's existing input/output behavior changes as a result of this work — this is a consistency and hygiene pass, not a functional rewrite. A short CONTRIBUTING-style convention doc exists so future scripts added to the repo start out consistent.

## 2. User Stories
- **As an** incident responder running these tools under time pressure, **I want to** see the same `-h`/`--help` structure, flag naming, and error-message style across every script **so that** I don't have to relearn each tool's quirks mid-investigation.
- **As a** repo maintainer, **I want to** consistent error handling (no bare `except:`, no silent failures, meaningful non-zero exit codes) across all scripts **so that** failures are visible and debuggable instead of masked.
- **As a** contributor adding a new script, **I want to** a documented style/convention guide and a lint/format command I can run **so that** my new tool matches the rest of the repo without guesswork.
- **As a** security-conscious reviewer, **I want to** every script audited for unsafe patterns (hardcoded secrets, unsafe `subprocess`/`shell=True` usage, unvalidated file paths) **so that** defensive-research tooling doesn't itself introduce vulnerabilities.
- **As a** user of the repo's Python tools, **I want to** a single accurate `requirements.txt` and consistent module/script structure **so that** `pip install -r requirements.txt` reliably gets me everything I need to run any script.

## 3. Technical Requirements
- [ ] Define and document per-language conventions (Python: argparse pattern, logging vs. print, docstring/header format, PEP 8 + formatter choice; Bash: header/usage function, `set -euo pipefail` where appropriate, shellcheck-clean; PowerShell: comment-based help, consistent parameter blocks)
- [ ] Add/agree on lint and format tooling for each language (e.g. a Python formatter/linter, `shellcheck` for Bash, PSScriptAnalyzer conventions for PowerShell) and document the exact command to run each, per existing repo convention of no enforced CI
- [ ] Audit every script under `Forensics/`, `Tools/`, `LogParse/`, `Malware/`, and `Automations/` against the documented conventions and bring each into compliance
- [ ] Standardize error handling and exit codes across all Python and Bash scripts (no bare excepts, no swallowed errors, consistent stderr usage)
- [ ] Standardize CLI help/usage text and flag naming across scripts that expose a CLI
- [ ] Verify `requirements.txt` stays accurate (via the existing `Automations/update_dependencies.py`) after any import changes
- [ ] Add a short repo-level conventions doc (e.g. `CONTRIBUTING.md` or a section in `CLAUDE.md`) capturing the agreed standards for future scripts
- [ ] Explicitly out of scope: changing any script's functional behavior, inputs, outputs, or adding new features — this pass is style/consistency/hygiene only

## 4. Acceptance Criteria
- [ ] Scenario 1: Running any Python script in the repo with `-h`/`--help` produces help text following the same structure (description, required/optional args grouped consistently, examples where applicable)
- [ ] Scenario 2: Running the documented lint/format command for each language (Python, Bash, PowerShell) against the full repo reports zero violations
- [ ] Scenario 3: Grepping the repo for `except:` (bare except) and common unsafe patterns (e.g. `shell=True` without justification, hardcoded credentials) returns no matches outside of documented, justified exceptions
- [ ] Scenario 4: A sample of previously-working scripts, run with the same inputs used before this change, produce identical output/behavior — confirming no functional regressions were introduced
- [ ] Scenario 5: A new contributor following only the new conventions doc can identify the correct argparse/logging/header pattern to use for a brand-new script without referencing other scripts for guesswork
