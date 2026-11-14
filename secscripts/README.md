# secscripts

The one shared helper package for the Security-Scripts tools (see the repo
`CONTRIBUTING.md`). It gives every directly-run Python tool the same CLI
contract so each tool doesn't re-implement the boilerplate. Stdlib-only.

Install once from the repo root:

```
pip install -e .
```

## Modules

| Module | Provides |
|--------|----------|
| `secscripts.cli` | `build_parser()` / `add_common_args()` — the shared flags `--version`, `--output-format {json,csv,text}` (extendable via `output_formats`), `-q/--quiet`, `-v/--verbose`, and the exit-code constants `EXIT_OK`/`EXIT_ERROR`. |
| `secscripts.output` | `emit()` / `render()` — turn a `list[dict]` of records into json, csv, or text on stdout. |
| `secscripts.log` | `configure()` — a stderr logger wired to the verbosity flags (data on stdout, logs on stderr). |
| `secscripts.hashing` | `sha256_file()`, `sha256_bytes()`, `manifest_entry()`, `build_manifest()` — streaming SHA-256 and evidence-manifest helpers. |
| `secscripts.progress` | `Progress` — a TTY-aware progress bar with ETA (silent when not a TTY). |
| `secscripts.candidates` | `from_wordlist()`, `from_mask()`, `apply_rules()`, `load_rules()` — password-candidate generators (wordlist, hashcat-style mask, rule subset) shared by the crackers. |
| `secscripts.crack` | `search()` — parallel candidate search (multiprocessing `imap`) with ordered first-match, progress, and resumable check-pointing. |

## Exit-code convention

`0` success · `1` a handled runtime/usage error reported to stderr · `2`
argparse usage error.

## Tests

```
pytest secscripts/tests
```
