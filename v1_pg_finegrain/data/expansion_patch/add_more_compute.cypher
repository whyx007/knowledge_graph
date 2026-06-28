MATCH (e:Enterprise {id:'ENT_337B26DB83F2'})
MATCH (s:SubTrack {id:'SUB_005'})
MATCH (st1:ChainStage {id:'STG_005_002'})
MATCH (st2:ChainStage {id:'STG_005_004'})
MATCH (k1:KeyCapability {id:'KCAP_COMP_001'})
MATCH (k2:KeyCapability {id:'KCAP_COMP_002'})
MERGE (e)-[r1:FOCUSES_ON_SUB_TRACK]->(s)
SET r1.confidence=0.74, r1.source='manual_expansion_patch_2026-05-12'
MERGE (e)-[r2:LOCATED_IN_STAGE]->(st1)
SET r2.confidence=0.72, r2.source='manual_expansion_patch_2026-05-12'
MERGE (e)-[r3:LOCATED_IN_STAGE]->(st2)
SET r3.confidence=0.70, r3.source='manual_expansion_patch_2026-05-12'
MERGE (e)-[r4:HAS_KEY_CAPABILITY]->(k1)
SET r4.confidence=0.72, r4.source='manual_expansion_patch_2026-05-12'
MERGE (e)-[r5:HAS_KEY_CAPABILITY]->(k2)
SET r5.confidence=0.70, r5.source='manual_expansion_patch_2026-05-12';

MATCH (e2:Enterprise {id:'ENT_69AA5BA59175'})
MATCH (s2:SubTrack {id:'SUB_005'})
MATCH (st3:ChainStage {id:'STG_005_001'})
MATCH (st4:ChainStage {id:'STG_005_004'})
MATCH (k3:KeyCapability {id:'KCAP_COMP_002'})
MERGE (e2)-[a1:FOCUSES_ON_SUB_TRACK]->(s2)
SET a1.confidence=0.68, a1.source='manual_expansion_patch_2026-05-12'
MERGE (e2)-[a2:LOCATED_IN_STAGE]->(st3)
SET a2.confidence=0.66, a2.source='manual_expansion_patch_2026-05-12'
MERGE (e2)-[a3:LOCATED_IN_STAGE]->(st4)
SET a3.confidence=0.64, a3.source='manual_expansion_patch_2026-05-12'
MERGE (e2)-[a4:HAS_KEY_CAPABILITY]->(k3)
SET a4.confidence=0.64, a4.source='manual_expansion_patch_2026-05-12';
