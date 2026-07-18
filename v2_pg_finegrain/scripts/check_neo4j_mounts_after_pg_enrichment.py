#!/usr/bin/env python3
"""Check Neo4j enterprise mounts against enriched PostgreSQL company fields."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import psycopg2
from neo4j import GraphDatabase
from psycopg2.extras import RealDictCursor


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "docs" / "twopaper_v2_Neo4j挂载调整检查报告.md"
SUBSTAGES_PATH = ROOT / "data" / "mappings" / "chain_substages.csv"
STAGES_PATH = ROOT / "data" / "mappings" / "chain_stages.csv"
CHAINS_PATH = ROOT / "data" / "mappings" / "chain_master.csv"

PG_DSN = "postgresql://postgres:postgres@127.0.0.1:5432/ceo_brief"
NEO4J_URI = "bolt://127.0.0.1:7688"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4j2026"

STRONG_FIELDS = ("core_tech", "products")
WEAK_FIELDS: tuple[str, ...] = ()
ALL_FIELDS = STRONG_FIELDS + WEAK_FIELDS

GENERIC_KEYWORDS = {
    "设备",
    "系统",
    "平台",
    "材料",
    "产品",
    "服务",
    "装备",
    "技术",
    "工艺",
    "软件",
    "硬件",
    "算法",
    "检测",
    "测量",
    "制造",
    "研发",
    "设计",
    "应用",
    "解决方案",
    "核心装备",
    "核心技术",
    "传感器",
    "芯片",
    "激光",
    "光学",
    "视觉",
    "机器人",
    "通信",
    "导航",
    "定位",
    "封装",
    "模组",
}

DROP_EVIDENCE_RE = re.compile(
    r"(融资|投资|估值|订单|客户|市场|销售|营收|收入|回款|团队|创始|应用领域|应用场景|目标市场|"
    r"深度参与|前沿方向|需求方|主要面向|广泛应用|下游|相似)"
)


@dataclass
class Substage:
    substage_id: str
    substage_name: str
    stage_id: str
    stage_name: str
    chain_id: str
    chain_name: str
    keywords: list[str]


def clean(value: object) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def norm(value: str) -> str:
    return re.sub(r"[\s，,。；;：:、（）()·.｜|/\\-]+", "", clean(value)).lower()


def split_keywords(raw: str) -> list[str]:
    out = []
    for item in (raw or "").split("|"):
        keyword = clean(item)
        if not keyword:
            continue
        if keyword.isascii() and len(keyword) < 3:
            continue
        out.append(keyword)
    return out


def specific_keyword(keyword: str) -> bool:
    keyword = clean(keyword)
    if not keyword or keyword in GENERIC_KEYWORDS:
        return False
    if keyword.isascii():
        return len(keyword) >= 3
    return len(keyword) >= 3


def keyword_matches(text: str, keyword: str) -> bool:
    if not text or not keyword:
        return False
    if keyword.isascii():
        flags = 0 if keyword.isupper() else re.IGNORECASE
        return re.search(rf"(?<![A-Za-z0-9]){re.escape(keyword)}(?![A-Za-z0-9])", text, flags) is not None
    return norm(keyword) in norm(text)


def excerpt(text: str, keywords: list[str], limit: int = 170) -> str:
    compact = clean(text)
    if not compact:
        return ""
    positions = [norm(compact).find(norm(k)) for k in keywords if norm(k) in norm(compact)]
    positions = [p for p in positions if p >= 0]
    if not positions:
        return compact[:limit]
    pos = min(positions)
    start = max(0, pos - limit // 2)
    return compact[start : start + limit]


def md_cell(value: object, limit: int = 180) -> str:
    text = clean(value)
    if len(text) > limit:
        text = text[: limit - 1] + "…"
    return text.replace("|", "\\|")


def load_substages() -> dict[str, Substage]:
    chains = {}
    with CHAINS_PATH.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            chains[row["chain_id"]] = row["chain_name"]

    stages = {}
    with STAGES_PATH.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            stages[row["stage_id"]] = {
                "stage_name": row["stage_name"],
                "chain_id": row["chain_id"],
                "chain_name": chains.get(row["chain_id"], row["chain_id"]),
            }

    substages: dict[str, Substage] = {}
    with SUBSTAGES_PATH.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            stage = stages[row["stage_id"]]
            keywords = split_keywords(row.get("keywords", ""))
            substages[row["substage_id"]] = Substage(
                substage_id=row["substage_id"],
                substage_name=row["substage_name"],
                stage_id=row["stage_id"],
                stage_name=stage["stage_name"],
                chain_id=stage["chain_id"],
                chain_name=stage["chain_name"],
                keywords=keywords,
            )
    return substages


def load_pg_companies() -> list[dict]:
    with psycopg2.connect(PG_DSN) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, name, domain, core_tech, products, industry, scenario, cert_ip, company_profile
                FROM companies
                ORDER BY id
                """
            )
            return list(cur.fetchall())


