#!/usr/bin/env python3
"""Delete the obsolete Open Source Consensus company duplicate from both stores."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import psycopg2
from neo4j import GraphDatabase
from psycopg2.extras import RealDictCursor

from apply_manual_company_updates import (
    DEFAULT_BACKUP_ROOT,
    DEFAULT_DSN,
    neo4j_snapshot,
    pg_snapshot,
    sha256_file,
    write_json,
)


OLD_ID = 265
OLD_NAME = "开源共识（上海）网络技术有限公司"
OLD_ENTERPRISE_ID = "ENT_PG_265"
NEW_ID = 1486
NEW_NAME = "上海开源共识智能科技股份公司"
NEW_ENTERPRISE_ID = "ENT_PG_1486"
EXPECTED_PG_BEFORE = 526
EXPECTED_PG_AFTER = 525
EXPECTED_MOUNTS = 293


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="删除已更名企业的旧重复记录")
    parser.add_argument("--dsn", default=os.getenv("PG_DSN", DEFAULT_DSN))
    parser.add_argument("--neo4j-uri", default=os.getenv("NEO4J_URI", "bolt://127.0.0.1:7688"))
    parser.add_argument("--neo4j-user", default=os.getenv("NEO4J_USER", "neo4j"))
    parser.add_argument("--neo4j-password", default=os.getenv("NEO4J_PASSWORD", "neo4j2026"))
    parser.add_argument("--backup-root", type=Path, default=DEFAULT_BACKUP_ROOT)
    parser.add_argument("--apply", action="store_true", help="备份后执行双库删除")
    return parser.parse_args()


def preflight(args: argparse.Namespace) -> dict[str, Any]:
    connection = psycopg2.connect(args.dsn)
    try:
        connection.autocommit = False
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SET TRANSACTION READ ONLY")
            cursor.execute("SELECT * FROM public.companies ORDER BY id")
            pg_rows = [dict(row) for row in cursor.fetchall()]
        connection.rollback()
    finally:
        connection.close()
    pg_by_id = {row["id"]: row for row in pg_rows}
    if len(pg_rows) != EXPECTED_PG_BEFORE:
        raise RuntimeError(f"PostgreSQL 企业数不是 {EXPECTED_PG_BEFORE}")
    if pg_by_id.get(OLD_ID, {}).get("name") != OLD_NAME:
        raise RuntimeError("PostgreSQL 旧企业 id/name 不匹配")
    if pg_by_id.get(NEW_ID, {}).get("name") != NEW_NAME:
        raise RuntimeError("PostgreSQL 新企业 id/name 不匹配")

    driver = GraphDatabase.driver(
        args.neo4j_uri, auth=(args.neo4j_user, args.neo4j_password)
    )
    try:
        neo = neo4j_snapshot(driver)
        with driver.session() as session:
            identities = {
                row["enterprise_id"]: row["enterprise_name"]
                for row in session.run(
                    "MATCH (e:Enterprise) WHERE e.enterprise_id IN $ids "
                    "RETURN e.enterprise_id AS enterprise_id, e.enterprise_name AS enterprise_name",
                    ids=[OLD_ENTERPRISE_ID, NEW_ENTERPRISE_ID],
                )
            }
            relationship_counts = dict(
                session.run(
                    "MATCH (e:Enterprise) WHERE e.enterprise_id IN $ids "
                    "OPTIONAL MATCH (e)-[r]-() "
                    "RETURN e.enterprise_id AS enterprise_id, count(r) AS relationships",
                    ids=[OLD_ENTERPRISE_ID, NEW_ENTERPRISE_ID],
                ).data()[0]
            )
            relationship_rows = session.run(
                "MATCH (e:Enterprise) WHERE e.enterprise_id IN $ids "
                "OPTIONAL MATCH (e)-[r]-() "
                "RETURN e.enterprise_id AS enterprise_id, count(r) AS relationships "
                "ORDER BY enterprise_id",
                ids=[OLD_ENTERPRISE_ID, NEW_ENTERPRISE_ID],
            ).data()
    finally:
        driver.close()
    if neo["counts"] != {"enterprises": EXPECTED_PG_BEFORE, "mounts": EXPECTED_MOUNTS}:
        raise RuntimeError(f"Neo4j 基线异常：{neo['counts']}")
    if identities != {OLD_ENTERPRISE_ID: OLD_NAME, NEW_ENTERPRISE_ID: NEW_NAME}:
        raise RuntimeError(f"Neo4j 新旧企业身份异常：{identities}")
    if any(row["relationships"] != 0 for row in relationship_rows):
        raise RuntimeError(f"新旧企业存在关系，拒绝直接删除：{relationship_rows}")
    return {"pg_rows": pg_rows, "neo": neo, "relationship_rows": relationship_rows}


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
    write_json(backup_dir / "postgres_deleted_row.json", next(row for row in state["pg_rows"] if row["id"] == OLD_ID))
    write_json(backup_dir / "neo4j_enterprises_before.json", state["neo"]["enterprises"])
    write_json(
        backup_dir / "neo4j_enterprise_relationships_before.json",
        state["neo"]["enterprise_relationships"],
    )
    write_json(
        backup_dir / "preflight.json",
        {
            "run_id": run_id,
            "old": {"id": OLD_ID, "name": OLD_NAME, "enterprise_id": OLD_ENTERPRISE_ID},
            "canonical": {"id": NEW_ID, "name": NEW_NAME, "enterprise_id": NEW_ENTERPRISE_ID},
            "relationships": state["relationship_rows"],
        },
    )
    manifest = {
        path.name: {"size": path.stat().st_size, "sha256": sha256_file(path)}
        for path in backup_dir.iterdir()
        if path.is_file()
    }
    write_json(backup_dir / "manifest.json", manifest)
    return backup_dir


def delete_postgres(connection: Any) -> None:
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("LOCK TABLE public.companies IN SHARE ROW EXCLUSIVE MODE")
        cursor.execute("SELECT count(*) AS count FROM public.companies")
        if cursor.fetchone()["count"] != EXPECTED_PG_BEFORE:
            raise RuntimeError("PostgreSQL 企业数在预检后发生变化")
        cursor.execute(
            "DELETE FROM public.companies WHERE id = %s AND name = %s RETURNING id,name",
            (OLD_ID, OLD_NAME),
        )
        deleted = cursor.fetchone()
        if not deleted or deleted["id"] != OLD_ID:
            raise RuntimeError("PostgreSQL 旧企业未被精确删除")
        cursor.execute("SELECT count(*) AS count FROM public.companies")
        if cursor.fetchone()["count"] != EXPECTED_PG_AFTER:
            raise RuntimeError("PostgreSQL 事务内删除后数量异常")
        cursor.execute("SELECT name FROM public.companies WHERE id = %s", (NEW_ID,))
        if cursor.fetchone()["name"] != NEW_NAME:
            raise RuntimeError("PostgreSQL 新企业在事务内异常")


def delete_neo4j(driver: Any) -> None:
    with driver.session() as session:
        transaction = session.begin_transaction()
        try:
            counters = transaction.run(
                "MATCH (old:Enterprise {enterprise_id: $old_id}) "
                "WHERE old.enterprise_name = $old_name DELETE old",
                old_id=OLD_ENTERPRISE_ID,
                old_name=OLD_NAME,
            ).consume().counters
            if counters.nodes_deleted != 1:
                raise RuntimeError("Neo4j 旧企业未被精确删除")
            counts = transaction.run(
                "MATCH (e:Enterprise) WITH count(e) AS enterprises "
                "MATCH ()-[r:LOCATED_IN_SUBSTAGE]->() "
                "RETURN enterprises, count(r) AS mounts"
            ).single(strict=True)
            canonical = transaction.run(
                "MATCH (e:Enterprise {enterprise_id: $id}) RETURN e.enterprise_name AS name",
                id=NEW_ENTERPRISE_ID,
            ).single(strict=True)
            if counts["enterprises"] != EXPECTED_PG_AFTER or counts["mounts"] != EXPECTED_MOUNTS:
                raise RuntimeError(f"Neo4j 事务内删除后计数异常：{dict(counts)}")
            if canonical["name"] != NEW_NAME:
                raise RuntimeError("Neo4j 新企业在事务内异常")
            transaction.commit()
        except Exception:
            transaction.rollback()
            raise


def restore_old_neo4j(driver: Any, state: dict[str, Any]) -> None:
    old = next(
        row for row in state["neo"]["enterprises"] if row["enterprise_id"] == OLD_ENTERPRISE_ID
    )
    with driver.session() as session:
        session.run("CREATE (e:Enterprise) SET e = $properties", properties=old["properties"]).consume()


def verify(args: argparse.Namespace, state: dict[str, Any]) -> dict[str, Any]:
    connection = psycopg2.connect(args.dsn)
    try:
        connection.autocommit = False
        current_pg = pg_snapshot(connection)
        connection.rollback()
    finally:
        connection.close()
    expected_pg = [row for row in state["pg_rows"] if row["id"] != OLD_ID]
    if current_pg != expected_pg:
        raise RuntimeError("PostgreSQL 删除后快照不等于删除前快照减旧行")

    driver = GraphDatabase.driver(
        args.neo4j_uri, auth=(args.neo4j_user, args.neo4j_password)
    )
    try:
        current_neo = neo4j_snapshot(driver)
    finally:
        driver.close()
    expected_enterprises = [
        row for row in state["neo"]["enterprises"] if row["enterprise_id"] != OLD_ENTERPRISE_ID
    ]
    if current_neo["enterprises"] != expected_enterprises:
        raise RuntimeError("Neo4j 删除后企业属性快照不等于删除前快照减旧节点")
    if current_neo["enterprise_relationships"] != state["neo"]["enterprise_relationships"]:
        raise RuntimeError("Neo4j 企业关系发生变化")
    if current_neo["counts"] != {"enterprises": EXPECTED_PG_AFTER, "mounts": EXPECTED_MOUNTS}:
        raise RuntimeError(f"Neo4j 最终计数异常：{current_neo['counts']}")
    return {
        "postgres_companies": len(current_pg),
        "neo4j_enterprises": current_neo["counts"]["enterprises"],
        "neo4j_mounts": current_neo["counts"]["mounts"],
        "other_postgres_rows_changed": 0,
        "other_neo4j_nodes_changed": 0,
        "enterprise_relationships_changed": 0,
    }


def main() -> None:
    args = parse_args()
    state = preflight(args)
    preview = {
        "delete_postgres": {"id": OLD_ID, "name": OLD_NAME},
        "delete_neo4j": {"enterprise_id": OLD_ENTERPRISE_ID, "name": OLD_NAME},
        "retain": {"id": NEW_ID, "enterprise_id": NEW_ENTERPRISE_ID, "name": NEW_NAME},
        "old_relationships": 0,
    }
    print(json.dumps(preview, ensure_ascii=False, indent=2))
    if not args.apply:
        print("\n预检通过；未执行删除。使用 --apply 执行。")
        return

    run_id = "delete_renamed_company_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid4().hex[:8]
    backup_dir = create_backups(args, state, run_id)
    connection = psycopg2.connect(args.dsn)
    driver = GraphDatabase.driver(
        args.neo4j_uri, auth=(args.neo4j_user, args.neo4j_password)
    )
    neo_committed = False
    try:
        connection.autocommit = False
        delete_postgres(connection)
        delete_neo4j(driver)
        neo_committed = True
        connection.commit()
    except Exception:
        connection.rollback()
        if neo_committed:
            restore_old_neo4j(driver, state)
        raise
    finally:
        connection.close()
        driver.close()

    verification = verify(args, state)
    result = {
        **preview,
        "run_id": run_id,
        "backup_dir": str(backup_dir),
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
