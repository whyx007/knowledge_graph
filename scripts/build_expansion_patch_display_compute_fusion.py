import json
from pathlib import Path
import pandas as pd

BASE = Path(r"C:\Users\XCKF\.openclaw\workspace-kg-prototype")
OUT = BASE / "data" / "expansion_patch"
OUT.mkdir(parents=True, exist_ok=True)

# =========================
# A. new subtracks
# =========================
subtracks = [
    {
        'domain_id': 'DOM_001',
        'domain_name': '光电子',
        'sub_track_id': 'SUB_004',
        'sub_track_name': '光显示',
        'sub_track_description': '围绕显示芯片、微显示、量子点显示材料、模组集成与终端应用的子赛道'
    },
    {
        'domain_id': 'DOM_001',
        'domain_name': '光电子',
        'sub_track_id': 'SUB_005',
        'sub_track_name': '光计算',
        'sub_track_description': '围绕光计算芯片、光交换互连、光电混合计算和系统级集成的子赛道'
    },
    {
        'domain_id': 'DOM_001',
        'domain_name': '光电子',
        'sub_track_id': 'SUB_006',
        'sub_track_name': '光融合（量子光学新原理）',
        'sub_track_description': '围绕量子光学新原理、光量子器件、融合感知与前沿系统平台的候选子赛道'
    },
]

stages = []

def add_stage(sub_id, sub_name, idx, name, level, category, up_id, down_id):
    stages.append({
        'stage_id': f"STG_{sub_id.split('_')[1]}_{idx:03d}",
        'sub_track_id': sub_id,
        'sub_track_name': sub_name,
        'stage_order': idx,
        'stage_name': name,
        'stage_level': level,
        'stage_category': category,
        'upstream_stage_id': up_id,
        'downstream_stage_id': down_id,
    })

# SUB_004 光显示
sd='SUB_004'; sn='光显示'
display_names = [
    ('显示材料/外延/衬底','上游','核心材料'),
    ('显示芯片','上游','核心器件'),
    ('背板/驱动/控制芯片','上游','驱动控制'),
    ('光学结构件与配套器件','上游','光学配套'),
    ('封装/键合/转移工艺','中游','关键工艺'),
    ('模组集成与校准','中游','模组集成'),
    ('显示整机与系统方案','中游','系统方案'),
    ('AR/VR微显示应用','下游','应用场景'),
    ('车载与高端显示应用','下游','应用场景'),
    ('大屏与专业显示应用','下游','应用场景'),
]
for i,(n,l,c) in enumerate(display_names, start=1):
    up = f'STG_004_{i-1:03d}' if i>1 else ''
    dn = f'STG_004_{i+1:03d}' if i<len(display_names) else ''
    add_stage(sd,sn,i,n,l,c,up,dn)

# SUB_005 光计算
sd='SUB_005'; sn='光计算'
compute_names = [
    ('光计算材料与工艺平台','上游','基础平台'),
    ('光计算核心器件','上游','核心器件'),
    ('光计算/光交换芯片','上游','核心芯片'),
    ('高速互连与封装模块','中游','互连封装'),
    ('板级/系统级集成','中游','系统集成'),
    ('光电混合计算平台','中游','平台系统'),
    ('AI集群与数据中心应用','下游','应用场景'),
    ('科学计算与专用算力应用','下游','应用场景'),
]
for i,(n,l,c) in enumerate(compute_names, start=1):
    up = f'STG_005_{i-1:03d}' if i>1 else ''
    dn = f'STG_005_{i+1:03d}' if i<len(compute_names) else ''
    add_stage(sd,sn,i,n,l,c,up,dn)

# SUB_006 光融合（量子光学新原理）
sd='SUB_006'; sn='光融合（量子光学新原理）'
fusion_names = [
    ('量子光学原理与核心材料','上游','原理/材料'),
    ('量子/超灵敏光学器件','上游','核心器件'),
    ('新原理成像/探测模组','中游','模组系统'),
    ('融合感知与控制平台','中游','平台系统'),
    ('科研平台与高端仪器应用','下游','应用场景'),
    ('特种感知与前沿产业应用','下游','应用场景'),
]
for i,(n,l,c) in enumerate(fusion_names, start=1):
    up = f'STG_006_{i-1:03d}' if i>1 else ''
    dn = f'STG_006_{i+1:03d}' if i<len(fusion_names) else ''
    add_stage(sd,sn,i,n,l,c,up,dn)

