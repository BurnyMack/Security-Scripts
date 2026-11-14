# Forensics / Python

Cross-platform Python forensics and collection tools. All share the common
`secscripts` CLI contract: `-h`, `--version`, `--output-format {json,csv,text}`,
`-q/--quiet`, `-v/--verbose`, and the exit-code convention (`0` ok, `1` handled
error, `2` usage). Install with `pip install -e .` from the repo root.

| Tool | Purpose |
|------|---------|
| `collect.py` | Config-driven (YAML) evidence collector: copies files, runs commands, SHA-256-hashes every artefact into a manifest, writes a timestamped audit log + JSON report, never modifies sources. |
| `exifcheck.py` | Extract core-property metadata from a `.docx` file (needs python-docx). |
| `fastfluxfinder.py` | Flag domains in a pcap resolving to many unique IPs — possible fast-flux DNS (needs scapy). |
| `inode_reader.py` | Read an inode's data block from an ext4 image and report its SHA-256 (needs pytsk3). |

## Examples

```
# Collection with integrity (see the profile format with --print-default-config)
python Forensics/Python/collect.py --print-default-config > profile.yaml
python Forensics/Python/collect.py -c profile.yaml -o ./evidence --output-format json

python Forensics/Python/exifcheck.py -i report.docx --output-format json
python Forensics/Python/fastfluxfinder.py capture.pcap --threshold 5
python Forensics/Python/inode_reader.py disk.img 12345 --hex
```

### Collector output

`collect.py` writes into the output directory: `collected/` (copied artefacts
and captured command output), `manifest.json` (per-artefact path/size/SHA-256/
timestamps), `audit.log` (timestamped actions), and `report.json` (summary with
counts and any errors).

## Known limitations

- `scapy` and `pytsk3` are heavy, optional deps imported lazily; the tools load
  (and `--version`/`--help` work) without them, but the analysis needs them.
- `collect.py` collects files and command output; it does not image disks or
  memory — use the Bash/PowerShell collectors or dedicated imagers for that.
- YARA/pcap-style whole-file inputs are read into memory.
