MATCH (e:Enterprise {id:'ENT_DD4B0C1ED421'})
MATCH (st:ChainStage {id:'STG_LA_002'})
MATCH (k:KeyCapability {id:'KCAP_LA_002'})
MERGE (e)-[r2:LOCATED_IN_STAGE]->(st)
SET r2.confidence=0.86, r2.source='manual_mount_2026-05-12'
MERGE (e)-[r3:HAS_KEY_CAPABILITY]->(k)
SET r3.confidence=0.80, r3.source='manual_mount_2026-05-12';