stages_df = pd.DataFrame(stages)

keycaps = [
    # 光显示
    ('KCAP_DISP_001','SUB_004','光显示','显示芯片设计能力','围绕显示芯片架构、像素设计与电路实现的能力'),
    ('KCAP_DISP_002','SUB_004','光显示','封装键合良率控制能力','围绕封装、键合、转移与良率稳定控制的能力'),
    ('KCAP_DISP_003','SUB_004','光显示','光学模组集成能力','围绕模组集成、校准与系统级整合的能力'),
    ('KCAP_DISP_004','SUB_004','光显示','显示系统方案交付能力','围绕显示整机、方案落地与客户交付的能力'),
    ('KCAP_DISP_005','SUB_004','光显示','微显示应用适配能力','围绕AR/VR、车载等微显示应用适配的能力'),
    # 光计算
    ('KCAP_COMP_001','SUB_005','光计算','光计算芯片架构设计能力','围绕光计算、光交换与片上架构设计的能力'),
    ('KCAP_COMP_002','SUB_005','光计算','高速光互连集成能力','围绕高速互连、封装耦合与链路集成的能力'),
    ('KCAP_COMP_003','SUB_005','光计算','光电混合系统协同能力','围绕光电混合计算系统协同设计与调优的能力'),
    ('KCAP_COMP_004','SUB_005','光计算','系统级算力平台交付能力','围绕板级、机柜级与平台级交付的能力'),
    ('KCAP_COMP_005','SUB_005','光计算','场景化算力适配能力','围绕AI集群、科学计算等场景适配的能力'),
    # 光融合
    ('KCAP_FUS_001','SUB_006','光融合（量子光学新原理）','量子光学原理实现能力','围绕量子光学新原理验证与实现的能力'),
    ('KCAP_FUS_002','SUB_006','光融合（量子光学新原理）','超灵敏光学探测能力','围绕弱光、单光子、超灵敏探测实现的能力'),
    ('KCAP_FUS_003','SUB_006','光融合（量子光学新原理）','新原理成像系统集成能力','围绕新原理成像/探测模组与系统集成的能力'),
    ('KCAP_FUS_004','SUB_006','光融合（量子光学新原理）','科研平台产品化能力','围绕科研平台、高端仪器工程化与产品化的能力'),
    ('KCAP_FUS_005','SUB_006','光融合（量子光学新原理）','前沿场景验证能力','围绕特种感知与前沿产业应用验证的能力'),
]
keycaps_df = pd.DataFrame(keycaps, columns=['capability_id','sub_track_id','sub_track_name','capability_name','description'])

appscn = [
    ('ASCN_DISP_001','SUB_004','光显示','AR/VR微显示','AR/VR和可穿戴微显示场景'),
    ('ASCN_DISP_002','SUB_004','光显示','车载与座舱显示','车载抬显与高端座舱显示场景'),
    ('ASCN_DISP_003','SUB_004','光显示','专业与大屏显示','大屏、指挥调度与专业显示场景'),
    ('ASCN_COMP_001','SUB_005','光计算','AI集群与数据中心','AI训练推理集群与数据中心场景'),
    ('ASCN_COMP_002','SUB_005','光计算','科学计算与专用算力','科研计算和专用算力场景'),
    ('ASCN_FUS_001','SUB_006','光融合（量子光学新原理）','科研平台与高端仪器','科研平台、高端仪器装备场景'),
    ('ASCN_FUS_002','SUB_006','光融合（量子光学新原理）','特种感知与前沿应用','特种感知与前沿产业验证场景'),
]
appscn_df = pd.DataFrame(appscn, columns=['scenario_id','sub_track_id','sub_track_name','scenario_name','description'])

# relations
sub_to_stage = []
stage_to_stage = []
stage_to_keycap = []
app_to_stage = []

