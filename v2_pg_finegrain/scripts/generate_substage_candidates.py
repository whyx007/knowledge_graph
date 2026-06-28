#!/usr/bin/env python3
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUBSTAGES = ROOT / "data/mappings/chain_substages.csv"
EVIDENCE = ROOT / "data/staging/enterprise_evidence.csv"
OUTPUT = ROOT / "data/staging/enterprise_to_substage.csv"


def normalize(text: str) -> str:
    return (text or "").lower()


def split_keywords(raw: str) -> list[str]:
    items = []
    for item in (raw or "").split("|"):
        kw = item.strip()
        if not kw:
            continue
        if kw.isascii() and len(kw) < 3:
            continue
        items.append(kw)
    return items


def keyword_matches(text: str, text_norm: str, keyword: str) -> bool:
    # Acronyms such as ROS, CPO, WDM must match as standalone tokens.
    # Otherwise substrings like "Rosa" can create false positives for "ROS".
    if keyword.isascii():
        pattern = rf"(?<![A-Za-z0-9]){re.escape(keyword)}(?![A-Za-z0-9])"
        flags = 0 if keyword.isupper() else re.IGNORECASE
        return re.search(pattern, text, flags) is not None
    return normalize(keyword) in text_norm


def excerpt(text: str, keyword: str, size: int = 160) -> str:
    compact = re.sub(r"\s+", " ", text or "").strip()
    pos = normalize(compact).find(normalize(keyword))
    if pos < 0:
        return compact[:size]
    start = max(0, pos - size // 2)
    end = min(len(compact), pos + len(keyword) + size // 2)
    return compact[start:end]


def main() -> None:
    substages = []
    with SUBSTAGES.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            keywords = split_keywords(row.get("keywords", ""))
            if keywords:
                substages.append(
                    {
                        "substage_id": row["substage_id"],
                        "substage_name": row["substage_name"],
                        "keywords": keywords,
                    }
                )

    candidates = []
    seen = set()
    with EVIDENCE.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            text = row.get("evidence_text", "") or ""
            text_norm = normalize(text)
            for substage in substages:
                matched = [kw for kw in substage["keywords"] if keyword_matches(text, text_norm, kw)]
                if not matched:
                    continue
                key = (row["enterprise_id"], substage["substage_id"])
                if key in seen:
                    continue
                seen.add(key)
                confidence = "medium" if len(matched) >= 2 else "low"
                candidates.append(
                    {
                        "enterprise_id": row["enterprise_id"],
                        "substage_id": substage["substage_id"],
                        "confidence": confidence,
                        "evidence": excerpt(text, matched[0]),
                        "source_field": row.get("source_field", ""),
                        "source_system": row.get("source_system", "postgresql"),
                        "needs_review": "true",
                    }
                )

    candidates.sort(key=lambda r: (r["enterprise_id"], r["substage_id"]))
    with OUTPUT.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "enterprise_id",
            "substage_id",
            "confidence",
            "evidence",
            "source_field",
            "source_system",
            "needs_review",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(candidates)

    print(f"Wrote {len(candidates)} candidate enterprise-to-substage mappings.")


if __name__ == "__main__":
    main()
