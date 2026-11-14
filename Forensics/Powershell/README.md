# Forensics / PowerShell

Windows live-response, collection, and logging-configuration scripts. Each has
a comment-based help block, so `Get-Help ./script.ps1 -Full` describes its
parameters and examples. Several change system state or collect evidence and
must be run elevated — read the help first.

Conventions (see repo `CONTRIBUTING.md`): comment-based help
(`.SYNOPSIS`/`.DESCRIPTION`/`.PARAMETER`/`.EXAMPLE`), typed `param()` blocks,
`-ErrorAction Stop` + `try/catch` for evidence-critical operations, and
**PSScriptAnalyzer must pass** (default rules; the CI `powershell` job runs it).

## Scripts

| Script | Purpose |
|--------|---------|
| `collectEvidence.ps1` | Memory capture (Magnet RAM Capture) + KAPE `!SANS_Triage`, with per-file MD5 and a SHA-256 `manifest.sha256.csv` over the evidence set. |
| `FolderCheck.ps1` | Report Name/Creation/Modified timestamps for subfolders to CSV. |
| `collect_timestamps.ps1` | Report file Creation/Access/Write times for a folder. |
| `botnetcheck.ps1` | Hunt current network connections for known malicious IPs. |
| `setAuditing.ps1` | Establish a baseline Windows audit policy. |
| `set_logging.ps1` | (Deprecated — use `setAuditing.ps1`) enlarge event logs and enable audit subcategories. |

## Running

```powershell
Install-Module -Name PSScriptAnalyzer -Scope CurrentUser
Invoke-ScriptAnalyzer -Path Forensics/Powershell -Recurse   # must be clean
Get-Help .\Forensics\Powershell\collectEvidence.ps1 -Full
```

## Known limitations

- `collectEvidence.ps1` expects `MRC.exe` and a `Kape\` directory alongside it
  and writes to `.\Evidence\<COMPUTERNAME>\`.
- State-changing scripts (`setAuditing.ps1`, `set_logging.ps1`) require an
  elevated session.
