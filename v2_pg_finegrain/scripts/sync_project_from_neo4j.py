#!/usr/bin/env python3
"""Export the running v2 Neo4j graph back into project staging files.

Neo4j is treated as the source of truth for this one-way reconciliation. The
export keeps the established staging columns and appends audit columns that
exist on manually maintained relationships in the database.
"""

from __future__ import annotations

import argparse
import csv
import re
import shutil
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

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
    "is_invested",
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
    "status",
    "audit_status",
    "audit_decision",
    "audit_confidence",
    "audit_evidence",
    "audit_reason",
    "audit_model",
    "audit_method",
    "audit_batch_id",
    "audit_reviewed_at",
    "audited_at",
    "match_basis",
]
SUMMARY_PATH = ROOT / "docs" / "当前Neo4j企业挂载环节与依据汇总.md"
SCHEMA_SUMMARY_PATH = ROOT / "docs" / "当前Neo4j结构快照.md"
SCHEMA_CYPHER_PATH = ROOT / "neo4j" / "cypher" / "current_schema.cypher"


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
           e.is_invested AS is_invested,
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
           r.updated_at AS updated_at,
           r.status AS status,
           r.audit_status AS audit_status,
           r.audit_decision AS audit_decision,
           r.audit_confidence AS audit_confidence,
           r.audit_evidence AS audit_evidence,
           r.audit_reason AS audit_reason,
           r.audit_model AS audit_model,
           r.audit_method AS audit_method,
           r.audit_batch_id AS audit_batch_id,
           r.audit_reviewed_at AS audit_reviewed_at,
           r.audited_at AS audited_at,
           r.match_basis AS match_basis
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


def fetch_schema(driver: Driver) -> dict[str, list[dict[str, Any]]]:
    queries = {
        "constraints": """
            SHOW CONSTRAINTS
            YIELD name, type, entityType, labelsOrTypes, properties, createStatement
            RETURN name, type, entityType, labelsOrTypes, properties, createStatement
            ORDER BY name
        """,
        "indexes": """
            SHOW INDEXES
            YIELD name, type, entityType, labelsOrTypes, properties,
                  owningConstraint, options, createStatement
            WHERE owningConstraint IS NULL AND type <> 'LOOKUP'
            RETURN name, type, entityType, labelsOrTypes, properties,
                   options, createStatement
            ORDER BY name
        """,
        "node_properties": """
            CALL db.schema.nodeTypeProperties()
            YIELD nodeLabels, propertyName, propertyTypes, mandatory
            WITH nodeLabels, propertyName, propertyTypes, mandatory
            MATCH (n)
            WHERE any(label IN labels(n) WHERE label IN nodeLabels)
              AND propertyName IN keys(n)
            RETURN nodeLabels, propertyName, propertyTypes, mandatory,
                   count(n) AS populated
            ORDER BY nodeLabels, propertyName
        """,
        "relationship_properties": """
            CALL db.schema.relTypeProperties()
            YIELD relType, propertyName, propertyTypes, mandatory
            WITH replace(replace(relType, ':`', ''), '`', '') AS relationshipType,
                 propertyName, propertyTypes, mandatory
            MATCH ()-[r]->()
            WHERE type(r) = relationshipType AND propertyName IN keys(r)
            RETURN relationshipType, propertyName, propertyTypes, mandatory,
                   count(r) AS populated
            ORDER BY relationshipType, propertyName
        """,
        "node_counts": """
            MATCH (n)
            UNWIND labels(n) AS label
            RETURN label, count(*) AS count
            ORDER BY label
        """,
        "relationship_counts": """
            MATCH ()-[r]->()
            RETURN type(r) AS relationshipType, count(*) AS count
            ORDER BY relationshipType
        """,
        "audit_batches": """
            MATCH (n:MountAuditSnapshot)
            RETURN 'MountAuditSnapshot' AS label, n.batch_id AS batchId,
                   NULL AS correctionBatchId, count(*) AS count
            UNION ALL
            MATCH (n:MountAuditDecision)
            RETURN 'MountAuditDecision' AS label, n.batch_id AS batchId,
                   n.correction_batch_id AS correctionBatchId, count(*) AS count
            ORDER BY label, batchId, correctionBatchId
        """,
    }
    result: dict[str, list[dict[str, Any]]] = {}
    with driver.session() as session:
        for name, query in queries.items():
            result[name] = [dict(record) for record in session.run(query)]
    return result


def idempotent_create(statement: str) -> str:
    return re.sub(
        r"^(CREATE (?:CONSTRAINT|FULLTEXT INDEX|VECTOR INDEX) `[^`]+`)",
        r"\1 IF NOT EXISTS",
        statement,
    )


