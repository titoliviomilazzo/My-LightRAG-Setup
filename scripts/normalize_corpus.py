#!/usr/bin/env python3
"""
Normalize extracted text before LightRAG indexing.

What it does:
- optional mojibake repair (latin1 -> utf-8 heuristic)
- Unicode NFKC normalization
- zero-width character removal
- PUA replacement using config/pua_replacements.json
- writes a JSON report for traceability
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

ZERO_WIDTH_RE = re.compile(r"[\u200b-\u200f\ufeff]")
PUA_RE = re.compile(r"[\ue000-\uf8ff]")
TARGET_EXTENSIONS = {".txt", ".md", ".csv", ".json"}


@dataclass
class FileStats:
    path: str
    changed: bool
    repaired_mojibake: bool
    pua_before: int
    pua_after: int
    replacement_char_count: int


def load_map(path: Path) -> Dict[str, str]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Replacement map must be a JSON object.")
    return {str(k): str(v) for k, v in data.items()}


def read_text_best_effort(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8", "utf-8-sig", "cp949", "euc-kr", "latin1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def hangul_count(text: str) -> int:
    return sum(1 for ch in text if "\uac00" <= ch <= "\ud7a3")


def maybe_repair_mojibake(text: str) -> tuple[str, bool]:
    # Typical case: utf-8 bytes decoded as latin1/cp1252.
    try:
        repaired = text.encode("latin1").decode("utf-8")
    except UnicodeError:
        return text, False
    if hangul_count(repaired) > hangul_count(text):
        return repaired, True
    return text, False


def normalize_text(text: str, replacements: Dict[str, str]) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = ZERO_WIDTH_RE.sub("", text)
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def iter_files(root: Path):
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in TARGET_EXTENSIONS:
            yield p


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument(
        "--map-file",
        type=Path,
        default=Path("config/pua_replacements.json"),
    )
    parser.add_argument("--write", action="store_true", help="Write normalized text in-place.")
    parser.add_argument(
        "--report-file",
        type=Path,
        default=Path("normalization_report.json"),
    )
    args = parser.parse_args()

    if not args.input_dir.exists():
        raise FileNotFoundError(f"Input dir does not exist: {args.input_dir}")

    replacements = load_map(args.map_file)
    stats: list[FileStats] = []

    for path in iter_files(args.input_dir):
        original = read_text_best_effort(path)
        repaired, repaired_flag = maybe_repair_mojibake(original)
        pua_before = len(PUA_RE.findall(repaired))
        normalized = normalize_text(repaired, replacements)
        pua_after = len(PUA_RE.findall(normalized))
        changed = normalized != original
        repl_char_count = normalized.count("\ufffd")

        if args.write and changed:
            path.write_text(normalized, encoding="utf-8", newline="\n")

        stats.append(
            FileStats(
                path=str(path),
                changed=changed,
                repaired_mojibake=repaired_flag,
                pua_before=pua_before,
                pua_after=pua_after,
                replacement_char_count=repl_char_count,
            )
        )

    report = {
        "input_dir": str(args.input_dir),
        "files_scanned": len(stats),
        "files_changed": sum(1 for s in stats if s.changed),
        "mojibake_repaired_files": sum(1 for s in stats if s.repaired_mojibake),
        "files_with_replacement_char": sum(1 for s in stats if s.replacement_char_count > 0),
        "files_with_pua_after": sum(1 for s in stats if s.pua_after > 0),
        "details": [s.__dict__ for s in stats],
    }
    args.report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({k: report[k] for k in report if k != "details"}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
