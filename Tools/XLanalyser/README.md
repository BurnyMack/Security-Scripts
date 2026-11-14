# XLanalyser

Summarise a CSV or XLSX file: per-column `describe()` statistics (count, mean,
std, min, quartiles, max) plus a null count per column.

## Install

```
pip install -e .                 # from the repo root (installs secscripts)
pip install pandas openpyxl XlsxWriter   # pandas + xlsx read/write engines
```

## Usage

```
python Tools/XLanalyser/XLanalyser.py <input.csv|input.xlsx> [options]
```

| Flag | Meaning |
|------|---------|
| `input_file` | A `.csv` or `.xlsx` file (positional). |
| `--output-format` | `text` (default), `json`, `csv`, or `xlsx`. |
| `-o, --output` | Output file for `--output-format xlsx` (default `summary.xlsx`). |
| `-q/-v`, `--version` | Shared `secscripts` flags. |

Exit codes: `0` success, `1` unreadable/unsupported input or missing engine,
`2` usage error.

## Examples

```
python Tools/XLanalyser/XLanalyser.py data.csv
python Tools/XLanalyser/XLanalyser.py data.xlsx --output-format json
python Tools/XLanalyser/XLanalyser.py data.csv --output-format xlsx -o report.xlsx
```

### Sample output (json)

```json
[
  {"column": "a", "count": 3.0, "mean": 2.0, "std": 1.0, "min": 1.0,
   "25%": 1.5, "50%": 2.0, "75%": 2.5, "max": 3.0, "null_count": 0},
  {"column": "b", "count": 2.0, "mean": 20.0, "null_count": 1}
]
```

## Known limitations

- `describe()` covers numeric columns; purely non-numeric columns contribute a
  null count but limited statistics.
- `.xlsx` input needs `openpyxl`; `.xlsx` output needs `XlsxWriter`.
