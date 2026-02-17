#!/usr/bin/env python3
"""
Build isolated per-project indexes (one document at a time) and run strict evaluation.

Workflow:
1) Backup source PDFs from C:\\LightRAG\\inputs\\__enqueued__
2) For each project PDF:
   - clear current index via /documents DELETE
   - upload only that PDF
   - wait until processing finishes
   - run 10 evaluation questions
   - record results (project-isolated, no cross-project contamination)
3) Optionally restore the full 4-project index
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import time
import urllib.request
from pathlib import Path

QUESTION_ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|")


def maybe_repair_mojibake(text: str) -> str:
    try:
        repaired = text.encode("latin1").decode("utf-8")
    except UnicodeError:
        return text
    old_hangul = sum(1 for c in text if "\uac00" <= c <= "\ud7a3")
    new_hangul = sum(1 for c in repaired if "\uac00" <= c <= "\ud7a3")
    return repaired if new_hangul > old_hangul else text


def project_name_from_filename(name: str) -> str:
    t = maybe_repair_mojibake(name)
    if "안동중앙고" in t:
        return "안동중앙고"
    if "수서중학교" in t or "수서중" in t:
        return "수서중학교"
    if "수암초" in t:
        return "수암초"
    if "경구고" in t:
        return "경구고"
    return Path(t).stem


def api_json(base_url: str, method: str, path: str, payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}{path}",
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method=method,
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        raw = resp.read().decode("utf-8")
    if not raw.strip():
        return {}
    return json.loads(raw)


def upload_pdf(base_url: str, file_path: Path) -> dict:
    boundary = "----LightRAGBoundary7MA4YWxkTrZu0gW"
    data = file_path.read_bytes()
    header = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"\r\n'
        "Content-Type: application/pdf\r\n\r\n"
    ).encode("utf-8")
    tail = f"\r\n--{boundary}--\r\n".encode("utf-8")
    body = header + data + tail
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/documents/upload",
        data=body,
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read().decode("utf-8"))


def wait_pipeline_idle(base_url: str, timeout_sec: int = 3600) -> None:
    start = time.time()
    while True:
        st = api_json(base_url, "GET", "/documents/pipeline_status")
        busy = bool(st.get("busy", False))
        if not busy:
            return
        if time.time() - start > timeout_sec:
            raise TimeoutError("Pipeline did not become idle in time.")
        time.sleep(5)


def wait_doc_processed(base_url: str, expected_processed: int, timeout_sec: int = 14400) -> None:
    start = time.time()
    while True:
        counts = api_json(base_url, "GET", "/documents/status_counts").get("status_counts", {})
        processed = int(counts.get("PROCESSED", counts.get("processed", 0)))
        failed = int(counts.get("FAILED", counts.get("failed", 0)))
        processing = int(counts.get("PROCESSING", counts.get("processing", 0)))
        pending = int(counts.get("PENDING", counts.get("pending", 0)))
        if processed >= expected_processed and failed == 0 and processing == 0 and pending == 0:
            return
        if time.time() - start > timeout_sec:
            raise TimeoutError(f"Document processing timeout. counts={counts}")
        time.sleep(8)


def extract_questions(path: Path) -> list[tuple[int, str]]:
    text = path.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines() if QUESTION_ROW_RE.match(line)]
    out: list[tuple[int, str]] = []
    for row in rows:
        cols = [c.strip() for c in row.strip("|").split("|")]
        if len(cols) >= 2 and cols[0].isdigit():
            out.append((int(cols[0]), cols[1]))
    return sorted(out, key=lambda x: x[0])


def call_query(base_url: str, question: str, project: str) -> dict:
    payload = {
        "query": f"[대상 프로젝트: {project}] {question}",
        "mode": "local",
        "top_k": 20,
        "chunk_top_k": 10,
        "enable_rerank": True,
        "include_references": True,
        "include_chunk_content": True,
        "hl_keywords": [project],
        "ll_keywords": [project, "내진보강", "구조", "성능평가"],
        "response_type": "Bullet Points",
    }
    return api_json(base_url, "POST", "/query", payload)


def summarize_answer(answer: str) -> str:
    s = maybe_repair_mojibake(answer).replace("\n", " ").strip()
    return s if len(s) <= 180 else s[:180] + "..."


def backup_source_pdfs(src_dir: Path, backup_dir: Path) -> list[Path]:
    backup_dir.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(src_dir.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"No PDF files found in {src_dir}")
    out = []
    for p in pdfs:
        dst = backup_dir / p.name
        if not dst.exists() or dst.stat().st_size != p.stat().st_size:
            shutil.copy2(p, dst)
        out.append(dst)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quality-md", required=True, type=Path)
    parser.add_argument("--output-md", default=Path("LightRAG 프로젝트별 분리인덱스 엄격 결과.md"), type=Path)
    parser.add_argument("--base-url", default="http://127.0.0.1:9700")
    parser.add_argument("--source-dir", default=Path(r"C:\LightRAG\inputs\__enqueued__"), type=Path)
    parser.add_argument("--backup-dir", default=Path(r"C:\LightRAG\inputs\_split_index_backup"), type=Path)
    parser.add_argument("--restore-full-index", action="store_true")
    args = parser.parse_args()

    questions = extract_questions(args.quality_md)
    if len(questions) != 10:
        raise RuntimeError(f"Expected 10 questions, got {len(questions)}")

    pdfs = backup_source_pdfs(args.source_dir, args.backup_dir)
    projects = [(project_name_from_filename(p.name), p) for p in pdfs]

    results = []
    for project, pdf in projects:
        wait_pipeline_idle(args.base_url, timeout_sec=1200)
        api_json(args.base_url, "DELETE", "/documents")
        wait_pipeline_idle(args.base_url, timeout_sec=1200)

        upload_pdf(args.base_url, pdf)
        wait_doc_processed(args.base_url, expected_processed=1, timeout_sec=14400)

        for no, q in questions:
            resp = call_query(args.base_url, q, project)
            answer = maybe_repair_mojibake(resp.get("response") or "")
            refs = resp.get("references") or []
            ref_names = [project_name_from_filename(str(r.get("file_path") or "")) for r in refs]
            target_hits = sum(1 for n in ref_names if n == project)
            foreign_hits = sum(1 for n in ref_names if n != project)
            ok = target_hits >= 1 and foreign_hits == 0
            results.append(
                {
                    "no": no,
                    "project": project,
                    "question": q,
                    "summary": summarize_answer(answer),
                    "target_hits": target_hits,
                    "foreign_hits": foreign_hits,
                    "refs": ", ".join(sorted(set(ref_names))) if ref_names else "없음",
                    "result": "P" if ok else "F",
                }
            )

    if args.restore_full_index:
        wait_pipeline_idle(args.base_url, timeout_sec=1200)
        api_json(args.base_url, "DELETE", "/documents")
        wait_pipeline_idle(args.base_url, timeout_sec=1200)
        for _, pdf in projects:
            upload_pdf(args.base_url, pdf)
        wait_doc_processed(args.base_url, expected_processed=len(projects), timeout_sec=14400)

    total = len(results)
    passed = sum(1 for r in results if r["result"] == "P")
    failed = total - passed
    pass_rate = passed / total if total else 0
    final = "PASS" if pass_rate >= 0.8 else "FAIL"

    out = []
    out.append("# LightRAG 프로젝트별 분리인덱스 엄격 결과")
    out.append("")
    out.append("기준")
    out.append("- 프로젝트별 단독 인덱스(해당 PDF 1개만 적재)로 질의")
    out.append("- 대상 프로젝트 참조 >= 1")
    out.append("- 외부 프로젝트 참조 = 0")
    out.append("")
    out.append(f"- 총 평가 건수: {total}")
    out.append(f"- 통과: {passed}")
    out.append(f"- 실패: {failed}")
    out.append(f"- 통과율: {pass_rate:.1%}")
    out.append(f"- 최종 판정: {final}")
    out.append("")
    out.append("| No | 대상 프로젝트 | 질문 | 응답 요약 | 대상참조수 | 외부참조수 | 참조 프로젝트 목록 | 판정 |")
    out.append("|---:|---|---|---|---:|---:|---|---|")
    for r in results:
        out.append(
            f"| {r['no']} | {r['project']} | {r['question']} | {r['summary']} | "
            f"{r['target_hits']} | {r['foreign_hits']} | {r['refs']} | {r['result']} |"
        )
    out.append("")

    args.output_md.write_text("\n".join(out), encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "projects": [p for p, _ in projects],
                "total": total,
                "pass": passed,
                "fail": failed,
                "pass_rate": round(pass_rate, 4),
                "final": final,
                "output": str(args.output_md),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