def load_neo4j_mounts() -> list[dict]:
    query = """
    MATCH (e:Enterprise)-[r:LOCATED_IN_SUBSTAGE]->(ss:ChainSubstage)
    OPTIONAL MATCH (ss)<-[:HAS_SUBSTAGE]-(st:ChainStage)
    OPTIONAL MATCH (st)<-[:HAS_STAGE]-(:ChainSegment)<-[:HAS_SEGMENT]-(c:IndustryChain)
    RETURN e.enterprise_id AS enterprise_id,
           e.enterprise_name AS enterprise_name,
           toInteger(e.source_pk) AS pg_id,
           ss.substage_id AS substage_id,
           ss.substage_name AS substage_name,
           st.stage_name AS stage_name,
           c.chain_name AS chain_name,
           r.confidence AS confidence,
           r.source_field AS source_field,
           r.evidence AS evidence,
           r.needs_review AS needs_review
    ORDER BY enterprise_id, substage_id
    """
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    try:
        with driver.session() as session:
            return [dict(record) for record in session.run(query)]
    finally:
        driver.close()


def score_company_substage(company: dict, substage: Substage) -> dict:
    strong_score = 0
    weak_score = 0
    matched: dict[str, list[str]] = {field: [] for field in ALL_FIELDS}

    candidates = [substage.substage_name] + [kw for kw in substage.keywords if specific_keyword(kw)]
    for field in ALL_FIELDS:
        text = clean(company.get(field))
        if not text:
            continue
        for keyword in candidates:
            if keyword_matches(text, keyword):
                matched[field].append(keyword)
                if field in STRONG_FIELDS:
                    strong_score += 4 if keyword == substage.substage_name else 3
                else:
                    weak_score += 2 if keyword == substage.substage_name else 1

    matched = {field: sorted(set(values)) for field, values in matched.items() if values}
    strong_fields = [field for field in STRONG_FIELDS if matched.get(field)]
    weak_fields = [field for field in WEAK_FIELDS if matched.get(field)]
    best_field = (strong_fields or weak_fields or [""])[0]
    return {
        "strong_score": strong_score,
        "weak_score": weak_score,
        "matched": matched,
        "strong_fields": strong_fields,
        "weak_fields": weak_fields,
        "evidence": excerpt(clean(company.get(best_field)), [kw for values in matched.values() for kw in values]),
    }


def strong_text(company: dict) -> str:
    return " ".join(clean(company.get(field)) for field in STRONG_FIELDS)


