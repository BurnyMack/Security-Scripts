# ZipCrack

Brute-force a password-protected ZIP against a **wordlist**, a **mask**, or a
**rule-mutated wordlist**, in parallel across CPU cores, with a resumable
progress display. Shares the candidate/engine layer with HashCrack.

## Install

```
pip install -e .     # from the repo root (installs secscripts)
```

## Usage

```
python Tools/ZipCrack/zipcrack.py <archive.zip> (-w WORDLIST | -m MASK) [options]
```

| Flag | Meaning |
|------|---------|
| `zipfile` | The password-protected archive (positional). |
| `-w, --wordlist` | Wordlist file. |
| `-m, --mask` | Hashcat-style mask (see HashCrack README for tokens). |
| `--rules` | Rules file (wordlist mode only). |
| `--workers` | Worker processes (default: all CPUs). |
| `--resume` | Resume-state file. |
| `-q/-v`, `--version`, `--output-format` | Shared `secscripts` flags. |

Exit codes: `0` password found, `1` not found / unreadable / unencrypted zip,
`2` usage error.

## Examples

```
python Tools/ZipCrack/zipcrack.py secret.zip -w rockyou.txt --workers 8
python Tools/ZipCrack/zipcrack.py secret.zip -m '?d?d?d?d'
```

## How it works

A candidate is tested by reading the archive's first encrypted entry with it;
the ZIP CRC check rejects wrong passwords (raising `RuntimeError`/
`BadZipFile`, which are caught). Each worker opens its own handle.

## Known limitations

- Supports the classic ZipCrypto scheme that Python's `zipfile` can read.
  AES-encrypted ZIPs (WinZip AES) are not supported by the stdlib and will not
  crack here.
- With traditional ZipCrypto, a wrong password can occasionally pass the CRC
  check; verify a "found" password by extracting.
