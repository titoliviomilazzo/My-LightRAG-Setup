#!/usr/bin/env python3
"""
Validate corpus quality before indexing.

Fails when:
- Unicode replacement character exists (U+FFFD)
- Private Use Area characters remain
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

PUA_RE = re.compile(r"[\ue000-\uf8ff]")
TARGET_EXTENSIONS = {".txt", ".md", ".csv", ".json"}


def read_text_best_effort(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8", "utf-8-sig", "cp949", "euc-kr", "latin1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def iter_files(root: Path):
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in TARGET_EXTENSIONS:
            yield p


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--report-file", type=Path, default=Path("validation_report.json"))
    args = parser.parse_args()

    if not args.input_dir.exists():
        raise FileNotFoundError(f"Input dir does not exist: {args.input_dir}")

    issues: list[dict] = []
    scanned = 0
    for path in iter_files(args.input_dir):
        scanned += 1
        text = read_text_best_effort(path)
        repl_count = text.count("\ufffd")
        pua_count = len(PUA_RE.findall(text))
        if repl_count or pua_count:
            issues.append(
                {
                    "path": str(path),
                    "replacement_char_count": repl_count,
                    "pua_count": pua_count,
                }
            )

    report = {
        "input_dir": str(args.input_dir),
        "files_scanned": scanned,
        "issue_count": len(issues),
        "issues": issues,
    }
    args.report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in report if k != "issues"}, ensure_ascii=False, indent=2))

    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
