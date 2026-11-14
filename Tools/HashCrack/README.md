# HashCrack

Brute-force a password hash against a **wordlist**, a **mask**, or a
**rule-mutated wordlist**, in parallel across CPU cores, with a resumable
progress display.

## Install

```
pip install -e .     # from the repo root (installs secscripts + passlib)
```

## Usage

```
python Tools/HashCrack/hashcrack.py <hash> (-w WORDLIST | -m MASK) [options]
```

| Flag | Meaning |
|------|---------|
| `hash` | The hash to crack (positional). |
| `--type` | `md5 sha1 sha256 sha512 md5crypt sha256crypt sha512crypt bcrypt ntlm lm`. Omit to auto-detect. |
| `-w, --wordlist` | Wordlist file (one candidate per line). |
| `-m, --mask` | Hashcat-style mask, e.g. `?l?l?d?d`. |
| `--rules` | Rules file (wordlist mode only). |
| `--workers` | Worker processes (default: all CPUs). |
| `--resume` | Resume-state file; an interrupted run continues from it. |
| `-q/-v`, `--version`, `--output-format` | Shared `secscripts` flags. |

Exit codes: `0` password found, `1` not found or an error, `2` usage error.

## Hash types & auto-detection

`$2a$/$2b$/$2y$` → bcrypt, `$6$` → sha512crypt, `$5$` → sha256crypt,
`$1$` → md5crypt; bare hex by length → md5 (32), sha1 (40), sha256 (64),
sha512 (128). **NTLM and LM look identical to a 32-char md5**, so pass
`--type ntlm` / `--type lm` for those.

## Masks and rules

Masks: `?l` a–z, `?u` A–Z, `?d` 0–9, `?s` punctuation, `?a` all, `??` literal
`?`; other characters are literals. Rule ops (left to right per rule line):
`:` none, `l` lower, `u` upper, `c` capitalise, `t` toggle case, `r` reverse,
`d` duplicate, `$X` append X, `^X` prepend X.

## Examples

```
python Tools/HashCrack/hashcrack.py 5f4dcc3b5aa765d61d8327deb882cf99 -m '?l?l?l?l?l?l?l?l'
python Tools/HashCrack/hashcrack.py '$6$salt$...' -w rockyou.txt --workers 8
python Tools/HashCrack/hashcrack.py <ntlm> --type ntlm -w words.txt --rules best64.rule
# Resume a long run after Ctrl-C:
python Tools/HashCrack/hashcrack.py <hash> -w huge.txt --resume run.state
```

## Known limitations

- Resume granularity is one chunk (2000 candidates); a resumed run may retry up
  to the last un-checkpointed chunk.
- crypt schemes (bcrypt/sha*crypt) are intentionally slow by design, so they are
  far slower per-candidate than raw digests.
