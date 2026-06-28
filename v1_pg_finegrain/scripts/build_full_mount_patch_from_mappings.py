import csv
import json
import re
from pathlib import Path

import pandas as pd

BASE = Path(r"C:\Users\XCKF\.openclaw\workspace-kg-prototype")
OUT = BASE / "data" / "mount_patch"
OUT.mkdir(parents=True, exist_ok=True)


def clean_name(s: str) -> str:
    s = "" if s is None else str(s)
    s = re.sub(r"[（(].*?人工核对.*?[)）]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def split_pipe(text: str):
    text = "" if text is None else str(text).strip()
    if not text:
        return []
    return [x.strip() for x in text.split("|") if x.strip()]


def read_loose_csv(path: Path, kind: str):
    rows = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        for raw in reader:
            if not raw or not any(x.strip() for x in raw):
                continue
            if kind == "subtrack":
                # 9 cols: 0..3 fixed, judgement middle, then confidence/manual/review_notes/reviewer tail(4)
                if len(raw) < 9:
                    continue
                rows.append({
                    "enterprise_id": raw[0].strip(),
                    "enterprise_name": raw[1].strip(),
                    "main_sub_track": raw[2].strip(),
                    "secondary_sub_tracks": raw[3].strip(),
                    "judgement_basis": ",".join(raw[4:-4]).strip(),
                    "confidence": raw[-4].strip(),
                    "manual_review_status": raw[-3].strip(),
                    "review_notes": raw[-2].strip(),
                    "reviewer": raw[-1].strip(),
                })
            elif kind == "stage":
                # 11 cols: 0..5 fixed, judgement middle, then confidence/manual/review_notes/reviewer tail(4)
                if len(raw) < 11:
                    continue
                rows.append({
                    "enterprise_id": raw[0].strip(),
                    "enterprise_name": raw[1].strip(),
                    "sub_track_name": raw[2].strip(),
                    "main_stage": raw[3].strip(),
                    "secondary_stages": raw[4].strip(),
                    "stage_type": raw[5].strip(),
                    "judgement_basis": ",".join(raw[6:-4]).strip(),
                    "confidence": raw[-4].strip(),
                    "manual_review_status": raw[-3].strip(),
                    "review_notes": raw[-2].strip(),
                    "reviewer": raw[-1].strip(),
                })
            elif kind == "cap":
                # 12 cols: 0..5 fixed, mapping_basis middle, then has_delivery/conf/manual/review_notes/reviewer tail(5)
                if len(raw) < 12:
                    continue
                rows.append({
                    "enterprise_id": raw[0].strip(),
                    "enterprise_name": raw[1].strip(),
                    "raw_capability_text": raw[2].strip(),
                    "mapped_key_capability": raw[3].strip(),
                    "sub_track_name": raw[4].strip(),
                    "stage_name": raw[5].strip(),
                    "mapping_basis": ",".join(raw[6:-5]).strip(),
                    "has_delivery_evidence": raw[-5].strip(),
                    "confidence": raw[-4].strip(),
                    "manual_review_status": raw[-3].strip(),
                    "review_notes": raw[-2].strip(),
                    "reviewer": raw[-1].strip(),
                })
    return pd.DataFrame(rows)


sub = read_loose_csv(BASE / "data" / "mappings" / "企业-子赛道映射表.csv", "subtrack")
stage = read_loose_csv(BASE / "data" / "mappings" / "企业-产业链环节映射表.csv", "stage")
cap = read_loose_csv(BASE / "data" / "mappings" / "企业能力-关键能力映射表.csv", "cap")

ent_map = pd.read_csv(BASE / "data" / "mappings" / "unified_enterprise_id_mapping.csv")
ents = pd.read_csv(BASE / "data" / "neo4j" / "neo4j_enterprise_nodes.csv")
subtracks = pd.read_csv(BASE / "data" / "mappings" / "unified_subtracks.csv")
stages = pd.read_csv(BASE / "data" / "mappings" / "unified_chain_stages.csv")
keycaps = pd.read_csv(BASE / "data" / "mappings" / "unified_key_capabilities.csv")

# enterprise id lookup: E### -> legacy ENT_xxx
ent_id_map = {str(r.unified_enterprise_id).strip(): str(r.legacy_enterprise_id).strip() for _, r in ent_map.iterrows()}
# normalize fallback by name
legacy_by_clean_name = {clean_name(r['name']): r['id:ID'] for _, r in ents.iterrows()}

subtrack_id_by_name = {str(r.sub_track_name).strip(): str(r.sub_track_id).strip() for _, r in subtracks.iterrows()}
stage_id_by_key = {(str(r.sub_track_name).strip(), str(r.stage_name).strip()): str(r.stage_id).strip() for _, r in stages.iterrows()}
keycap_id_by_key = {(str(r.sub_track_name).strip(), str(r.capability_name).strip()): str(r.capability_id).strip() for _, r in keycaps.iterrows()}


def resolve_legacy_id(enterprise_id: str, enterprise_name: str):
    legacy = ent_id_map.get(str(enterprise_id).strip())
    if legacy:
        return legacy
    return legacy_by_clean_name.get(clean_name(enterprise_name), "")

# confirmed only
sub_c = sub[sub["manual_review_status"] == "已确认"].copy()
stage_c = stage[stage["manual_review_status"] == "已确认"].copy()
cap_c = cap[cap["manual_review_status"] == "已确认"].copy()

sub_rows = []
for _, r in sub_c.iterrows():
    legacy_id = resolve_legacy_id(r["enterprise_id"], r["enterprise_name"])
    if not legacy_id:
        continue
    names = [r["main_sub_track"]] + split_pipe(r.get("secondary_sub_tracks", ""))
    for name in names:
        sid = subtrack_id_by_name.get(name)
        if not sid:
            continue
        sub_rows.append({
            "start_id": legacy_id,
            "end_id": sid,
            "confidence": r.get("confidence", ""),
            "source": "企业-子赛道映射表.csv",
            "enterprise_name": clean_name(r["enterprise_name"]),
            "sub_track_name": name,
        })

stage_rows = []
for _, r in stage_c.iterrows():
    legacy_id = resolve_legacy_id(r["enterprise_id"], r["enterprise_name"])
    if not legacy_id:
        continue
    main_sub = str(r["sub_track_name"]).strip()
    stage_names = []
    if str(r.get("main_stage", "")).strip():
        stage_names.append((main_sub, str(r["main_stage"]).strip()))
    for item in split_pipe(r.get("secondary_stages", "")):
        if ":" in item:
            sub_name, stage_name = item.split(":", 1)
            stage_names.append((sub_name.strip(), stage_name.strip()))
        else:
            stage_names.append((main_sub, item.strip()))
    for sub_name, stage_name in stage_names:
        stid = stage_id_by_key.get((sub_name, stage_name))
        if not stid:
            continue
        stage_rows.append({
            "start_id": legacy_id,
            "end_id": stid,
            "confidence": r.get("confidence", ""),
            "source": "企业-产业链环节映射表.csv",
            "enterprise_name": clean_name(r["enterprise_name"]),
            "sub_track_name": sub_name,
            "stage_name": stage_name,
        })

cap_rows = []
for _, r in cap_c.iterrows():
    legacy_id = resolve_legacy_id(r["enterprise_id"], r["enterprise_name"])
    if not legacy_id:
        continue
    key = (str(r["sub_track_name"]).strip(), str(r["mapped_key_capability"]).strip())
    kid = keycap_id_by_key.get(key)
    if not kid:
        continue
    cap_rows.append({
        "start_id": legacy_id,
        "end_id": kid,
        "confidence": r.get("confidence", ""),
        "source": "企业能力-关键能力映射表.csv",
        "enterprise_name": clean_name(r["enterprise_name"]),
        "sub_track_name": key[0],
        "key_capability_name": key[1],
    })

sub_df = pd.DataFrame(sub_rows).drop_duplicates(["start_id", "end_id"])
stage_df = pd.DataFrame(stage_rows).drop_duplicates(["start_id", "end_id"])
cap_df = pd.DataFrame(cap_rows).drop_duplicates(["start_id", "end_id"])

sub_df.to_csv(OUT / "mount_rel_enterprise_to_subtrack_full.csv", index=False, encoding="utf-8-sig")
stage_df.to_csv(OUT / "mount_rel_enterprise_to_stage_full.csv", index=False, encoding="utf-8-sig")
cap_df.to_csv(OUT / "mount_rel_enterprise_to_keycapability_full.csv", index=False, encoding="utf-8-sig")

cypher = """// Full mount patch from confirmed enterprise mapping tables\nLOAD CSV WITH HEADERS FROM 'file:///mount_rel_enterprise_to_subtrack_full.csv' AS row\nMATCH (a:Enterprise {id: row.start_id})\nMATCH (b:SubTrack {id: row.end_id})\nMERGE (a)-[r:FOCUSES_ON_SUB_TRACK]->(b)\nSET r.confidence = toFloat(row.confidence),\n    r.source = row.source;\n\nLOAD CSV WITH HEADERS FROM 'file:///mount_rel_enterprise_to_stage_full.csv' AS row\nMATCH (a:Enterprise {id: row.start_id})\nMATCH (b:ChainStage {id: row.end_id})\nMERGE (a)-[r:LOCATED_IN_STAGE]->(b)\nSET r.confidence = toFloat(row.confidence),\n    r.source = row.source;\n\nLOAD CSV WITH HEADERS FROM 'file:///mount_rel_enterprise_to_keycapability_full.csv' AS row\nMATCH (a:Enterprise {id: row.start_id})\nMATCH (b:KeyCapability {id: row.end_id})\nMERGE (a)-[r:HAS_KEY_CAPABILITY]->(b)\nSET r.confidence = toFloat(row.confidence),\n    r.source = row.source;\n"""
(OUT / "import_full_mount_patch.cypher").write_text(cypher, encoding="utf-8")

summary = {
    "confirmed_enterprises_subtrack": int(sub_c["enterprise_id"].nunique()),
    "subtrack_relations": int(len(sub_df)),
    "stage_relations": int(len(stage_df)),
    "keycap_relations": int(len(cap_df)),
    "enterprises_in_patch": int(len(set(sub_df["enterprise_name"].tolist()) | set(stage_df["enterprise_name"].tolist()) | set(cap_df["enterprise_name"].tolist()))),
}
(OUT / "full_mount_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False))