for _, r in stages_df.iterrows():
    sub_to_stage.append({'start_id':r['sub_track_id'],'end_id':r['stage_id'],'confidence':1.0,'source':'expansion_patch_2026-05-12'})
    if str(r['upstream_stage_id']).strip():
        stage_to_stage.append({'start_id':r['upstream_stage_id'],'end_id':r['stage_id'],'confidence':1.0,'source':'expansion_patch_2026-05-12'})

# stage -> key capability mappings
map_stage_caps = {
    'SUB_004': {
        '显示材料/外延/衬底':['KCAP_DISP_001'],
        '显示芯片':['KCAP_DISP_001'],
        '背板/驱动/控制芯片':['KCAP_DISP_001'],
        '光学结构件与配套器件':['KCAP_DISP_003'],
        '封装/键合/转移工艺':['KCAP_DISP_002'],
        '模组集成与校准':['KCAP_DISP_003'],
        '显示整机与系统方案':['KCAP_DISP_004'],
        'AR/VR微显示应用':['KCAP_DISP_005'],
        '车载与高端显示应用':['KCAP_DISP_005'],
        '大屏与专业显示应用':['KCAP_DISP_004'],
    },
    'SUB_005': {
        '光计算材料与工艺平台':['KCAP_COMP_001'],
        '光计算核心器件':['KCAP_COMP_001'],
        '光计算/光交换芯片':['KCAP_COMP_001'],
        '高速互连与封装模块':['KCAP_COMP_002'],
        '板级/系统级集成':['KCAP_COMP_003','KCAP_COMP_004'],
        '光电混合计算平台':['KCAP_COMP_003'],
        'AI集群与数据中心应用':['KCAP_COMP_005'],
        '科学计算与专用算力应用':['KCAP_COMP_005'],
    },
    'SUB_006': {
        '量子光学原理与核心材料':['KCAP_FUS_001'],
        '量子/超灵敏光学器件':['KCAP_FUS_002'],
        '新原理成像/探测模组':['KCAP_FUS_003'],
        '融合感知与控制平台':['KCAP_FUS_003','KCAP_FUS_004'],
        '科研平台与高端仪器应用':['KCAP_FUS_004'],
        '特种感知与前沿产业应用':['KCAP_FUS_005'],
    }
}
for _, r in stages_df.iterrows():
    caps = map_stage_caps.get(r['sub_track_id'], {}).get(r['stage_name'], [])
    for cap in caps:
        stage_to_keycap.append({'start_id':r['stage_id'],'end_id':cap,'confidence':0.95,'source':'expansion_patch_2026-05-12'})

# app scenario mappings
app_map = {
    'ASCN_DISP_001':['AR/VR微显示应用'],
    'ASCN_DISP_002':['车载与高端显示应用'],
    'ASCN_DISP_003':['大屏与专业显示应用'],
    'ASCN_COMP_001':['AI集群与数据中心应用'],
    'ASCN_COMP_002':['科学计算与专用算力应用'],
    'ASCN_FUS_001':['科研平台与高端仪器应用'],
    'ASCN_FUS_002':['特种感知与前沿产业应用'],
}
name_to_stage = {r['stage_name']:r['stage_id'] for _, r in stages_df.iterrows()}
for _, a in appscn_df.iterrows():
    for st in app_map.get(a['scenario_id'], []):
        app_to_stage.append({'start_id':a['scenario_id'],'end_id':name_to_stage[st],'confidence':0.95,'source':'expansion_patch_2026-05-12'})

sub_df = pd.DataFrame(subtracks)
sub_df.to_csv(OUT/'expansion_subtracks.csv', index=False, encoding='utf-8-sig')
stages_df.to_csv(OUT/'expansion_chain_stages.csv', index=False, encoding='utf-8-sig')
keycaps_df.to_csv(OUT/'expansion_key_capabilities.csv', index=False, encoding='utf-8-sig')
appscn_df.to_csv(OUT/'expansion_application_scenarios.csv', index=False, encoding='utf-8-sig')
pd.DataFrame(sub_to_stage).to_csv(OUT/'expansion_rel_subtrack_to_stage.csv', index=False, encoding='utf-8-sig')
pd.DataFrame(stage_to_stage).to_csv(OUT/'expansion_rel_stage_to_stage.csv', index=False, encoding='utf-8-sig')
pd.DataFrame(stage_to_keycap).to_csv(OUT/'expansion_rel_stage_to_keycapability.csv', index=False, encoding='utf-8-sig')
pd.DataFrame(app_to_stage).to_csv(OUT/'expansion_rel_appscenario_to_stage.csv', index=False, encoding='utf-8-sig')

