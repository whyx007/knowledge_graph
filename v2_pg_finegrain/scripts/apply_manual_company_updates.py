#!/usr/bin/env python3
"""Update existing companies and add new companies to PostgreSQL and Neo4j.

The operation targets the running ceo_brief PostgreSQL database and the
neo4j-kg-v2-finegrain Docker Neo4j instance. It creates logical snapshots
before writing and keeps all PostgreSQL mutations in one transaction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import date, datetime, time, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import uuid4

import psycopg2
from neo4j import GraphDatabase
from psycopg2.extras import RealDictCursor

from preview_manual_company_updates import (
    DEFAULT_DSN,
    DEFAULT_XLSX,
    FIELDS,
    MANUAL_NAME_MAP,
    clean_text,
    load_excel,
    website_review,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BACKUP_ROOT = ROOT / "data" / "backups"
NEO4J_FIELDS = tuple(field.db_column for field in FIELDS)
EXPECTED_PG_BEFORE = 480
EXPECTED_EXCEL = 526
EXPECTED_EXISTING = 480
EXPECTED_NEW = 46
EXPECTED_MOUNTS = 293


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="将人工确认企业信息增量写入 PostgreSQL 和 Neo4j")
    parser.add_argument("--xlsx", type=Path, default=DEFAULT_XLSX)
    parser.add_argument("--dsn", default=os.getenv("PG_DSN", DEFAULT_DSN))
    parser.add_argument("--neo4j-uri", default=os.getenv("NEO4J_URI", "bolt://127.0.0.1:7688"))
    parser.add_argument("--neo4j-user", default=os.getenv("NEO4J_USER", "neo4j"))
    parser.add_argument("--neo4j-password", default=os.getenv("NEO4J_PASSWORD", "neo4j2026"))
    parser.add_argument("--backup-root", type=Path, default=DEFAULT_BACKUP_ROOT)
    parser.add_argument("--apply", action="store_true", help="执行备份和双库写入；缺省只做预检")
    return parser.parse_args()


def json_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [json_value(item) for item in value]
    return str(value)


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(json_value(value), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_website(value: str | None) -> str | None:
    if not value:
        return None
    status, suggested = website_review(value)
    if status in {"www_without_protocol", "bare_domain_without_protocol"}:
        return suggested
    return value


def pg_snapshot(connection: Any) -> list[dict[str, Any]]:
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM public.companies ORDER BY id")
        return [dict(row) for row in cursor.fetchall()]


def neo4j_snapshot(driver: Any) -> dict[str, Any]:
    with driver.session() as session:
        enterprises = [
            {"enterprise_id": row["enterprise_id"], "properties": dict(row["properties"])}
            for row in session.run(
                "MATCH (e:Enterprise) "
                "RETURN e.enterprise_id AS enterprise_id, properties(e) AS properties "
                "ORDER BY enterprise_id"
            )
        ]
        relationships = [
            {
                "enterprise_id": row["enterprise_id"],
                "type": row["type"],
                "other_labels": row["other_labels"],
                "other_identity": row["other_identity"],
                "properties": dict(row["properties"]),
            }
            for row in session.run(
                "MATCH (e:Enterprise)-[r]-(other) "
                "RETURN e.enterprise_id AS enterprise_id, type(r) AS type, "
                "labels(other) AS other_labels, "
                "coalesce(other.substage_id, other.enterprise_id, other.stage_id, "
                "other.segment_id, other.chain_id) AS other_identity, "
                "properties(r) AS properties "
                "ORDER BY enterprise_id, type, other_identity"
            )
        ]
        counts = session.run(
            "MATCH (e:Enterprise) WITH count(e) AS enterprises "
            "MATCH ()-[r:LOCATED_IN_SUBSTAGE]->() "
            "RETURN enterprises, count(r) AS mounts"
        ).single(strict=True)
    return {
        "enterprises": enterprises,
        "enterprise_relationships": relationships,
        "counts": dict(counts),
    }


def fetch_pg_baseline(dsn: str) -> tuple[list[dict[str, Any]], dict[str, int]]:
    connection = psycopg2.connect(dsn)
    try:
        connection.autocommit = False
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SET TRANSACTION READ ONLY")
            cursor.execute(
                "SELECT id,name,company_profile,founder,core_tech,products,scenario,cert_ip,website "
                "FROM public.companies ORDER BY id"
            )
            companies = [dict(row) for row in cursor.fetchall()]
            cursor.execute(
                "SELECT count(*) FILTER (WHERE core_tech_vec IS NOT NULL) AS core_vectors, "
                "count(*) FILTER (WHERE full_text_vec IS NOT NULL) AS full_vectors "
                "FROM public.companies"
            )
            vector_counts = dict(cursor.fetchone())
        connection.rollback()
        return companies, vector_counts
    finally:
        connection.close()


def build_operations(
    excel_rows: list[dict[str, Any]], pg_rows: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int]]:
    pg_by_name = {row["name"]: row for row in pg_rows}
    existing: list[dict[str, Any]] = []
    new: list[dict[str, Any]] = []
    seen_ids: set[int] = set()
    stats = {"field_updates": 0, "website_normalized": 0, "vector_invalidations": 0}

    for excel in excel_rows:
        source_name = excel["excel_name"]
        pg_name = MANUAL_NAME_MAP.get(source_name, source_name)
        pg = pg_by_name.get(pg_name)
        target: dict[str, Any] = {
            "excel_row": excel["excel_row"],
            "excel_name": source_name,
            "name": pg_name if pg else source_name,
        }
        changed_fields: list[str] = []
        for field in FIELDS:
            column = field.db_column
            value = excel[column]
            if column == "website" and value:
                normalized = normalize_website(value)
                if normalized != value:
                    stats["website_normalized"] += 1
                value = normalized
            if pg:
                old = pg[column]
                if value is None:
                    value = old
                elif value != clean_text(old):
                    changed_fields.append(column)
                    stats["field_updates"] += 1
            target[column] = value
        target["changed_fields"] = changed_fields

        if pg:
            if pg["id"] in seen_ids:
                raise RuntimeError(f"多个 Excel 行映射到 PostgreSQL id={pg['id']}")
            seen_ids.add(pg["id"])
            target["id"] = pg["id"]
            if {"core_tech", "products"} & set(changed_fields):
                stats["vector_invalidations"] += 1
            existing.append(target)
        else:
            new.append(target)

    missing_ids = {row["id"] for row in pg_rows} - seen_ids
    if missing_ids:
        raise RuntimeError(f"Excel 未覆盖 {len(missing_ids)} 个现有 PostgreSQL id")
    return existing, new, stats


def preflight(args: argparse.Namespace) -> dict[str, Any]:
    xlsx = args.xlsx.resolve()
    excel_rows, excel_metadata = load_excel(xlsx)
    pg_rows, vector_counts = fetch_pg_baseline(args.dsn)
    existing, new, stats = build_operations(excel_rows, pg_rows)

    driver = GraphDatabase.driver(
        args.neo4j_uri, auth=(args.neo4j_user, args.neo4j_password)
    )
    try:
        neo = neo4j_snapshot(driver)
    finally:
        driver.close()

    assertions = {
        "excel_companies": len(excel_rows),
        "postgres_before": len(pg_rows),
        "existing_updates": len(existing),
        "new_inserts": len(new),
        "neo4j_before": neo["counts"]["enterprises"],
        "mounts_before": neo["counts"]["mounts"],
        **vector_counts,
    }
    expected = {
        "excel_companies": EXPECTED_EXCEL,
        "postgres_before": EXPECTED_PG_BEFORE,
        "existing_updates": EXPECTED_EXISTING,
        "new_inserts": EXPECTED_NEW,
        "neo4j_before": EXPECTED_PG_BEFORE,
        "mounts_before": EXPECTED_MOUNTS,
        "core_vectors": 0,
        "full_vectors": 0,
    }
    failures = {
        key: {"expected": expected[key], "actual": value}
        for key, value in assertions.items()
        if value != expected[key]
    }
    pg_names = {row["name"] for row in pg_rows}
    neo_names = {
        row["properties"].get("enterprise_name") for row in neo["enterprises"]
    }
    if pg_names != neo_names:
        failures["pg_neo4j_name_sets"] = {
            "missing_in_neo4j": sorted(pg_names - neo_names),
            "extra_in_neo4j": sorted(neo_names - pg_names),
        }
    if failures:
        raise RuntimeError("预检断言失败：" + json.dumps(failures, ensure_ascii=False))

    return {
        "xlsx": xlsx,
        "source_sha256": sha256_file(xlsx),
        "excel_metadata": excel_metadata,
        "pg_rows": pg_rows,
        "existing": existing,
        "new": new,
        "neo_snapshot": neo,
        "stats": stats,
        "assertions": assertions,
    }


def create_backups(
    args: argparse.Namespace, state: dict[str, Any], run_id: str
) -> tuple[Path, list[dict[str, Any]]]:
    backup_dir = args.backup_root.resolve() / run_id
    backup_dir.mkdir(parents=True, exist_ok=False)
    shutil.copy2(state["xlsx"], backup_dir / "source.xlsx")

    dump_path = backup_dir / "postgres_companies_before.dump"
    subprocess.run(
        [
            "pg_dump", "--format=custom", "--no-owner", "--no-privileges",
            "--table=public.companies", f"--file={dump_path}", args.dsn,
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    connection = psycopg2.connect(args.dsn)
    try:
        connection.autocommit = False
        with connection.cursor() as cursor:
            cursor.execute("SET TRANSACTION READ ONLY")
        postgres_rows = pg_snapshot(connection)
        connection.rollback()
    finally:
        connection.close()
    write_json(backup_dir / "postgres_companies_before.json", postgres_rows)
    write_json(
        backup_dir / "neo4j_enterprises_before.json",
        state["neo_snapshot"]["enterprises"],
    )
    write_json(
        backup_dir / "neo4j_enterprise_relationships_before.json",
        state["neo_snapshot"]["enterprise_relationships"],
    )
    write_json(
        backup_dir / "preflight.json",
        {
            "run_id": run_id,
            "source_sha256": state["source_sha256"],
            "assertions": state["assertions"],
            "stats": state["stats"],
        },
    )
    manifest = {
        path.name: {"size": path.stat().st_size, "sha256": sha256_file(path)}
        for path in backup_dir.iterdir()
        if path.is_file()
    }
    write_json(backup_dir / "manifest.json", manifest)
    return backup_dir, postgres_rows


def apply_postgres(
    connection: Any,
    existing: list[dict[str, Any]],
    new: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    fields = list(NEO4J_FIELDS)
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("LOCK TABLE public.companies IN SHARE ROW EXCLUSIVE MODE")
        cursor.execute("SELECT count(*) AS count FROM public.companies")
        if cursor.fetchone()["count"] != EXPECTED_PG_BEFORE:
            raise RuntimeError("PostgreSQL 行数在预检后发生变化")

        update_sql = (
            "UPDATE public.companies SET "
            + ", ".join(f"{field} = %s" for field in fields)
            + ", core_tech_vec = CASE WHEN %s THEN NULL ELSE core_tech_vec END"
            + ", full_text_vec = CASE WHEN %s THEN NULL ELSE full_text_vec END"
            + " WHERE id = %s"
        )
        for row in existing:
            invalidate = bool({"core_tech", "products"} & set(row["changed_fields"]))
            cursor.execute(
                update_sql,
                [*(row[field] for field in fields), invalidate, invalidate, row["id"]],
            )
            if cursor.rowcount != 1:
                raise RuntimeError(f"更新 PostgreSQL id={row['id']} 失败")

        insert_sql = (
            "INSERT INTO public.companies "
            "(name, company_profile, founder, core_tech, products, scenario, cert_ip, website, "
            "status, source_file, is_invested) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'在持','企业信息确认人工确认.xlsx',true) "
            "RETURNING id"
        )
        for row in new:
            cursor.execute(insert_sql, [row["name"], *(row[field] for field in fields)])
            row["id"] = cursor.fetchone()["id"]

        cursor.execute(
            "SELECT id,name,company_profile,founder,core_tech,products,scenario,cert_ip,website "
            "FROM public.companies ORDER BY id"
        )
        final_rows = [dict(row) for row in cursor.fetchall()]
        if len(final_rows) != EXPECTED_EXCEL:
            raise RuntimeError(f"PostgreSQL 事务内行数不是 {EXPECTED_EXCEL}")
    return final_rows


def neo4j_payload(pg_rows: list[dict[str, Any]], run_id: str) -> list[dict[str, Any]]:
    payload = []
    for row in pg_rows:
        item = {
            "enterprise_id": f"ENT_PG_{row['id']}",
            "enterprise_name": row["name"],
            "source_pk": str(row["id"]),
            "profile_sync_run_id": run_id,
        }
        item.update({field: row[field] for field in NEO4J_FIELDS})
        payload.append(item)
    return payload


def apply_neo4j(driver: Any, rows: list[dict[str, Any]], run_id: str) -> None:
    query = (
        "UNWIND $rows AS row "
        "MERGE (e:Enterprise {enterprise_id: row.enterprise_id}) "
        "SET e.enterprise_name = row.enterprise_name, e.source_pk = row.source_pk, "
        "e.source_system = 'postgresql', e.company_profile = row.company_profile, "
        "e.founder = row.founder, e.core_tech = row.core_tech, e.products = row.products, "
        "e.scenario = row.scenario, e.cert_ip = row.cert_ip, e.website = row.website, "
        "e.profile_source = 'manual_confirmation_xlsx', "
        "e.profile_sync_run_id = $run_id, e.last_profile_sync_at = datetime(), "
        "e.last_sync_at = datetime()"
    )
    with driver.session() as session:
        transaction = session.begin_transaction()
        try:
            for start in range(0, len(rows), 100):
                transaction.run(query, rows=rows[start : start + 100], run_id=run_id).consume()
            counts = transaction.run(
                "MATCH (e:Enterprise) WITH count(e) AS enterprises "
                "MATCH ()-[r:LOCATED_IN_SUBSTAGE]->() "
                "RETURN enterprises, count(r) AS mounts"
            ).single(strict=True)
            if counts["enterprises"] != EXPECTED_EXCEL or counts["mounts"] != EXPECTED_MOUNTS:
                raise RuntimeError(f"Neo4j 事务内计数异常：{dict(counts)}")
            synced = transaction.run(
                "MATCH (e:Enterprise {profile_sync_run_id: $run_id}) RETURN count(e) AS count",
                run_id=run_id,
            ).single(strict=True)["count"]
            if synced != EXPECTED_EXCEL:
                raise RuntimeError(f"Neo4j 事务内仅同步 {synced} 个节点")
            transaction.commit()
        except Exception:
            transaction.rollback()
            raise


def restore_neo4j(driver: Any, snapshot: list[dict[str, Any]], new_ids: list[str]) -> None:
    with driver.session() as session:
        transaction = session.begin_transaction()
        try:
            if new_ids:
                transaction.run(
                    "MATCH (e:Enterprise) WHERE e.enterprise_id IN $ids DETACH DELETE e",
                    ids=new_ids,
                ).consume()
            for start in range(0, len(snapshot), 100):
                transaction.run(
                    "UNWIND $rows AS row "
                    "MATCH (e:Enterprise {enterprise_id: row.enterprise_id}) "
                    "SET e = row.properties",
                    rows=snapshot[start : start + 100],
                ).consume()
            transaction.commit()
        except Exception:
            transaction.rollback()
            raise


def verify(args: argparse.Namespace, run_id: str, expected_rows: list[dict[str, Any]]) -> dict[str, Any]:
    connection = psycopg2.connect(args.dsn)
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT id,name,company_profile,founder,core_tech,products,scenario,cert_ip,website "
                "FROM public.companies ORDER BY id"
            )
            pg_rows = [dict(row) for row in cursor.fetchall()]
    finally:
        connection.close()
    if pg_rows != expected_rows:
        raise RuntimeError("PostgreSQL 提交后数据与事务内验收结果不一致")

    expected = {f"ENT_PG_{row['id']}": row for row in pg_rows}
    driver = GraphDatabase.driver(
        args.neo4j_uri, auth=(args.neo4j_user, args.neo4j_password)
    )
    try:
        with driver.session() as session:
            neo_rows = [
                dict(row)
                for row in session.run(
                    "MATCH (e:Enterprise) RETURN e.enterprise_id AS enterprise_id, "
                    "e.enterprise_name AS name, e.source_pk AS source_pk, "
                    "e.company_profile AS company_profile, e.founder AS founder, "
                    "e.core_tech AS core_tech, e.products AS products, e.scenario AS scenario, "
                    "e.cert_ip AS cert_ip, e.website AS website ORDER BY enterprise_id"
                )
            ]
            counts = dict(
                session.run(
                    "MATCH (e:Enterprise) WITH count(e) AS enterprises "
                    "MATCH ()-[r:LOCATED_IN_SUBSTAGE]->() "
                    "RETURN enterprises, count(r) AS mounts"
                ).single(strict=True)
            )
            run_count = session.run(
                "MATCH (e:Enterprise {profile_sync_run_id: $run_id}) RETURN count(e) AS count",
                run_id=run_id,
            ).single(strict=True)["count"]
    finally:
        driver.close()

    mismatches = []
    for neo in neo_rows:
        pg = expected.get(neo["enterprise_id"])
        if pg is None:
            mismatches.append({"enterprise_id": neo["enterprise_id"], "reason": "missing_pg"})
            continue
        if neo["name"] != pg["name"] or neo["source_pk"] != str(pg["id"]):
            mismatches.append({"enterprise_id": neo["enterprise_id"], "reason": "identity"})
            continue
        for field in NEO4J_FIELDS:
            if neo[field] != pg[field]:
                mismatches.append({"enterprise_id": neo["enterprise_id"], "field": field})
    if counts != {"enterprises": EXPECTED_EXCEL, "mounts": EXPECTED_MOUNTS}:
        raise RuntimeError(f"双库验收 Neo4j 计数失败：{counts}")
    if run_count != EXPECTED_EXCEL or len(neo_rows) != EXPECTED_EXCEL or mismatches:
        raise RuntimeError(
            f"双库逐字段验收失败：run_count={run_count}, neo_rows={len(neo_rows)}, "
            f"mismatches={mismatches[:10]}"
        )
    return {
        "postgres_companies": len(pg_rows),
        "neo4j_enterprises": counts["enterprises"],
        "neo4j_mounts": counts["mounts"],
        "field_mismatches": 0,
        "run_id_nodes": run_count,
    }


def main() -> None:
    args = parse_args()
    state = preflight(args)
    report = {
        "source_sha256": state["source_sha256"],
        "assertions": state["assertions"],
        "planned_existing_updates": len(state["existing"]),
        "planned_new_inserts": len(state["new"]),
        "stats": state["stats"],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.apply:
        print("\n预检通过；未执行写入。使用 --apply 执行。")
        return

    run_id = "manual_company_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid4().hex[:8]
    backup_dir, _ = create_backups(args, state, run_id)
    connection = psycopg2.connect(args.dsn)
    driver = GraphDatabase.driver(
        args.neo4j_uri, auth=(args.neo4j_user, args.neo4j_password)
    )
    neo_committed = False
    new_enterprise_ids: list[str] = []
    try:
        connection.autocommit = False
        final_pg_rows = apply_postgres(connection, state["existing"], state["new"])
        new_enterprise_ids = [f"ENT_PG_{row['id']}" for row in state["new"]]
        apply_neo4j(driver, neo4j_payload(final_pg_rows, run_id), run_id)
        neo_committed = True
        connection.commit()
    except Exception:
        connection.rollback()
        if neo_committed:
            restore_neo4j(driver, state["neo_snapshot"]["enterprises"], new_enterprise_ids)
        raise
    finally:
        connection.close()
        driver.close()

    verification = verify(args, run_id, final_pg_rows)
    result = {
        **report,
        "run_id": run_id,
        "backup_dir": str(backup_dir),
        "new_postgres_ids": [row["id"] for row in state["new"]],
        "verification": verification,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    write_json(backup_dir / "result.json", result)
    print("\n" + json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
