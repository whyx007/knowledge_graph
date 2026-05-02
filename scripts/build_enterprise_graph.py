import argparse
import hashlib
import json
import re
from pathlib import Path

import pandas as pd


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def norm_text(value) -> str:
    if value is None:
        return ""
    if pd.isna(value):
        return ""
    text = str(value).strip()
    return text


def collapse_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


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


def clean_value(text: str, strip_tokens: list[str], collapse_whitespace: bool) -> str:
    value = norm_text(text)
    if collapse_whitespace:
        value = collapse_ws(value)
    if value in strip_tokens:
        return ""
    return value


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def build_graph(df: pd.DataFrame, config: dict, source_name: str):
    delimiters = config['source'].get('default_delimiters', [])
    strip_tokens = set(config.get('normalization', {}).get('strip_tokens', []))
    collapse_whitespace = bool(config.get('normalization', {}).get('collapse_whitespace', True))
    dedup_values = bool(config.get('normalization', {}).get('deduplicate_values', True))

    enterprise_cfg = config['enterprise']
    name_field = enterprise_cfg['name_field']
    property_map = enterprise_cfg.get('properties', {})
    relations_cfg = config.get('relations', [])
    ent_prefix = config['source'].get('enterprise_id_prefix', 'ENT')

    enterprise_rows = []
    entity_rows = {}
    relationship_rows = []

    for idx, row in df.iterrows():
        row_no = idx + 2
        enterprise_name = clean_value(row.get(name_field, ''), list(strip_tokens), collapse_whitespace)
        if not enterprise_name:
            continue

        enterprise_id = slug_id(ent_prefix, 'Enterprise', enterprise_name)
        ent = {
            'id': enterprise_id,
            'label': 'Enterprise',
            'name': enterprise_name,
            'source_file': source_name,
            'row_no': row_no,
        }

        for prop_name, field_name in property_map.items():
            ent[prop_name] = clean_value(row.get(field_name, ''), list(strip_tokens), collapse_whitespace)

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
                        'id': target_id,
                        'label': target_label,
                        'name': value,
                        'normalized_name': collapse_ws(value).lower(),
                        'source_file': source_name,
                    }

                relationship_rows.append({
                    'from_id': enterprise_id,
                    'from_label': 'Enterprise',
                    'relation_type': relation_type,
                    'to_id': target_id,
                    'to_label': target_label,
                    'raw_value': value,
                    'source_file': source_name,
                    'row_no': row_no,
                })

    enterprise_df = pd.DataFrame(enterprise_rows).drop_duplicates(subset=['id'])
    entity_df = pd.DataFrame(entity_rows.values()).drop_duplicates(subset=['id'])
    relationship_df = pd.DataFrame(relationship_rows).drop_duplicates(
        subset=['from_id', 'relation_type', 'to_id']
    )

    return enterprise_df, entity_df, relationship_df


def write_outputs(out_dir: Path, enterprise_df: pd.DataFrame, entity_df: pd.DataFrame, relationship_df: pd.DataFrame):
    processed_dir = out_dir / 'processed'
    neo4j_dir = out_dir / 'neo4j'
    ensure_dir(processed_dir)
    ensure_dir(neo4j_dir)

    enterprise_df.to_csv(processed_dir / 'enterprise_nodes.csv', index=False, encoding='utf-8-sig')
    entity_df.to_csv(processed_dir / 'entity_nodes.csv', index=False, encoding='utf-8-sig')
    relationship_df.to_csv(processed_dir / 'relationships.csv', index=False, encoding='utf-8-sig')

    enterprise_neo = enterprise_df.copy()
    enterprise_neo[':LABEL'] = 'Enterprise'
    enterprise_neo.rename(columns={'id': 'id:ID', 'name': 'name'}, inplace=True)
    enterprise_neo.to_csv(neo4j_dir / 'neo4j_enterprise_nodes.csv', index=False, encoding='utf-8-sig')

    entity_neo = entity_df.copy()
    entity_neo[':LABEL'] = entity_neo['label']
    entity_neo.rename(columns={'id': 'id:ID', 'name': 'name'}, inplace=True)
    entity_neo.to_csv(neo4j_dir / 'neo4j_entity_nodes.csv', index=False, encoding='utf-8-sig')

    rel_neo = relationship_df.copy()
    rel_neo.rename(columns={'from_id': ':START_ID', 'to_id': ':END_ID', 'relation_type': ':TYPE'}, inplace=True)
    rel_neo.to_csv(neo4j_dir / 'neo4j_relationships.csv', index=False, encoding='utf-8-sig')


def main():
    parser = argparse.ArgumentParser(description='Build enterprise graph files from Excel/CSV for Neo4j.')
    parser.add_argument('--config', required=True, help='Path to field mapping JSON config')
    parser.add_argument('--input', required=True, help='Path to source Excel or CSV file')
    parser.add_argument('--outdir', default='data', help='Output root directory')
    parser.add_argument('--sheet', default=None, help='Excel sheet name or index override')
    args = parser.parse_args()

    config_path = Path(args.config)
    input_path = Path(args.input)
    out_dir = Path(args.outdir)

    config = load_config(config_path)

    if input_path.suffix.lower() in ['.xlsx', '.xls']:
        sheet = args.sheet if args.sheet is not None else config.get('source', {}).get('sheet', 0)
        df = pd.read_excel(input_path, sheet_name=sheet)
    else:
        df = pd.read_csv(input_path)

    enterprise_df, entity_df, relationship_df = build_graph(df, config, input_path.name)
    write_outputs(out_dir, enterprise_df, entity_df, relationship_df)

    print(json.dumps({
        'enterprise_count': int(len(enterprise_df)),
        'entity_count': int(len(entity_df)),
        'relationship_count': int(len(relationship_df)),
        'output_root': str(out_dir)
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
