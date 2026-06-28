#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

: "${PGHOST:=127.0.0.1}"
: "${PGPORT:=5432}"
: "${PGDATABASE:=ceo_brief}"
: "${PGUSER:=postgres}"

psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" \
  -f "$ROOT_DIR/sql/postgres_extract_views.sql"

psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" \
  -c "\\copy (
    SELECT
      enterprise_id,
      enterprise_name,
      source_system,
      source_pk,
      last_sync_at
    FROM kg_v2_enterprises
    ORDER BY source_pk::integer
  ) TO '$ROOT_DIR/data/staging/enterprises.csv' WITH CSV HEADER"

psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" \
  -c "\\copy (
    SELECT
      enterprise_id,
      source_pk,
      enterprise_name,
      domain,
      industry,
      scenario,
      evidence_text,
      source_field,
      source_system,
      extracted_at
    FROM kg_v2_enterprise_evidence
    ORDER BY source_pk::integer
  ) TO '$ROOT_DIR/data/staging/enterprise_evidence.csv' WITH CSV HEADER"

echo "Exported PostgreSQL staging CSV files."