cypher = """// expansion patch: 光显示 / 光计算 / 光融合（量子光学新原理）\nLOAD CSV WITH HEADERS FROM 'file:///expansion_subtracks.csv' AS row\nMERGE (d:IndustryDomain {id: row.domain_id})\n  ON CREATE SET d.name = row.domain_name\nMERGE (s:SubTrack {id: row.sub_track_id})\nSET s.name = row.sub_track_name,\n    s.description = row.sub_track_description\nMERGE (d)-[:HAS_SUB_TRACK]->(s);\n\nLOAD CSV WITH HEADERS FROM 'file:///expansion_chain_stages.csv' AS row\nMERGE (s:SubTrack {id: row.sub_track_id})\nMERGE (c:ChainStage {id: row.stage_id})\nSET c.name = row.stage_name,\n    c.stage_order = toInteger(row.stage_order),\n    c.stage_level = row.stage_level,\n    c.stage_category = row.stage_category,\n    c.sub_track_id = row.sub_track_id;\n\nLOAD CSV WITH HEADERS FROM 'file:///expansion_key_capabilities.csv' AS row\nMERGE (s:SubTrack {id: row.sub_track_id})\nMERGE (k:KeyCapability {id: row.capability_id})\nSET k.name = row.capability_name,\n    k.description = row.description,\n    k.sub_track_id = row.sub_track_id;\n\nLOAD CSV WITH HEADERS FROM 'file:///expansion_application_scenarios.csv' AS row\nMERGE (s:SubTrack {id: row.sub_track_id})\nMERGE (a:ApplicationScenario {id: row.scenario_id})\nSET a.name = row.scenario_name,\n    a.description = row.description,\n    a.sub_track_id = row.sub_track_id;\n\nLOAD CSV WITH HEADERS FROM 'file:///expansion_rel_subtrack_to_stage.csv' AS row\nMATCH (a:SubTrack {id: row.start_id})\nMATCH (b:ChainStage {id: row.end_id})\nMERGE (a)-[r:HAS_STAGE]->(b)\nSET r.confidence = toFloat(row.confidence), r.source = row.source;\n\nLOAD CSV WITH HEADERS FROM 'file:///expansion_rel_stage_to_stage.csv' AS row\nMATCH (a:ChainStage {id: row.start_id})\nMATCH (b:ChainStage {id: row.end_id})\nMERGE (a)-[r:UPSTREAM_OF]->(b)\nSET r.confidence = toFloat(row.confidence), r.source = row.source;\n\nLOAD CSV WITH HEADERS FROM 'file:///expansion_rel_stage_to_keycapability.csv' AS row\nMATCH (a:ChainStage {id: row.start_id})\nMATCH (b:KeyCapability {id: row.end_id})\nMERGE (a)-[r:REQUIRES_CAPABILITY]->(b)\nSET r.confidence = toFloat(row.confidence), r.source = row.source;\n\nLOAD CSV WITH HEADERS FROM 'file:///expansion_rel_appscenario_to_stage.csv' AS row\nMATCH (a:ApplicationScenario {id: row.start_id})\nMATCH (b:ChainStage {id: row.end_id})\nMERGE (a)-[r:DRIVES_STAGE]->(b)\nSET r.confidence = toFloat(row.confidence), r.source = row.source;\n"""
(OUT/'import_expansion_patch.cypher').write_text(cypher, encoding='utf-8')
summary = {
    'subtracks_added': int(len(sub_df)),
    'stages_added': int(len(stages_df)),
    'key_capabilities_added': int(len(keycaps_df)),
    'application_scenarios_added': int(len(appscn_df)),
    'subtrack_stage_relations': int(len(sub_to_stage)),
    'stage_stage_relations': int(len(stage_to_stage)),
    'stage_keycap_relations': int(len(stage_to_keycap)),
    'app_stage_relations': int(len(app_to_stage)),
}
(OUT/'expansion_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(summary, ensure_ascii=False))
