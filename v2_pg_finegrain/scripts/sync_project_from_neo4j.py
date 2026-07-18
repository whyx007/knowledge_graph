#!/usr/bin/env python3
"""Export the running v2 Neo4j graph back into project staging files.

Neo4j is treated as the source of truth for this one-way reconciliation. The
export keeps the established staging columns and appends audit columns that
exist on manually maintained relationships in the database.
"""

from __future__ import annotations

import argparse
import csv
import shutil
from collections import Counter
from datetime import date, datetime
from pathlib import Path

from neo4j import Driver, GraphDatabase


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_URI = "bolt://127.0.0.1:7688"
DEFAULT_USER = "neo4j"
DEFAULT_PASSWORD = "neo4j2026"

ENTERPRISE_FIELDS = [
    "enterprise_id",
    "enterprise_name",
    "source_system",
    "source_pk",
    "last_sync_at",
]
MOUNT_FIELDS = [
    "enterprise_id",
    "substage_id",
    "confidence",
    "evidence",
    "source_field",
    "source_system",
    "needs_review",
    "source",
    "source_pk",
    "updated_at",
]
SUMMARY_PATH = ROOT / "docs" / "当前Neo4j企业挂载环节与依据汇总.md"


def scalar(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


def natural_key(value: str) -> tuple[int, str]:
    suffix = value.rsplit("_", 1)[-1]
    return (int(suffix), value) if suffix.isdigit() else (10**9, value)


def fetch(driver: Driver) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    enterprise_query = """
    MATCH (e:Enterprise)
    RETURN e.enterprise_id AS enterprise_id,
           e.enterprise_name AS enterprise_name,
           e.source_system AS source_system,
           e.source_pk AS source_pk,
           e.last_sync_at AS last_sync_at
    """
    mount_query = """
    MATCH (e:Enterprise)-[r:LOCATED_IN_SUBSTAGE]->(s:ChainSubstage)
    RETURN e.enterprise_id AS enterprise_id,
           s.substage_id AS substage_id,
           r.confidence AS confidence,
           r.evidence AS evidence,
           r.source_field AS source_field,
           r.source_system AS source_system,
           r.needs_review AS needs_review,
           r.source AS source,
           r.source_pk AS source_pk,
           r.updated_at AS updated_at
    """
    with driver.session() as session:
        enterprises = [
            {field: scalar(record[field]) for field in ENTERPRISE_FIELDS}
            for record in session.run(enterprise_query)
        ]
        mounts = [
            {field: scalar(record[field]) for field in MOUNT_FIELDS}
            for record in session.run(mount_query)
        ]
    enterprises.sort(key=lambda row: natural_key(row["enterprise_id"]))
    mounts.sort(key=lambda row: (natural_key(row["enterprise_id"]), row["substage_id"]))
    return enterprises, mounts


def fetch_summary_rows(driver: Driver) -> list[dict[str, str]]:
    query = """
    MATCH (e:Enterprise)-[r:LOCATED_IN_SUBSTAGE]->(ss:ChainSubstage)
    OPTIONAL MATCH (ss)<-[:HAS_SUBSTAGE]-(st:ChainStage)
    OPTIONAL MATCH (st)<-[:HAS_STAGE]-(seg:ChainSegment)
    OPTIONAL MATCH (seg)<-[:HAS_SEGMENT]-(c:IndustryChain)
    RETURN e.enterprise_id AS enterprise_id,
           e.enterprise_name AS enterprise_name,
           c.chain_name AS chain_name,
           seg.segment_name AS segment_name,
           st.stage_name AS stage_name,
           ss.substage_id AS substage_id,
           ss.substage_name AS substage_name,
           r.confidence AS confidence,
           r.needs_review AS needs_review,
           r.source_field AS source_field,
           r.source_system AS source_system,
           r.source AS source,
           r.evidence AS evidence
    """
    with driver.session() as session:
        rows = [{key: scalar(record[key]) for key in record.keys()} for record in session.run(query)]
    rows.sort(key=lambda row: (row["chain_name"], natural_key(row["enterprise_id"]), row["substage_id"]))
    return rows


def md_cell(value: str, limit: int = 220) -> str:
    value = value.replace("\n", " ").replace("\r", " ").replace("|", "\\|")
    if len(value) > limit:
        value = value[: limit - 1] + "…"
    return value or "-"


def write_summary(path: Path, rows: list[dict[str, str]], enterprise_count: int) -> None:
    pending = sum(row["needs_review"].lower() == "true" for row in rows)
    confirmed = len(rows) - pending
    chain_counts = Counter(row["chain_name"] for row in rows)
    chain_enterprises = {
        chain: len({row["enterprise_id"] for row in rows if row["chain_name"] == chain})
        for chain in chain_counts
    }
    confidence_counts = Counter(row["confidence"] or "-" for row in rows)
    lines = [
        "# 当前 Neo4j 企业挂载环节与依据汇总",
        "",
        "> 数据来源：v2 Neo4j 当前图谱 `neo4j-kg-v2-finegrain`。",
        "> 本文件由 `scripts/sync_project_from_neo4j.py` 从运行中的数据库生成。",
        "",
        "## 汇总",
        "",
        f"- Enterprise 节点数：{enterprise_count}",
        f"- 已挂载企业数：{len({row['enterprise_id'] for row in rows})}",
        f"- 企业-二级环节挂载关系数：{len(rows)}",
        f"- 待复核关系：{pending}",
        f"- 已确认关系：{confirmed}",
        "",
        "### 按产业链统计",
        "",
        "| 产业链 | 企业数 | 挂载关系数 |",
        "|---|---:|---:|",
    ]
    for chain in sorted(chain_counts):
        lines.append(f"| {md_cell(chain)} | {chain_enterprises[chain]} | {chain_counts[chain]} |")
    lines += ["", "### 按置信度统计", "", "| 置信度 | 挂载关系数 |", "|---|---:|"]
    for confidence, count in sorted(confidence_counts.items()):
        lines.append(f"| {md_cell(confidence)} | {count} |")
    lines += [
        "",
        "## 明细",
        "",
        "| 企业ID | 企业名称 | 产业链 | 分段 | 一级环节 | 二级环节ID | 二级环节 | 置信度 | 待复核 | 来源字段 | 来源系统 | 依据 |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        source_system = row["source_system"] or row["source"]
        lines.append(
            "| "
            + " | ".join(
                md_cell(row[field])
                for field in (
                    "enterprise_id",
                    "enterprise_name",
                    "chain_name",
                    "segment_name",
                    "stage_name",
                    "substage_id",
                    "substage_name",
                    "confidence",
                    "needs_review",
                    "source_field",
                )
            )
            + f" | {md_cell(source_system)} | {md_cell(row['evidence'])} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uri", default=DEFAULT_URI)
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    parser.add_argument("--no-import-copy", action="store_true")
    args = parser.parse_args()

    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))
    try:
        enterprises, mounts = fetch(driver)
        summary_rows = fetch_summary_rows(driver)
    finally:
        driver.close()

    enterprise_path = ROOT / "data" / "staging" / "enterprises.csv"
    mount_path = ROOT / "data" / "staging" / "enterprise_to_substage.csv"
    write_csv(enterprise_path, ENTERPRISE_FIELDS, enterprises)
    write_csv(mount_path, MOUNT_FIELDS, mounts)

    if not args.no_import_copy:
        import_dir = ROOT / "neo4j" / "import"
        shutil.copy2(enterprise_path, import_dir / enterprise_path.name)
        shutil.copy2(mount_path, import_dir / mount_path.name)

    write_summary(SUMMARY_PATH, summary_rows, len(enterprises))

    print(f"Exported {len(enterprises)} Enterprise nodes")
    print(f"Exported {len(mounts)} LOCATED_IN_SUBSTAGE relationships")


if __name__ == "__main__":
    main()
