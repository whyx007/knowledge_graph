import hashlib
import json
import re
from pathlib import Path

import pandas as pd

WORKDIR = Path(r"C:\Users\XCKF\.openclaw\workspace-kg-prototype")
CONFIG_PATH = WORKDIR / "config" / "field_mapping.enterprise_xlsx.json"
INPUT_XLSX = WORKDIR / "data" / "company-info_with_url.xlsx"
BASE_ENTERPRISE = WORKDIR / "data" / "neo4j" / "neo4j_enterprise_nodes.csv"
BASE_ENTITY = WORKDIR / "data" / "neo4j" / "neo4j_entity_nodes.csv"
BASE_REL = WORKDIR / "data" / "neo4j" / "neo4j_relationships.csv"
OUTDIR = WORKDIR / "data" / "incremental"


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def norm_text(value) -> str:
    if value is None:
        return ""
    if pd.isna(value):
        return ""
    return str(value).strip()


def collapse_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def clean_company_name(text: str) -> str:
    text = norm_text(text)
    text = re.sub(r"[（(].*?(人工核对|官网|网站|URL|链接).*?[)）]", "", text)
    return collapse_ws(text)


def slug_id(prefix: str, label: str, name: str) -> str:
    base = f"{label}::{name}".encode("utf-8")
    digest = hashlib.md5(base).hexdigest()[:12].upper()
    return f"{prefix}_{digest}"


def split_multi_value(text: str, delimiters: list[str]) -> list[str]:
    if not text:
        return []
    pattern = "|".join(re.escape(d) for d in delimiters)
    parts = re.split(pattern, text)
    return [p.strip() for p in parts if p and p.strip()]


