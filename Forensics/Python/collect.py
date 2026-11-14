#!/usr/bin/env python3
"""
Config-driven forensic evidence collector with built-in integrity proof.

Reads a YAML profile describing which files to collect and which commands to
run, copies each artefact into an output directory, and for everything it
gathers records a SHA-256 hash in a manifest, appends a timestamped line to an
audit log, and writes a structured JSON report. Source files are only ever
read (never modified): their mtimes are preserved.

Usage:
    collect.py --config profile.yaml --output ./evidence
    collect.py --print-default-config > profile.yaml

Requirements:
    PyYAML; secscripts (pip install -e .).

Profile format (YAML):
    name: default
    files:                 # files to copy + hash (missing paths are logged)
      - /etc/hostname
    commands:              # commands to run; stdout is captured + hashed
      - name: processes
        argv: ["ps", "aux"]
"""

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import yaml  # noqa: E402

from secscripts.cli import EXIT_ERROR, EXIT_OK, build_parser  # noqa: E402
from secscripts.hashing import manifest_entry, sha256_bytes  # noqa: E402
from secscripts.log import configure  # noqa: E402

DEFAULT_CONFIG = {
    "name": "default",
    "files": ["/etc/hostname"],
    "commands": [{"name": "date", "argv": ["date", "-u"]}],
}


def _now():
    return datetime.now(tz=UTC).isoformat()


def _safe_dest(base: Path, source: Path) -> Path:
    """Map an absolute source path under ``base`` without escaping it."""
    parts = [p for p in source.parts if p not in ("/", "\\", "")]
    dest = base.joinpath(*parts)
    # Defence in depth: ensure the resolved dest stays within base.
    base_resolved = base.resolve()
    if not str(dest.resolve()).startswith(str(base_resolved)):
        raise ValueError(f"unsafe destination for {source}")
    return dest


class Collector:
    def __init__(self, output_dir: Path, logger):
        self.output_dir = output_dir
        self.logger = logger
        self.collected_dir = output_dir / "collected"
        self.manifest: list[dict] = []
        self.audit: list[str] = []
        self.errors: list[str] = []

    def _audit_line(self, action: str) -> None:
        line = f"{_now()} {action}"
        self.audit.append(line)
        self.logger.info(action)

    def collect_file(self, raw_path: str) -> None:
        source = Path(raw_path)
        if not source.is_file():
            msg = f"skip missing file: {raw_path}"
            self._audit_line(msg)
            self.errors.append(msg)
            return
        import shutil

        dest = _safe_dest(self.collected_dir, source)
        dest.parent.mkdir(parents=True, exist_ok=True)
        # copy2 reads the source and preserves its metadata; it does not modify
        # the source file.
        shutil.copy2(source, dest)
        entry = manifest_entry(source)
        entry["collected_copy"] = str(dest.relative_to(self.output_dir))
        entry["kind"] = "file"
        self.manifest.append(entry)
        self._audit_line(f"collected file {raw_path} sha256={entry['sha256']}")

    def collect_command(self, name: str, argv: list[str]) -> None:
        try:
            proc = subprocess.run(argv, capture_output=True, timeout=300, check=False)
        except (OSError, subprocess.SubprocessError) as exc:
            msg = f"command {name} failed to run: {exc}"
            self._audit_line(msg)
            self.errors.append(msg)
            return
        out_path = self.collected_dir / "commands" / f"{name}.out"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(proc.stdout)
        self.manifest.append(
            {
                "kind": "command",
                "name": name,
                "argv": argv,
                "returncode": proc.returncode,
                "size": len(proc.stdout),
                "sha256": sha256_bytes(proc.stdout),
                "collected_copy": str(out_path.relative_to(self.output_dir)),
            }
        )
        self._audit_line(f"ran command {name} rc={proc.returncode}")

    def run(self, config: dict) -> dict:
        started = _now()
        self.collected_dir.mkdir(parents=True, exist_ok=True)
        self._audit_line(f"collection started profile={config.get('name', 'unnamed')}")
        for raw_path in config.get("files", []) or []:
            self.collect_file(str(raw_path))
        for command in config.get("commands", []) or []:
            self.collect_command(command["name"], list(command["argv"]))
        finished = _now()
        self._audit_line("collection finished")

        report = {
            "profile": config.get("name", "unnamed"),
            "started": started,
            "finished": finished,
            "artefact_count": len(self.manifest),
            "error_count": len(self.errors),
            "errors": self.errors,
        }
        (self.output_dir / "manifest.json").write_text(
            json.dumps(self.manifest, indent=2, default=str), encoding="utf-8"
        )
        (self.output_dir / "audit.log").write_text("\n".join(self.audit) + "\n", encoding="utf-8")
        (self.output_dir / "report.json").write_text(
            json.dumps(report, indent=2, default=str), encoding="utf-8"
        )
        return report


def main(argv=None):
    parser = build_parser(
        "Config-driven forensic collector with SHA-256 integrity.",
        prog="collect",
    )
    parser.add_argument("-c", "--config", help="path to a YAML collection profile")
    parser.add_argument("-o", "--output", help="output directory for collected evidence")
    parser.add_argument(
        "--print-default-config",
        action="store_true",
        help="print a sample YAML profile and exit",
    )
    args = parser.parse_args(argv)
    logger = configure(args, name="collect")

    if args.print_default_config:
        print(yaml.safe_dump(DEFAULT_CONFIG, sort_keys=False).rstrip())
        return EXIT_OK

    if not args.output:
        logger.error("--output is required")
        return EXIT_ERROR

    if args.config:
        try:
            config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            logger.error("could not read config %s: %s", args.config, exc)
            return EXIT_ERROR
        if not isinstance(config, dict):
            logger.error("config must be a YAML mapping")
            return EXIT_ERROR
    else:
        logger.info("no --config given; using the built-in default profile")
        config = DEFAULT_CONFIG

    collector = Collector(Path(args.output), logger)
    report = collector.run(config)
    emit_format = args.output_format
    if emit_format == "json":
        print(json.dumps(report, indent=2, default=str))
    else:
        logger.info(
            "collected %d artefact(s), %d error(s) -> %s",
            report["artefact_count"],
            report["error_count"],
            args.output,
        )
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
