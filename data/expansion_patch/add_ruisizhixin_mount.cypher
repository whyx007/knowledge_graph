MATCH (e:Enterprise {id:'ENT_46E1C15BE614'})
MATCH (s:SubTrack {id:'SUB_001'})
MATCH (st:ChainStage {id:'STG_MV_003'})
MATCH (k:KeyCapability {id:'KCAP_MV_001'})
MERGE (e)-[r1:FOCUSES_ON_SUB_TRACK]->(s)
SET r1.confidence=0.88, r1.source='manual_mount_2026-05-12'
MERGE (e)-[r2:LOCATED_IN_STAGE]->(st)
SET r2.confidence=0.90, r2.source='manual_mount_2026-05-12'
MERGE (e)-[r3:HAS_KEY_CAPABILITY]->(k)
SET r3.confidence=0.84, r3.source='manual_mount_2026-05-12';
