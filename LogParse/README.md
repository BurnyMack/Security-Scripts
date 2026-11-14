# LogParse

Parse a log file into structured records and output them as **json**, **csv**,
**text**, or **xlsx**. Supports Apache access logs, IIS (W3C-style), syslog,
CEF, and YARA rule files, plus pcap (via `dpkt`). When you don't name a format
it is auto-detected.

## Install

From the repo root:

```
pip install -e .          # installs the shared secscripts package
pip install pandas XlsxWriter   # only needed for --output-format xlsx
```

## Usage

```
python LogParse/CLIParse.py -p <path> [--format FMT] [--output-format FMT] [-o DIR]
```

| Flag | Meaning |
|------|---------|
| `-p, --path` | Log file to parse (required). |
| `--format` | `apache`, `iis`, `syslog`, `cef`, `pcap`, `yara`. Omit to auto-detect. |
| `--output-format` | `json` (default), `csv`, `text`, or `xlsx`. |
| `-o, --output` | Output directory. For json/csv/text, omit to print to stdout; xlsx always writes a file. |
| `-q/--quiet`, `-v/--verbose` | Logging verbosity (logs go to stderr). |
| `--version` | Print version and exit. |

Exit codes: `0` success, `1` a handled error (missing file, undetectable or
ambiguous format, parse/write failure), `2` argparse usage error.

## Examples

```
# Auto-detect and print JSON to stdout
python LogParse/CLIParse.py -p access.log

# Force apache, write CSV to stdout
python LogParse/CLIParse.py -p access.log --format apache --output-format csv

# Parse CEF to an xlsx file in ./out/
python LogParse/CLIParse.py -p events.cef --output-format xlsx -o out/
```

Sample files for every supported format live in `LogParse/TestFiles/`.

### Sample output

`python LogParse/CLIParse.py -p LogParse/TestFiles/apache.log` →

```json
[
  {
    "IP": "192.168.1.1",
    "timestamp": "10/Oct/2023:12:34:56 +0000",
    "URL": "GET /index.html",
    "Status Code": "200",
    "Bytes Sent": "1234"
  },
  ...
]
```

## Auto-detection

Detection counts how many of the first 200 lines match each line-oriented
format (apache/iis/syslog/cef) and does a whole-file check for YARA. It raises
a clear error when nothing matches (`could not auto-detect log format`) or when
two formats tie (`ambiguous log format; candidates: ...`). Pass `--format` to
skip detection.

## Known limitations

- **YARA and pcap are read whole**, not streamed line by line, so very large
  files of those two types load into memory; apache/iis/syslog/cef are read
  line by line.
- **pcap** needs `dpkt` (`dpkt_fix` in `requirements.txt`) and is not part of
  auto-detection — pass `--format pcap` explicitly.
- The **IIS** parser targets a space-separated W3C-style line
  (`date time c-ip method uri status bytes "user-agent"`); IIS logs with a
  different selected field set need the regex in `LogParse.py` adjusted.
- `LogParse.py` and `LogAnalyse.py` are importable library modules;
  `CLIParse.py` is the entry point.
