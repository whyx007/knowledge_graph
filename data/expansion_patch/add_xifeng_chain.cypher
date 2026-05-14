MATCH (e:Enterprise {id:'ENT_B881DA0DA218'})
MATCH (sub:SubTrack {id:'SUB_005'})
MATCH (st1:ChainStage {id:'STG_005_003'})
MATCH (st2:ChainStage {id:'STG_005_004'})
MATCH (st3:ChainStage {id:'STG_005_007'})
MATCH (k1:KeyCapability {id:'KCAP_COMP_001'})
MATCH (k2:KeyCapability {id:'KCAP_COMP_002'})
MATCH (k3:KeyCapability {id:'KCAP_COMP_005'})
MERGE (e)-[rsub:FOCUSES_ON_SUB_TRACK]->(sub)
SET rsub.confidence=0.88, rsub.source='manual_mount_2026-05-12'
MERGE (e)-[rst1:LOCATED_IN_STAGE]->(st1)
SET rst1.confidence=0.86, rst1.source='manual_mount_2026-05-12'
MERGE (e)-[rst2:LOCATED_IN_STAGE]->(st2)
SET rst2.confidence=0.82, rst2.source='manual_mount_2026-05-12'
MERGE (e)-[rst3:LOCATED_IN_STAGE]->(st3)
SET rst3.confidence=0.78, rst3.source='manual_mount_2026-05-12'
MERGE (e)-[rk1:HAS_KEY_CAPABILITY]->(k1)
SET rk1.confidence=0.88, rk1.source='manual_mount_2026-05-12'
MERGE (e)-[rk2:HAS_KEY_CAPABILITY]->(k2)
SET rk2.confidence=0.84, rk2.source='manual_mount_2026-05-12'
MERGE (e)-[rk3:HAS_KEY_CAPABILITY]->(k3)
SET rk3.confidence=0.76, rk3.source='manual_mount_2026-05-12';
