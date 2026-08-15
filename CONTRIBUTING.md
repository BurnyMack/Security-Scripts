# Contributing / Code Conventions

This repo is a grab-bag of independent, standalone IR/forensics/malware-research
scripts (see `CLAUDE.md`). There's no shared build or framework, so these
conventions exist to keep every script easy to pick up on its own, not to
introduce cross-folder abstractions. Match them when adding or editing any
script, regardless of folder.

Out of scope for these conventions: type hints, a `logging`-module rewrite of
CLI output, or any new framework/dependency. Scripts here are meant to stay
dependency-light, one-file, and readable without extra machinery.

## Python

- **Header**: every directly-run script starts with `#!/usr/bin/env python3`
  followed by a short module docstring: one line describing what it does, a
  `Usage:` line with a real example invocation, and a `Requirements:` line
  only if it needs a non-stdlib package. Library modules that are only ever
  imported (never run directly — e.g. `LogParse/LogParse.py`,
  `Tools/XLanalyser/XLanalyser.py`, Volatility plugins) skip the shebang but
  keep the docstring.
- **CLI parsing**: use `argparse` (not `getopt`, not raw `sys.argv` indexing)
  for every script that is meant to be run directly with arguments. Volatility
  plugins are the one exception — they take arguments through Volatility's own
  plugin/config API, not argparse.
- **Imports**: explicit imports only — no `from module import *`, even for
  libraries (like `scapy`) where wildcard imports are common elsewhere.
- **Errors**: never use a bare `except:`. Catch the specific exception(s) you
  expect, print a clear message to `sys.stderr`, and `sys.exit(1)` on
  unrecoverable failure. Don't let a script exit 0 after silently failing.
- **No hardcoded personal paths/secrets**: file paths, hosts, and credentials
  come from CLI arguments or environment variables, never a literal path from
  the original author's machine.
- **Format & lint**: [ruff](https://docs.astral.sh/ruff/) is the formatter and
  linter, configured in `pyproject.toml` at the repo root.
  ```
  python -m pip install ruff
  python -m ruff format .
  python -m ruff check .
  ```

## Bash (`Forensics/Bash/`, `Forensics/docker/**/*.sh`)

- **Header**: `#!/bin/bash`, then a comment block covering *Purpose*,
  *Requirements* (tools/privileges/OS it expects), and *Usage* (a real example
  invocation). Keep any existing warnings (e.g. "tailored to a specific
  environment") in the header too.
- **Strict mode is a per-script judgment call, not a blanket rule**:
  single-purpose scripts that do one linear operation (e.g. `fileshred.sh`,
  `ext4_inode_extractor.sh`) should start with `set -euo pipefail`. Multi-step
  *collector* scripts that are expected to keep gathering evidence even if one
  optional tool/artifact is missing (e.g. `evidence_collector.sh`,
  `macos_evidence.sh`) should **not** use `set -e`, since that would silently
  change their behavior (abort the whole collection run on the first missing
  tool). Those scripts should still use `set -uo pipefail` (catch unset vars
  and broken pipes) and check the exit status of individual steps explicitly
  where a failure should be logged rather than fatal.
- **Quoting**: always quote variable expansions (`"$var"`, `"$@"`).
- **Conditionals**: use `[[ ... ]]`, not `[ ... ]` — the repo already targets
  bash specifically (`#!/bin/bash`), not POSIX `sh`.
- **Lint**: [ShellCheck](https://www.shellcheck.net/) must run clean. Any
  intentionally-ignored warning needs an inline
  `# shellcheck disable=SCxxxx` with a one-line reason.
  ```
  shellcheck Forensics/Bash/*.sh Forensics/docker/**/*.sh
  ```

## PowerShell (`Forensics/Powershell/`)

- **Header**: a real
  [comment-based help](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_comment_based_help)
  block (`.SYNOPSIS`, `.DESCRIPTION`, `.PARAMETER`, `.EXAMPLE`) so
  `Get-Help ./script.ps1` works, instead of an informal "Purpose/Requirements"
  comment block.
- **Parameters**: expose script inputs through a `param()` block with typed
  parameters rather than hardcoded values or manual `$args` indexing.
- **Errors**: critical operations (evidence/file copies, anything where a
  silent failure would mean *lost evidence*) use `-ErrorAction Stop` with
  `try/catch` and a clear error message — don't let a collection step fail
  silently.
- **Lint**: [PSScriptAnalyzer](https://github.com/PowerShell/PSScriptAnalyzer)
  must run clean with the default rule set. Any intentionally-ignored rule
  needs a `[Diagnostics.CodeAnalysis.SuppressMessageAttribute(...)]` with a
  reason.
  ```
  Install-Module -Name PSScriptAnalyzer -Scope CurrentUser
  Invoke-ScriptAnalyzer -Path Forensics/Powershell -Recurse
  ```

## General

- No functional behavior changes disguised as "cleanup" — if a fix changes
  what a script actually does (not just how it's written), call it out
  explicitly rather than folding it into a consistency pass.
- `Malware/` scripts (`arpspoof.py`, `keylogger.py`, `ransomware.py`) follow
  the same style rules as any other Python script. Per the repo's README
  disclaimer they're defensive-research/educational code — consistency edits
  must not make them more evasive or capable than they already are.
- After changing Python imports/dependencies, regenerate `requirements.txt`
  with `python Automations/update_dependencies.py`.
