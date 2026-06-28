#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMPORT_DIR="$ROOT_DIR/neo4j/import"

mkdir -p "$IMPORT_DIR"

cp "$ROOT_DIR/data/mappings/chain_master.csv" "$IMPORT_DIR/"
cp "$ROOT_DIR/data/mappings/chain_segments.csv" "$IMPORT_DIR/"
cp "$ROOT_DIR/data/mappings/chain_stages.csv" "$IMPORT_DIR/"
cp "$ROOT_DIR/data/mappings/chain_substages.csv" "$IMPORT_DIR/"
cp "$ROOT_DIR/data/mappings/substage_to_substage.csv" "$IMPORT_DIR/"
cp "$ROOT_DIR/data/staging/enterprises.csv" "$IMPORT_DIR/"
cp "$ROOT_DIR/data/staging/enterprise_to_substage.csv" "$IMPORT_DIR/"

chmod -R a+rX "$IMPORT_DIR"

echo "Prepared Neo4j import CSV files in $IMPORT_DIR."