def chain_context_ok(company: dict, substage: Substage, score: dict) -> bool:
    text = strong_text(company)
    evidence = score.get("evidence", "")
    if DROP_EVIDENCE_RE.search(evidence):
        # Allow explicit product/equipment names, but block application-direction snippets.
        if not re.search(r"(核心产品|主营产品|产品为|产品包括|核心技术|自主研发|研发与制造|生产和研发|检测设备|激光器设计与制造)", evidence):
            return False
    if "_DOWN_" in substage.stage_id:
        return False
    if substage.chain_id == "CHAIN_SPACE_001":
        return bool(re.search(r"(卫星|航天|火箭|星载|星地|测运控|遥感|运载|航天器|推进|姿轨控)", text))
    if substage.chain_id == "CHAIN_OC_001":
        return bool(re.search(r"(光通信|光模块|光互连|光互联|CPO|NPO|AOC|PON|硅光|光芯片|光器件|光电)", text, re.I))
    if substage.chain_id == "CHAIN_ROBOT_001":
        return bool(re.search(r"(机器人本体|机械臂|AMR|AGV|巡检机器人|服务机器人|协作机器人|具身智能|机器人核心零部件)", text, re.I))
    if substage.chain_id == "CHAIN_LA_001":
        if substage.substage_id == "SUB_LA_001" and not re.search(r"(光纤激光器.*(?:设计|制造|产品)|(?:工业|单模|高功率|万瓦级).*光纤激光器)", text):
            return False
        return bool(re.search(r"(激光|光纤激光器|超快|飞秒|皮秒|切割|焊接|清洗|打标|微加工)", text))
    if substage.chain_id == "CHAIN_MV_001":
        return bool(re.search(r"(视觉|相机|成像|AOI|检测|测量|高光谱|三维|3D)", text, re.I))
    if substage.chain_id == "CHAIN_DISPLAY_001":
        return bool(re.search(r"(显示|LED|OLED|Micro LED|Micro-LED|mLED|AMOLED|FMM|掩模版|发光)", text, re.I))
    if substage.chain_id == "CHAIN_COMP_001":
        return bool(re.search(r"(光计算|光子计算|光芯片|光互连|CPO|AI算力|大模型|推理|训练)", text, re.I))
    if substage.chain_id == "CHAIN_FUSION_001":
        return bool(re.search(r"(量子|光谱|精密测量|光学相干|弱光|单光子|冷原子)", text))
    return True


def make_candidates(companies: list[dict], substages: dict[str, Substage], current_pairs: set[tuple[int, str]]) -> list[dict]:
    candidates = []
    for company in companies:
        for substage in substages.values():
            pair = (company["id"], substage.substage_id)
            if pair in current_pairs:
                continue
            score = score_company_substage(company, substage)
            if score["strong_score"] < 4:
                continue
            if not chain_context_ok(company, substage, score):
                continue
            # Avoid pure application/customer language even if it contains a product-like keyword.
            if DROP_EVIDENCE_RE.search(score["evidence"]) and not score["strong_fields"]:
                continue
            candidates.append(
                {
                    "pg_id": company["id"],
                    "company": company["name"],
                    "substage_id": substage.substage_id,
                    "substage": substage.substage_name,
                    "stage": substage.stage_name,
                    "chain": substage.chain_name,
                    "score": score["strong_score"],
                    "fields": ",".join(score["strong_fields"]),
                    "keywords": "、".join(sorted({kw for f in score["strong_fields"] for kw in score["matched"].get(f, [])})),
                    "evidence": score["evidence"],
                }
            )
    candidates.sort(key=lambda r: (-r["score"], r["chain"], r["company"], r["substage_id"]))
    return candidates


def make_review_items(companies_by_id: dict[int, dict], substages: dict[str, Substage], mounts: list[dict]) -> list[dict]:
    items = []
    for rel in mounts:
        pg_id = rel.get("pg_id")
        company = companies_by_id.get(pg_id)
        substage = substages.get(rel["substage_id"])
        if not company or not substage:
            continue
        score = score_company_substage(company, substage)
        source_field = clean(rel.get("source_field"))
        evidence = clean(rel.get("evidence"))
        no_strong_now = score["strong_score"] == 0
        if no_strong_now:
            reason = []
            if not score["matched"]:
                reason.append("core_tech/products 未命中该细分环节关键词")
            else:
                reason.append("core_tech/products 缺少足够强证据")
            if source_field and not re.search(r"(core_tech|products|homepage_official)", source_field):
                reason.append("现有关系来源不是核心技术/产品")
            items.append(
                {
                    "pg_id": pg_id,
                    "company": company["name"],
                    "substage_id": substage.substage_id,
                    "substage": substage.substage_name,
                    "stage": substage.stage_name,
                    "chain": substage.chain_name,
                    "confidence": rel.get("confidence"),
                    "source_field": source_field,
                    "reason": "；".join(reason),
                    "evidence": evidence,
                }
            )
    items.sort(key=lambda r: (r["chain"], r["company"], r["substage_id"]))
    return items


