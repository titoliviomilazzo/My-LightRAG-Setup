#!/usr/bin/env python3
"""
Re-run 10-question quality evaluation against LightRAG query API.

- Reads questions from markdown table
- Calls /query with hybrid mode
- Repairs mojibake in response/reference text when possible
- Applies simple "standard" heuristic scoring
- Rewrites result table and summary in the same markdown
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.request
from pathlib import Path

QUESTION_ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|")
STOPWORDS = {
    "및",
    "과",
    "와",
    "의",
    "을",
    "를",
    "이",
    "가",
    "은",
    "는",
    "에서",
    "으로",
    "로",
    "대한",
    "정리",
    "설명",
    "여부",
    "적용",
    "결과",
    "방식",
    "기준",
    "비교",
    "후보",
    "최종",
}


def maybe_repair_mojibake(text: str) -> str:
    try:
        repaired = text.encode("latin1").decode("utf-8")
    except UnicodeError:
        return text
    # Keep repaired only when Hangul appears meaningfully.
    old_hangul = sum(1 for c in text if "\uac00" <= c <= "\ud7a3")
    new_hangul = sum(1 for c in repaired if "\uac00" <= c <= "\ud7a3")
    return repaired if new_hangul > old_hangul else text


def toks(s: str) -> list[str]:
    s = re.sub(r"[^0-9A-Za-z가-힣 ]+", " ", s)
    return [t for t in s.split() if len(t) >= 2 and t not in STOPWORDS]


def score_answer(question: str, answer: str, ref_count: int) -> tuple[int, int, int, int]:
    qtok = set(toks(question))
    atok = set(toks(answer))
    overlap = len(qtok & atok)
    rel_ratio = overlap / max(1, len(qtok))

    if ref_count >= 2:
        evidence = 3
    elif ref_count == 1:
        evidence = 2
    else:
        evidence = 0

    if rel_ratio >= 0.5:
        relevance = 2
    elif rel_ratio >= 0.2:
        relevance = 1
    else:
        relevance = 0

    halluc_free = 1
    if ("\ufffd" in answer) or ("수서중학교" in answer and "안동중앙고" in question):
        halluc_free = 0

    accuracy = 1
    if relevance == 2:
        accuracy = 3
    elif relevance == 1:
        accuracy = 2
    if len(answer) < 80:
        accuracy = max(0, accuracy - 1)
    if halluc_free == 0:
        accuracy = max(0, accuracy - 1)

    return accuracy, evidence, relevance, halluc_free


def extract_questions(md: str) -> list[tuple[int, str]]:
    rows = [line for line in md.splitlines() if QUESTION_ROW_RE.match(line)]
    out: list[tuple[int, str]] = []
    for row in rows:
        cols = [c.strip() for c in row.strip("|").split("|")]
        if len(cols) < 2 or not cols[0].isdigit():
            continue
        out.append((int(cols[0]), cols[1]))
    return sorted(out, key=lambda x: x[0])


def call_query(base_url: str, question: str, mode: str) -> dict:
    payload = json.dumps({"query": question, "mode": mode}).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}/query",
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quality-md", required=True, type=Path)
    parser.add_argument("--base-url", default="http://127.0.0.1:9700")
    parser.add_argument("--mode", default="hybrid")
    args = parser.parse_args()

    md = args.quality_md.read_text(encoding="utf-8")
    questions = extract_questions(md)
    if len(questions) != 10:
        raise RuntimeError(f"Expected 10 questions, got {len(questions)}")

    results = []
    for no, q in questions:
        resp = call_query(args.base_url.rstrip("/"), q, args.mode)
        answer = maybe_repair_mojibake((resp.get("response") or "").strip())
        refs = resp.get("references") or []
        ref_files = []
        for r in refs[:3]:
            fp = maybe_repair_mojibake(str(r.get("file_path") or "")).strip()
            if fp:
                ref_files.append(fp)
        accuracy, evidence, relevance, nofab = score_answer(q, answer, len(ref_files))
        total = accuracy + evidence + relevance + nofab
        pf = "P" if total >= 8 else "F"
        summary = answer.replace("\n", " ").strip()
        if len(summary) > 180:
            summary = summary[:180] + "..."
        results.append(
            {
                "no": no,
                "question": q,
                "summary": summary or "응답 없음",
                "refs": ", ".join(ref_files) if ref_files else "없음",
                "accuracy": accuracy,
                "evidence": evidence,
                "relevance": relevance,
                "nofab": nofab,
                "total": total,
                "pf": pf,
            }
        )

    total_score = sum(r["total"] for r in results)
    avg = total_score / len(results)
    p_count = sum(1 for r in results if r["pf"] == "P")
    f_count = len(results) - p_count
    ref_missing = sum(1 for r in results if r["refs"] == "없음")
    final = "PASS" if (avg >= 8.0 and p_count >= 8 and ref_missing <= 2) else "FAIL"

    # Rebuild markdown deterministically.
    out = []
    out.append("# LightRAG 품질 검증표 (10문항)")
    out.append("")
    out.append("검증 기준(문항당 10점)")
    out.append("- 정확성: 0~4")
    out.append("- 근거성(References 연계성): 0~3")
    out.append("- 질문 충족도: 0~2")
    out.append("- 환각 없음: 0~1")
    out.append("")
    out.append("합격 기준(권장)")
    out.append("- 문항 평균 8.0점 이상")
    out.append("- 환각 없음 항목 10문항 중 8개 이상")
    out.append("- References 누락 문항 2개 이하")
    out.append("")
    out.append("| No | 질문 | 응답 요약 | References(파일/근거) | 정확성(0~4) | 근거성(0~3) | 질문충족(0~2) | 환각없음(0~1) | 합계(10) | 판정(P/F) | 비고 |")
    out.append("|---|---|---|---|---:|---:|---:|---:|---:|---|---|")
    for r in results:
        out.append(
            f"| {r['no']} | {r['question']} | {r['summary']} | {r['refs']} | "
            f"{r['accuracy']} | {r['evidence']} | {r['relevance']} | {r['nofab']} | "
            f"{r['total']} | {r['pf']} | 자동채점(표준) |"
        )
    out.append("")
    out.append("## 집계")
    out.append(f"- 총점: {total_score}/100")
    out.append(f"- 평균점: {avg:.1f}/10")
    out.append(f"- P 문항 수: {p_count}")
    out.append(f"- F 문항 수: {f_count}")
    out.append(f"- References 누락 문항 수: {ref_missing}")
    out.append(f"- 최종 판정: {final}")
    out.append("")
    out.append("## 자동채점 결과")
    out.append("- 질의 모드: hybrid")
    out.append("- 인코딩 복구(가능한 경우): latin1->utf-8 휴리스틱 적용")
    out.append("- 권장: 정규화/검증 스크립트 실행 후 동일 문항 재평가")
    out.append("")

    args.quality_md.write_text("\n".join(out), encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "total_score": total_score,
                "average": round(avg, 1),
                "pass_items": p_count,
                "fail_items": f_count,
                "final": final,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
