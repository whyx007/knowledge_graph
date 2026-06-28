MATCH (e:Enterprise {id:'ENT_203143C4EA39'})
MATCH (s:SubTrack {id:'SUB_005'})
MATCH (st1:ChainStage {id:'STG_005_003'})
MATCH (st2:ChainStage {id:'STG_005_004'})
MATCH (k1:KeyCapability {id:'KCAP_COMP_001'})
MATCH (k2:KeyCapability {id:'KCAP_COMP_002'})
MERGE (e)-[r1:FOCUSES_ON_SUB_TRACK]->(s)
SET r1.confidence=0.78, r1.source='manual_expansion_patch_2026-05-12'
MERGE (e)-[r2:LOCATED_IN_STAGE]->(st1)
SET r2.confidence=0.76, r2.source='manual_expansion_patch_2026-05-12'
MERGE (e)-[r3:LOCATED_IN_STAGE]->(st2)
SET r3.confidence=0.72, r3.source='manual_expansion_patch_2026-05-12'
MERGE (e)-[r4:HAS_KEY_CAPABILITY]->(k1)
SET r4.confidence=0.78, r4.source='manual_expansion_patch_2026-05-12'
MERGE (e)-[r5:HAS_KEY_CAPABILITY]->(k2)
SET r5.confidence=0.72, r5.source='manual_expansion_patch_2026-05-12';

MATCH (e2:Enterprise {id:'ENT_337B26DB83F2'})
MATCH (s2:SubTrack {id:'SUB_005'})
MATCH (st3:ChainStage {id:'STG_005_002'})
MATCH (st4:ChainStage {id:'STG_005_004'})
MATCH (k3:KeyCapability {id:'KCAP_COMP_001'})
MATCH (k4:KeyCapability {id:'KCAP_COMP_002'})
MERGE (e2)-[a1:FOCUSES_ON_SUB_TRACK]->(s2)
SET a1.confidence=0.74, a1.source='manual_expansion_patch_2026-05-12'
MERGE (e2)-[a2:LOCATED_IN_STAGE]->(st3)
SET a2.confidence=0.72, a2.source='manual_expansion_patch_2026-05-12'
MERGE (e2)-[a3:LOCATED_IN_STAGE]->(st4)
SET a3.confidence=0.70, a3.source='manual_expansion_patch_2026-05-12'
MERGE (e2)-[a4:HAS_KEY_CAPABILITY]->(k3)
SET a4.confidence=0.72, a4.source='manual_expansion_patch_2026-05-12'
MERGE (e2)-[a5:HAS_KEY_CAPABILITY]->(k4)
SET a5.confidence=0.70, a5.source='manual_expansion_patch_2026-05-12';
