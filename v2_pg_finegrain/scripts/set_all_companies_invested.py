#!/usr/bin/env python3
"""Set is_invested=true for all current PostgreSQL and Neo4j companies."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import psycopg2
from neo4j import GraphDatabase

from apply_manual_company_updates import (
    DEFAULT_BACKUP_ROOT,
    DEFAULT_DSN,
    neo4j_snapshot,
    pg_snapshot,
    restore_neo4j,
    sha256_file,
    write_json,
)


EXPECTED_COMPANIES = 525
EXPECTED_MOUNTS = 293


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="将现有企业统一标记为已被投")
    parser.add_argument("--dsn", default=os.getenv("PG_DSN", DEFAULT_DSN))
    parser.add_argument("--neo4j-uri", default=os.getenv("NEO4J_URI", "bolt://127.0.0.1:7688"))
    parser.add_argument("--neo4j-user", default=os.getenv("NEO4J_USER", "neo4j"))
    parser.add_argument("--neo4j-password", default=os.getenv("NEO4J_PASSWORD", "neo4j2026"))
    parser.add_argument("--backup-root", type=Path, default=DEFAULT_BACKUP_ROOT)
    parser.add_argument("--apply", action="store_true", help="备份后执行双库写入")
    return parser.parse_args()


def preflight(args: argparse.Namespace) -> dict[str, Any]:
    connection = psycopg2.connect(args.dsn)
    try:
        connection.autocommit = False
        with connection.cursor() as cursor:
            cursor.execute("SET TRANSACTION READ ONLY")
        pg_rows = pg_snapshot(connection)
        connection.rollback()
    finally:
        connection.close()
    if len(pg_rows) != EXPECTED_COMPANIES:
        raise RuntimeError(f"PostgreSQL 企业数不是 {EXPECTED_COMPANIES}")
    pg_true = sum(row["is_invested"] is True for row in pg_rows)

    driver = GraphDatabase.driver(
        args.neo4j_uri, auth=(args.neo4j_user, args.neo4j_password)
    )
    try:
        neo = neo4j_snapshot(driver)
        with driver.session() as session:
            values = dict(
                session.run(
                    "MATCH (e:Enterprise) RETURN count(e) AS total, "
                    "count(e.is_invested) AS with_field, "
                    "count(CASE WHEN e.is_invested = true THEN 1 END) AS true_count, "
                    "count(CASE WHEN e.is_invested = false THEN 1 END) AS false_count"
                ).single(strict=True)
            )
    finally:
        driver.close()
    if neo["counts"] != {"enterprises": EXPECTED_COMPANIES, "mounts": EXPECTED_MOUNTS}:
        raise RuntimeError(f"Neo4j 基线异常：{neo['counts']}")
    if pg_true != EXPECTED_COMPANIES:
        raise RuntimeError(f"PostgreSQL 仅有 {pg_true} 家 is_invested=true")
    return {"pg_rows": pg_rows, "neo": neo, "neo_values": values}


def create_backups(args: argparse.Namespace, state: dict[str, Any], run_id: str) -> Path:
    backup_dir = args.backup_root.resolve() / run_id
    backup_dir.mkdir(parents=True, exist_ok=False)
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
    write_json(backup_dir / "postgres_companies_before.json", state["pg_rows"])
    write_json(backup_dir / "neo4j_enterprises_before.json", state["neo"]["enterprises"])
    write_json(
        backup_dir / "neo4j_enterprise_relationships_before.json",
        state["neo"]["enterprise_relationships"],
    )
    write_json(
        backup_dir / "preflight.json",
        {"run_id": run_id, "postgres_true": EXPECTED_COMPANIES, "neo4j": state["neo_values"]},
    )
    manifest = {
        path.name: {"size": path.stat().st_size, "sha256": sha256_file(path)}
        for path in backup_dir.iterdir()
        if path.is_file()
    }
    write_json(backup_dir / "manifest.json", manifest)
    return backup_dir


def apply_postgres(connection: Any) -> int:
    with connection.cursor() as cursor:
        cursor.execute("LOCK TABLE public.companies IN SHARE ROW EXCLUSIVE MODE")
        cursor.execute("SELECT count(*) FROM public.companies")
        if cursor.fetchone()[0] != EXPECTED_COMPANIES:
            raise RuntimeError("PostgreSQL 企业数在预检后发生变化")
        cursor.execute(
            "UPDATE public.companies SET is_invested = true "
            "WHERE is_invested IS DISTINCT FROM true"
        )
        changed = cursor.rowcount
        cursor.execute(
            "SELECT count(*) FROM public.companies WHERE is_invested IS DISTINCT FROM true"
        )
        if cursor.fetchone()[0] != 0:
            raise RuntimeError("PostgreSQL 事务内仍有非已投企业")
        return changed


def apply_neo4j(driver: Any, run_id: str) -> int:
    with driver.session() as session:
        transaction = session.begin_transaction()
        try:
            result = transaction.run(
                "MATCH (e:Enterprise) SET e.is_invested = true, "
                "e.invested_flag_run_id = $run_id, e.invested_flag_updated_at = datetime()",
                run_id=run_id,
            ).consume()
            counts = transaction.run(
                "MATCH (e:Enterprise) WITH count(e) AS enterprises, "
                "count(CASE WHEN e.is_invested = true THEN 1 END) AS invested "
                "MATCH ()-[r:LOCATED_IN_SUBSTAGE]->() "
                "RETURN enterprises, invested, count(r) AS mounts"
            ).single(strict=True)
            if dict(counts) != {
                "enterprises": EXPECTED_COMPANIES,
                "invested": EXPECTED_COMPANIES,
                "mounts": EXPECTED_MOUNTS,
            }:
                raise RuntimeError(f"Neo4j 事务内验收失败：{dict(counts)}")
            transaction.commit()
            return result.counters.properties_set
        except Exception:
            transaction.rollback()
            raise


def verify(args: argparse.Namespace, state: dict[str, Any], run_id: str) -> dict[str, Any]:
    connection = psycopg2.connect(args.dsn)
    try:
        connection.autocommit = False
        current_pg = pg_snapshot(connection)
        connection.rollback()
    finally:
        connection.close()
    if current_pg != state["pg_rows"]:
        raise RuntimeError("PostgreSQL 原本已全为 true，但写入后快照发生变化")

    driver = GraphDatabase.driver(
        args.neo4j_uri, auth=(args.neo4j_user, args.neo4j_password)
    )
    try:
        current_neo = neo4j_snapshot(driver)
    finally:
        driver.close()
    old_by_id = {row["enterprise_id"]: row["properties"] for row in state["neo"]["enterprises"]}
    unexpected = []
    for row in current_neo["enterprises"]:
        old = old_by_id[row["enterprise_id"]]
        new = row["properties"]
        for key in set(old) | set(new):
            if old.get(key) == new.get(key):
                continue
            if key not in {"is_invested", "invested_flag_run_id", "invested_flag_updated_at"}:
                unexpected.append((row["enterprise_id"], key))
        if new.get("is_invested") is not True or new.get("invested_flag_run_id") != run_id:
            unexpected.append((row["enterprise_id"], "is_invested"))
    if unexpected:
        raise RuntimeError(f"Neo4j 出现非预期属性变化：{unexpected[:10]}")
    if current_neo["enterprise_relationships"] != state["neo"]["enterprise_relationships"]:
        raise RuntimeError("Neo4j 企业关系发生变化")
    if current_neo["counts"] != {"enterprises": EXPECTED_COMPANIES, "mounts": EXPECTED_MOUNTS}:
        raise RuntimeError(f"Neo4j 最终计数异常：{current_neo['counts']}")
    return {
        "postgres_invested_true": EXPECTED_COMPANIES,
        "neo4j_invested_true": EXPECTED_COMPANIES,
        "postgres_other_changes": 0,
        "neo4j_unexpected_property_changes": 0,
        "enterprise_relationships_changed": 0,
    }


def main() -> None:
    args = parse_args()
    state = preflight(args)
    preview = {
        "postgres_companies": EXPECTED_COMPANIES,
        "postgres_already_true": EXPECTED_COMPANIES,
        "neo4j_before": state["neo_values"],
        "target_value": True,
    }
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    if not args.apply:
        print("\n预检通过；未执行写入。使用 --apply 执行。")
        return

    run_id = "set_all_invested_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid4().hex[:8]
    backup_dir = create_backups(args, state, run_id)
    connection = psycopg2.connect(args.dsn)
    driver = GraphDatabase.driver(
        args.neo4j_uri, auth=(args.neo4j_user, args.neo4j_password)
    )
    neo_committed = False
    try:
        connection.autocommit = False
        postgres_changed = apply_postgres(connection)
        neo4j_properties_set = apply_neo4j(driver, run_id)
        neo_committed = True
        connection.commit()
    except Exception:
        connection.rollback()
        if neo_committed:
            restore_neo4j(driver, state["neo"]["enterprises"], [])
        raise
    finally:
        connection.close()
        driver.close()

    verification = verify(args, state, run_id)
    result = {
        **preview,
        "run_id": run_id,
        "backup_dir": str(backup_dir),
        "postgres_rows_changed": postgres_changed,
        "neo4j_properties_set": neo4j_properties_set,
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
