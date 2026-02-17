#!/usr/bin/env python3
"""
Run strict project-aware evaluation.

For each question and each detected project:
- query LightRAG with strict retrieval profile
- force project scope in the prompt
- verify whether references match the target project
- write a markdown report with explicit project attribution
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.parse
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


def extract_questions(md: str) -> list[tuple[int, str]]:
    rows = [line for line in md.splitlines() if QUESTION_ROW_RE.match(line)]
    out: list[tuple[int, str]] = []
    for row in rows:
        cols = [c.strip() for c in row.strip("|").split("|")]
        if len(cols) >= 2 and cols[0].isdigit():
            out.append((int(cols[0]), cols[1]))
    return sorted(out, key=lambda x: x[0])


def canonical_project_name(text: str) -> str:
    t = maybe_repair_mojibake(text)
    if "안동중앙고" in t:
        return "안동중앙고"
    if "수서중학교" in t or "수서중" in t:
        return "수서중학교"
    if "수암초" in t:
        return "수암초"
    if "경구고" in t:
        return "경구고"
    return Path(t).stem[:30]


def get_projects(base_url: str) -> list[str]:
    params = urllib.parse.urlencode({"offset": 0, "limit": 500})
    url = f"{base_url.rstrip('/')}/documents?{params}"
    raw = urllib.request.urlopen(url, timeout=30).read().decode("utf-8")
    data = json.loads(raw)
    processed = (data.get("statuses") or {}).get("processed") or []
    names = []
    for item in processed:
        fp = str(item.get("file_path") or "")
        names.append(canonical_project_name(fp))
    dedup = sorted(set(n for n in names if n))
    return dedup


def call_query(base_url: str, question: str, project: str, mode: str) -> dict:
    strict_query = (
        f"[대상 프로젝트: {project}] {question}\n"
        f"반드시 {project} 관련 근거만 사용하고 다른 프로젝트 정보는 제외하세요. "
        "답변 첫 줄에 '프로젝트: <이름>' 형식으로 명시하세요."
    )
    payload = {
        "query": strict_query,
        "mode": mode,
        "top_k": 30,
        "chunk_top_k": 12,
        "enable_rerank": True,
        "include_references": True,
        "include_chunk_content": True,
        "hl_keywords": [project],
        "ll_keywords": [project, "내진보강", "구조", "성능평가"],
        "response_type": "Bullet Points",
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/query",
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=240) as resp:
        return json.loads(resp.read().decode("utf-8"))


def summarize_answer(text: str, limit: int = 180) -> str:
    s = maybe_repair_mojibake(text).replace("\n", " ").strip()
    if len(s) > limit:
        s = s[:limit] + "..."
    return s or "응답 없음"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quality-md", required=True, type=Path)
    parser.add_argument("--output-md", default=Path("LightRAG 프로젝트별 엄격 질의 결과.md"), type=Path)
    parser.add_argument("--base-url", default="http://127.0.0.1:9700")
    parser.add_argument("--mode", default="local", choices=["local", "hybrid", "mix", "global", "naive", "bypass"])
    parser.add_argument("--min-target-hits", type=int, default=1)
    args = parser.parse_args()

    questions = extract_questions(args.quality_md.read_text(encoding="utf-8"))
    if len(questions) != 10:
        raise RuntimeError(f"Expected 10 questions, got {len(questions)}")

    projects = get_projects(args.base_url)
    if not projects:
        raise RuntimeError("No processed projects found from /documents endpoint.")

    rows = []
    strict_pass = 0
    total = 0

    for no, q in questions:
        for project in projects:
            total += 1
            resp = call_query(args.base_url, q, project, args.mode)
            answer = maybe_repair_mojibake(resp.get("response") or "")
            refs = resp.get("references") or []
            ref_projects = [canonical_project_name(str(r.get("file_path") or "")) for r in refs]
            ref_projects = [p for p in ref_projects if p]
            ref_counts: dict[str, int] = {}
            for p in ref_projects:
                ref_counts[p] = ref_counts.get(p, 0) + 1
            dominant = max(ref_counts, key=ref_counts.get) if ref_counts else "없음"
            target_hits = ref_counts.get(project, 0)
            foreign_hits = sum(v for k, v in ref_counts.items() if k != project)

            # strict criteria: dominant must match target and target evidence must exist
            is_pass = target_hits >= args.min_target_hits and dominant == project
            if is_pass:
                strict_pass += 1

            rows.append(
                {
                    "no": no,
                    "project": project,
                    "question": q,
                    "summary": summarize_answer(answer),
                    "target_hits": target_hits,
                    "foreign_hits": foreign_hits,
                    "dominant": dominant,
                    "refs": ", ".join(sorted(set(ref_projects))) if ref_projects else "없음",
                    "result": "P" if is_pass else "F",
                }
            )

    pass_rate = strict_pass / total if total else 0.0
    final = "PASS" if pass_rate >= 0.8 else "FAIL"

    out = []
    out.append("# LightRAG 프로젝트별 엄격 질의 결과")
    out.append("")
    out.append("엄격 기준")
    out.append("- 질의는 프로젝트명을 강제 포함하여 실행")
    out.append(f"- 참조문헌 기준 대상 프로젝트 hit >= {args.min_target_hits}")
    out.append("- 참조문헌 최다 프로젝트(dominant)가 대상 프로젝트와 일치해야 통과")
    out.append("- 외부 프로젝트 참조가 있어도 dominant가 대상이면 통과(제약: API 문서필터 부재)")
    out.append("")
    out.append(f"- 프로젝트 수: {len(projects)} ({', '.join(projects)})")
    out.append(f"- 총 평가 건수: {total} (10문항 x {len(projects)}프로젝트)")
    out.append(f"- 통과: {strict_pass}")
    out.append(f"- 실패: {total - strict_pass}")
    out.append(f"- 통과율: {pass_rate:.1%}")
    out.append(f"- 최종 판정: {final}")
    out.append("")
    out.append("| No | 대상 프로젝트 | 질문 | 응답 요약 | 대상참조수 | 외부참조수 | dominant 프로젝트 | 참조 프로젝트 목록 | 판정 |")
    out.append("|---:|---|---|---|---:|---:|---|---|---|")
    for r in rows:
        out.append(
            f"| {r['no']} | {r['project']} | {r['question']} | {r['summary']} | "
            f"{r['target_hits']} | {r['foreign_hits']} | {r['dominant']} | {r['refs']} | {r['result']} |"
        )
    out.append("")

    args.output_md.write_text("\n".join(out), encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "projects": projects,
                "total": total,
                "pass": strict_pass,
                "fail": total - strict_pass,
                "pass_rate": round(pass_rate, 4),
                "final": final,
                "mode": args.mode,
                "min_target_hits": args.min_target_hits,
                "output": str(args.output_md),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
