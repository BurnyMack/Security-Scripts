# Forensics / Volatility Plugins

Custom plugins for the [Volatility 2](https://github.com/volatilityfoundation/volatility)
memory-forensics framework. They are **loaded into a Volatility install, not
run standalone**, and because Volatility 2 is a Python-2-era framework they are
not importable under this repo's Python 3.11+ environment.

## Plugins

| Plugin | Purpose |
|--------|---------|
| `ramscan.py` | Faster MALFIND-style scan: process name/PID/PPID/command line; VADs with RWX flagged suspicious. |
| `Fastvadscan.py` | Fast VAD scan. |
| `cmdcheck.py` | Command-execution check. |
| `pathcheck.py` | Flag processes running from unusual/suspicious locations (e.g. TEMP). |
| `triagecheck.py` | Highlight low-hanging-fruit signs of malicious activity (uses pslist; evadable). |

## Using

Point Volatility at this directory with `--plugins` and invoke a plugin by name:

```
vol.py --plugins="Forensics/Volatility Plugins" -f memory.img --profile=<Profile> ramscan
```

## Testing

The `tests/` suite checks the plugins **statically** (valid Python syntax,
each defines a plugin class, each has header documentation) via `ast`, since the
Volatility 2 framework can't be imported under Python 3:

```
pytest "Forensics/Volatility Plugins/tests"
```

## Known limitations

- Volatility 2 / Python 2 framework plugins; verify behaviour inside a real
  Volatility 2 installation against a known memory image.
- `triagecheck.py` checks for obvious indicators only — a clean result does not
  prove the system is untampered.
