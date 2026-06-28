MATCH (e:Enterprise {id:'ENT_DD4B0C1ED421'})
MATCH (k:KeyCapability {id:'KCAP_LA_002'})
MERGE (e)-[r3:HAS_KEY_CAPABILITY]->(k)
SET r3.confidence=0.80, r3.source='manual_mount_2026-05-12';
