MATCH (e:Enterprise {id:'ENT_6415559C2721'})
MATCH (s:SubTrack {id:'SUB_001'})
MATCH (st1:ChainStage {id:'STG_MV_003'})
MATCH (st2:ChainStage {id:'STG_MV_007'})
MATCH (k1:KeyCapability {id:'KCAP_MV_001'})
MATCH (k2:KeyCapability {id:'KCAP_MV_002'})
MERGE (e)-[r1:FOCUSES_ON_SUB_TRACK]->(s)
SET r1.confidence=0.90, r1.source='manual_mount_2026-05-12'
MERGE (e)-[r2:LOCATED_IN_STAGE]->(st1)
SET r2.confidence=0.88, r2.source='manual_mount_2026-05-12'
MERGE (e)-[r3:LOCATED_IN_STAGE]->(st2)
SET r3.confidence=0.84, r3.source='manual_mount_2026-05-12'
MERGE (e)-[r4:HAS_KEY_CAPABILITY]->(k1)
SET r4.confidence=0.88, r4.source='manual_mount_2026-05-12'
MERGE (e)-[r5:HAS_KEY_CAPABILITY]->(k2)
SET r5.confidence=0.86, r5.source='manual_mount_2026-05-12';
