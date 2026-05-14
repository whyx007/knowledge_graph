MATCH (e:Enterprise {id:'ENT_0EEE5F4580B9'})
MATCH (s:SubTrack {id:'SUB_006'})
MATCH (st1:ChainStage {id:'STG_006_003'})
MATCH (st2:ChainStage {id:'STG_006_004'})
MATCH (k1:KeyCapability {id:'KCAP_FUS_003'})
MATCH (k2:KeyCapability {id:'KCAP_FUS_005'})
MERGE (e)-[r1:FOCUSES_ON_SUB_TRACK]->(s)
SET r1.confidence=0.76, r1.source='manual_expansion_patch_2026-05-12'
MERGE (e)-[r2:LOCATED_IN_STAGE]->(st1)
SET r2.confidence=0.74, r2.source='manual_expansion_patch_2026-05-12'
MERGE (e)-[r3:LOCATED_IN_STAGE]->(st2)
SET r3.confidence=0.72, r3.source='manual_expansion_patch_2026-05-12'
MERGE (e)-[r4:HAS_KEY_CAPABILITY]->(k1)
SET r4.confidence=0.74, r4.source='manual_expansion_patch_2026-05-12'
MERGE (e)-[r5:HAS_KEY_CAPABILITY]->(k2)
SET r5.confidence=0.72, r5.source='manual_expansion_patch_2026-05-12';