def write_schema_cypher(path: Path, schema: dict[str, list[dict[str, Any]]]) -> None:
    lines = [
        "// Generated from neo4j-kg-v2-finegrain by sync_project_from_neo4j.py.",
        "// Neo4j-managed LOOKUP indexes are intentionally omitted.",
        "",
    ]
    statements = [
        record["createStatement"]
        for section in ("constraints", "indexes")
        for record in schema[section]
        if record.get("createStatement")
    ]
    for statement in statements:
        lines.extend([idempotent_create(statement) + ";", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def schema_list(value: Any) -> str:
    if not value:
        return "-"
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)


def write_schema_summary(
    path: Path, schema: dict[str, list[dict[str, Any]]], generated_at: str
) -> None:
    node_counts = {row["label"]: row["count"] for row in schema["node_counts"]}
    rel_counts = {
        row["relationshipType"]: row["count"]
        for row in schema["relationship_counts"]
    }
    lines = [
        "# 当前 Neo4j 结构快照",
        "",
        "> 数据来源：Docker 容器 `neo4j-kg-v2-finegrain`。",
        f"> 生成时间：`{generated_at}`。",
        "> 本文件由 `scripts/sync_project_from_neo4j.py` 生成；属性“完整”表示当前该类型的所有实体都包含该属性，不代表存在性约束。",
        "",
        "## 节点类型",
        "",
        "| 标签 | 当前节点数 |",
        "|---|---:|",
    ]
    for label, count in node_counts.items():
        lines.append(f"| `{label}` | {count} |")

    lines += [
        "",
        "## 关系类型",
        "",
        "| 类型 | 当前关系数 |",
        "|---|---:|",
    ]
    for relationship_type, count in rel_counts.items():
        lines.append(f"| `{relationship_type}` | {count} |")

    lines += [
        "",
        "## 约束",
        "",
        "| 名称 | 类型 | 实体 | 标签/类型 | 属性 |",
        "|---|---|---|---|---|",
    ]
    for row in schema["constraints"]:
        lines.append(
            f"| `{row['name']}` | {row['type']} | {row['entityType']} | "
            f"{schema_list(row['labelsOrTypes'])} | {schema_list(row['properties'])} |"
        )

    lines += [
        "",
        "## 用户索引",
        "",
        "Neo4j 自动创建的节点/关系 LOOKUP 索引未列入可重建脚本。",
        "",
        "| 名称 | 类型 | 实体 | 标签/类型 | 属性 |",
        "|---|---|---|---|---|",
    ]
    for row in schema["indexes"]:
        lines.append(
            f"| `{row['name']}` | {row['type']} | {row['entityType']} | "
            f"{schema_list(row['labelsOrTypes'])} | {schema_list(row['properties'])} |"
        )

    lines += [
        "",
        "## 节点属性",
        "",
        "| 标签 | 属性 | 当前类型 | 已填充 | 完整 |",
        "|---|---|---|---:|---|",
    ]
    for row in schema["node_properties"]:
        labels = schema_list(row["nodeLabels"])
        lines.append(
            f"| `{labels}` | `{row['propertyName']}` | "
            f"{schema_list(row['propertyTypes'])} | {row['populated']} | "
            f"{'是' if row['mandatory'] else '否'} |"
        )

    lines += [
        "",
        "## 关系属性",
        "",
        "| 关系类型 | 属性 | 当前类型 | 已填充 | 完整 |",
        "|---|---|---|---:|---|",
    ]
    for row in schema["relationship_properties"]:
        lines.append(
            f"| `{row['relationshipType']}` | `{row['propertyName']}` | "
            f"{schema_list(row['propertyTypes'])} | {row['populated']} | "
            f"{'是' if row['mandatory'] else '否'} |"
        )

    lines += [
        "",
        "## 挂载审计批次",
        "",
        "| 节点类型 | 批次 | 修正批次 | 节点数 |",
        "|---|---|---|---:|",
    ]
    for row in schema["audit_batches"]:
        correction = row["correctionBatchId"] or "-"
        lines.append(
            f"| `{row['label']}` | `{row['batchId']}` | `{correction}` | {row['count']} |"
        )

    lines += [
        "",
        "## 重建入口",
        "",
        "- 约束和用户索引：`neo4j/cypher/current_schema.cypher`",
        "- 基础图谱和当前挂载：`neo4j/cypher/import_finegrain_base.cypher`",
        "- 标准中间表：`data/mappings/*.csv`、`data/staging/*.csv`",
        "- `Enterprise.embedding` 向量值和两个审计节点类型的数据未写入标准中间表；本快照记录其结构、数量和批次。",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


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
        schema = fetch_schema(driver)
    finally:
        driver.close()

    enterprise_path = ROOT / "data" / "staging" / "enterprises.csv"
    mount_path = ROOT / "data" / "staging" / "enterprise_to_substage.csv"
    write_csv(enterprise_path, ENTERPRISE_FIELDS, enterprises)
    write_csv(mount_path, MOUNT_FIELDS, mounts)

    if not args.no_import_copy:
        import_dir = ROOT / "neo4j" / "import"
        shutil.copyfile(enterprise_path, import_dir / enterprise_path.name)
        shutil.copyfile(mount_path, import_dir / mount_path.name)

    write_summary(SUMMARY_PATH, summary_rows, len(enterprises))
    generated_at = datetime.now(timezone.utc).isoformat()
    write_schema_cypher(SCHEMA_CYPHER_PATH, schema)
    write_schema_summary(SCHEMA_SUMMARY_PATH, schema, generated_at)

    print(f"Exported {len(enterprises)} Enterprise nodes")
    print(f"Exported {len(mounts)} LOCATED_IN_SUBSTAGE relationships")
    print(f"Recorded {len(schema['node_counts'])} node labels")
    print(f"Recorded {len(schema['relationship_counts'])} relationship types")


if __name__ == "__main__":
    main()