def write_report(companies: list[dict], mounts: list[dict], additions: list[dict], reviews: list[dict]) -> None:
    lines = [
        "# twopaper_v2 更新后 Neo4j 挂载调整检查报告",
        "",
        f"- 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "- PostgreSQL：`ceo_brief.public.companies`",
        "- Neo4j：`bolt://127.0.0.1:7688` / 容器 `neo4j-kg-v2-finegrain`",
        f"- PostgreSQL 企业数：{len(companies)}",
        f"- Neo4j 当前挂载关系：{len(mounts)}",
        f"- 建议新增挂载候选：{len(additions)}",
        f"- 建议复核/可能移除候选：{len(reviews)}",
        "",
        "## 检查口径",
        "",
        "- 新增候选只按 `core_tech`、`products` 的强匹配生成。",
        "- 不使用 `industry`、`scenario`、`company_profile`、`cert_ip` 作为挂载校验依据。",
        "- 对已有 Neo4j 关系，若更新后的 `core_tech/products` 缺少该二级环节证据，则列入复核/可能移除。",
        "- 本报告只做检查和建议，未直接修改 Neo4j。",
        "",
        "## 建议新增挂载候选",
        "",
        "| PG id | 企业 | 建议链 | 一级环节 | 二级环节 | 命中字段 | 关键词 | 依据摘要 |",
        "|---:|---|---|---|---|---|---|---|",
    ]
    for row in additions:
        lines.append(
            f"| {row['pg_id']} | {md_cell(row['company'], 60)} | {md_cell(row['chain'], 40)} | "
            f"{md_cell(row['stage'], 40)} | `{row['substage_id']}` {md_cell(row['substage'], 50)} | "
            f"{row['fields']} | {md_cell(row['keywords'], 80)} | {md_cell(row['evidence'], 220)} |"
        )

    lines.extend(
        [
            "",
            "## 建议复核/可能移除候选",
            "",
            "| PG id | 企业 | 当前链 | 一级环节 | 当前二级环节 | 置信度 | 原来源字段 | 原因 | 现有依据摘要 |",
            "|---:|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in reviews:
        lines.append(
            f"| {row['pg_id']} | {md_cell(row['company'], 60)} | {md_cell(row['chain'], 40)} | "
            f"{md_cell(row['stage'], 40)} | `{row['substage_id']}` {md_cell(row['substage'], 50)} | "
            f"{md_cell(row['confidence'], 20)} | {md_cell(row['source_field'], 40)} | {md_cell(row['reason'], 100)} | "
            f"{md_cell(row['evidence'], 220)} |"
        )

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    substages = load_substages()
    companies = load_pg_companies()
    mounts = load_neo4j_mounts()
    companies_by_id = {company["id"]: company for company in companies}
    current_pairs = {(mount["pg_id"], mount["substage_id"]) for mount in mounts if mount.get("pg_id") is not None}
    additions = make_candidates(companies, substages, current_pairs)
    reviews = make_review_items(companies_by_id, substages, mounts)
    write_report(companies, mounts, additions, reviews)
    print(f"companies={len(companies)}")
    print(f"neo4j_mounts={len(mounts)}")
    print(f"add_candidates={len(additions)}")
    print(f"review_candidates={len(reviews)}")
    print(f"report={REPORT_PATH}")


if __name__ == "__main__":
    main()
