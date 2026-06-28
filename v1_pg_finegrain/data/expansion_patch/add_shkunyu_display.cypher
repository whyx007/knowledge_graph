MATCH (e:Enterprise {id:'ENT_7AB5E223A54E'})
MATCH (s:SubTrack {id:'SUB_004'})
MATCH (st1:ChainStage {id:'STG_004_004'})
MATCH (st2:ChainStage {id:'STG_004_008'})
MATCH (k1:KeyCapability {id:'KCAP_DISP_003'})
MATCH (k2:KeyCapability {id:'KCAP_DISP_005'})
MERGE (e)-[r1:FOCUSES_ON_SUB_TRACK]->(s)
SET r1.confidence=0.84, r1.source='manual_expansion_patch_2026-05-12'
MERGE (e)-[r2:LOCATED_IN_STAGE]->(st1)
SET r2.confidence=0.80, r2.source='manual_expansion_patch_2026-05-12'
MERGE (e)-[r3:LOCATED_IN_STAGE]->(st2)
SET r3.confidence=0.78, r3.source='manual_expansion_patch_2026-05-12'
MERGE (e)-[r4:HAS_KEY_CAPABILITY]->(k1)
SET r4.confidence=0.80, r4.source='manual_expansion_patch_2026-05-12'
MERGE (e)-[r5:HAS_KEY_CAPABILITY]->(k2)
SET r5.confidence=0.78, r5.source='manual_expansion_patch_2026-05-12';