def clean_value(text, strip_tokens: list[str], collapse_whitespace: bool) -> str:
    value = norm_text(text)
    if collapse_whitespace:
        value = collapse_ws(value)
    if value in strip_tokens:
        return ""
    return value


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def build_incremental(df: pd.DataFrame, config: dict):
    delimiters = config['source'].get('default_delimiters', [])
    strip_tokens = set(config.get('normalization', {}).get('strip_tokens', []))
    collapse_whitespace = bool(config.get('normalization', {}).get('collapse_whitespace', True))
    dedup_values = bool(config.get('normalization', {}).get('deduplicate_values', True))
    enterprise_cfg = config['enterprise']
    name_field = enterprise_cfg['name_field']
    property_map = enterprise_cfg.get('properties', {})
    relations_cfg = config.get('relations', [])
    ent_prefix = config['source'].get('enterprise_id_prefix', 'ENT')

    existing_enterprise_df = pd.read_csv(BASE_ENTERPRISE)
    existing_names = {clean_company_name(x) for x in existing_enterprise_df['name'].dropna().tolist()}

    enterprise_rows = []
    entity_rows = {}
    relationship_rows = []
    skipped_existing = []

    for idx, row in df.iterrows():
        row_no = idx + 2
        raw_name = row.get(name_field, '')
        enterprise_name = clean_company_name(raw_name)
        if not enterprise_name:
            continue
        if enterprise_name in existing_names:
            skipped_existing.append(enterprise_name)
            continue

        enterprise_id = slug_id(ent_prefix, 'Enterprise', enterprise_name)
        ent = {
            'id:ID': enterprise_id,
            'label': 'Enterprise',
            'name': enterprise_name,
            'source_file': INPUT_XLSX.name,
            'row_no': row_no,
            ':LABEL': 'Enterprise',
        }

        for prop_name, field_name in property_map.items():
            ent[prop_name] = clean_value(row.get(field_name, ''), list(strip_tokens), collapse_whitespace)

        if '官网URL' in df.columns:
            ent['website_url'] = clean_value(row.get('官网URL', ''), list(strip_tokens), collapse_whitespace)

        enterprise_rows.append(ent)

        for rel_cfg in relations_cfg:
            field = rel_cfg['field']
            target_label = rel_cfg['target_label']
            relation_type = rel_cfg['relation_type']
            target_id_prefix = rel_cfg['target_id_prefix']

            raw = clean_value(row.get(field, ''), list(strip_tokens), collapse_whitespace)
            if not raw:
                continue

            values = split_multi_value(raw, delimiters)
            cleaned = []
            seen = set()
            for v in values:
                cv = clean_value(v, list(strip_tokens), collapse_whitespace)
                if not cv:
                    continue
                key = cv.lower()
                if dedup_values and key in seen:
                    continue
                seen.add(key)
                cleaned.append(cv)

            for value in cleaned:
                target_id = slug_id(target_id_prefix, target_label, value)
                entity_key = (target_id, target_label)
                if entity_key not in entity_rows:
                    entity_rows[entity_key] = {
                        'id:ID': target_id,
                        'label': target_label,
                        'name': value,
                        'normalized_name': collapse_ws(value).lower(),
                        'source_file': INPUT_XLSX.name,
                        ':LABEL': target_label,
                    }

                relationship_rows.append({
                    ':START_ID': enterprise_id,
                    'from_label': 'Enterprise',
                    ':TYPE': relation_type,
                    ':END_ID': target_id,
                    'to_label': target_label,
                    'raw_value': value,
                    'source_file': INPUT_XLSX.name,
                    'row_no': row_no,
                })

    inc_enterprise_df = pd.DataFrame(enterprise_rows)
    inc_entity_df = pd.DataFrame(entity_rows.values()) if entity_rows else pd.DataFrame(columns=['id:ID','label','name','normalized_name','source_file',':LABEL'])
    inc_rel_df = pd.DataFrame(relationship_rows) if relationship_rows else pd.DataFrame(columns=[':START_ID','from_label',':TYPE',':END_ID','to_label','raw_value','source_file','row_no'])

    existing_entity_ids = set(pd.read_csv(BASE_ENTITY)['id:ID'].dropna().tolist())
    existing_rel_df = pd.read_csv(BASE_REL)
    existing_rel_keys = set(zip(existing_rel_df[':START_ID'], existing_rel_df[':TYPE'], existing_rel_df[':END_ID']))

    if not inc_entity_df.empty:
        inc_entity_df = inc_entity_df[~inc_entity_df['id:ID'].isin(existing_entity_ids)].drop_duplicates(subset=['id:ID'])
    if not inc_rel_df.empty:
        rel_keys = list(zip(inc_rel_df[':START_ID'], inc_rel_df[':TYPE'], inc_rel_df[':END_ID']))
        inc_rel_df = inc_rel_df[[k not in existing_rel_keys for k in rel_keys]].drop_duplicates(subset=[':START_ID',':TYPE',':END_ID'])

    ensure_dir(OUTDIR)
    inc_enterprise_df.to_csv(OUTDIR / 'neo4j_enterprise_nodes_incremental.csv', index=False, encoding='utf-8-sig')
    inc_entity_df.to_csv(OUTDIR / 'neo4j_entity_nodes_incremental.csv', index=False, encoding='utf-8-sig')
    inc_rel_df.to_csv(OUTDIR / 'neo4j_relationships_incremental.csv', index=False, encoding='utf-8-sig')

    cypher = """// Incremental import for company-info_with_url.xlsx\n// 仅导入新增企业；已有企业不重复导入\n\nLOAD CSV WITH HEADERS FROM 'file:///neo4j_enterprise_nodes_incremental.csv' AS row\nMERGE (e:Enterprise {id: row.`id:ID`})\nSET e.name = row.name,\n    e.label = row.label,\n    e.source_file = row.source_file,\n    e.row_no = toInteger(row.row_no),\n    e.core_technology = row.core_technology,\n    e.technology_maturity = row.technology_maturity,\n    e.possible_scenarios = row.possible_scenarios,\n    e.business_model = row.business_model,\n    e.delivery_capability = row.delivery_capability,\n    e.certification_ip = row.certification_ip,\n    e.founder_team_and_gap = row.founder_team_and_gap,\n    e.recent_revenue_profit = row.recent_revenue_profit,\n    e.competition_and_diff = row.competition_and_diff,\n    e.match_level = row.match_level,\n    e.website_url = row.website_url;\n\nLOAD CSV WITH HEADERS FROM 'file:///neo4j_entity_nodes_incremental.csv' AS row\nCALL {\n  WITH row\n  FOREACH (_ IN CASE WHEN row.label = 'Product' THEN [1] ELSE [] END |\n    MERGE (n:Product {id: row.`id:ID`})\n    SET n.name = row.name, n.label = row.label, n.normalized_name = row.normalized_name, n.source_file = row.source_file\n  )\n  FOREACH (_ IN CASE WHEN row.label = 'Capability' THEN [1] ELSE [] END |\n    MERGE (n:Capability {id: row.`id:ID`})\n    SET n.name = row.name, n.label = row.label, n.normalized_name = row.normalized_name, n.source_file = row.source_file\n  )\n  FOREACH (_ IN CASE WHEN row.label = 'Industry' THEN [1] ELSE [] END |\n    MERGE (n:Industry {id: row.`id:ID`})\n    SET n.name = row.name, n.label = row.label, n.normalized_name = row.normalized_name, n.source_file = row.source_file\n  )\n  FOREACH (_ IN CASE WHEN row.label = 'Scenario' THEN [1] ELSE [] END |\n    MERGE (n:Scenario {id: row.`id:ID`})\n    SET n.name = row.name, n.label = row.label, n.normalized_name = row.normalized_name, n.source_file = row.source_file\n  )\n  FOREACH (_ IN CASE WHEN row.label = 'Customer' THEN [1] ELSE [] END |\n    MERGE (n:Customer {id: row.`id:ID`})\n    SET n.name = row.name, n.label = row.label, n.normalized_name = row.normalized_name, n.source_file = row.source_file\n  )\n  FOREACH (_ IN CASE WHEN row.label = 'Supplier' THEN [1] ELSE [] END |\n    MERGE (n:Supplier {id: row.`id:ID`})\n    SET n.name = row.name, n.label = row.label, n.normalized_name = row.normalized_name, n.source_file = row.source_file\n  )\n  FOREACH (_ IN CASE WHEN row.label = 'DemandTag' THEN [1] ELSE [] END |\n    MERGE (n:DemandTag {id: row.`id:ID`})\n    SET n.name = row.name, n.label = row.label, n.normalized_name = row.normalized_name, n.source_file = row.source_file\n  )\n  RETURN 1 AS done\n}\nRETURN count(*) AS imported_entities;\n\nLOAD CSV WITH HEADERS FROM 'file:///neo4j_relationships_incremental.csv' AS row\nMATCH (a {id: row.`:START_ID`})\nMATCH (b {id: row.`:END_ID`})\nCALL {\n  WITH row, a, b\n  FOREACH (_ IN CASE WHEN row.`:TYPE` = 'PROVIDES_PRODUCT' THEN [1] ELSE [] END | MERGE (a)-[:PROVIDES_PRODUCT]->(b))\n  FOREACH (_ IN CASE WHEN row.`:TYPE` = 'HAS_CAPABILITY' THEN [1] ELSE [] END | MERGE (a)-[:HAS_CAPABILITY]->(b))\n  FOREACH (_ IN CASE WHEN row.`:TYPE` = 'SERVES_INDUSTRY' THEN [1] ELSE [] END | MERGE (a)-[:SERVES_INDUSTRY]->(b))\n  FOREACH (_ IN CASE WHEN row.`:TYPE` = 'APPLIES_TO_SCENARIO' THEN [1] ELSE [] END | MERGE (a)-[:APPLIES_TO_SCENARIO]->(b))\n  FOREACH (_ IN CASE WHEN row.`:TYPE` = 'HAS_CUSTOMER' THEN [1] ELSE [] END | MERGE (a)-[:HAS_CUSTOMER]->(b))\n  FOREACH (_ IN CASE WHEN row.`:TYPE` = 'HAS_SUPPLIER' THEN [1] ELSE [] END | MERGE (a)-[:HAS_SUPPLIER]->(b))\n  FOREACH (_ IN CASE WHEN row.`:TYPE` = 'HAS_DEMAND' THEN [1] ELSE [] END | MERGE (a)-[:HAS_DEMAND]->(b))\n  RETURN 1 AS done\n}\nRETURN count(*) AS imported_relationships;\n"""
    (OUTDIR / 'import_incremental_company_info.cypher').write_text(cypher, encoding='utf-8')

    summary = {
        'input_rows': int(len(df)),
        'existing_enterprises': int(len(existing_names)),
        'incremental_enterprises': int(len(inc_enterprise_df)),
        'incremental_entities': int(len(inc_entity_df)),
        'incremental_relationships': int(len(inc_rel_df)),
        'skipped_existing_unique': int(len(set(skipped_existing))),
    }
    pd.DataFrame({'company_name': sorted(set(skipped_existing))}).to_csv(OUTDIR / 'skipped_existing_companies.csv', index=False, encoding='utf-8-sig')
    pd.DataFrame({'company_name': inc_enterprise_df['name'].tolist() if not inc_enterprise_df.empty else []}).to_csv(OUTDIR / 'incremental_companies.csv', index=False, encoding='utf-8-sig')
    (OUTDIR / 'incremental_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    config = load_config(CONFIG_PATH)
    df = pd.read_excel(INPUT_XLSX)
    build_incremental(df, config)
