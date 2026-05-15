// Conservative cleanup: remove only old manual_mount_2026-05-12 relations that point to 光计算 (SUB_005)
// Safe target: keep mainline merged relations, keep candidate_space, keep non-compute cross-domain relations.

// Remove old compute subtrack relation
MATCH (:Enterprise)-[r:FOCUSES_ON_SUB_TRACK]->(:SubTrack {id:'SUB_005'})
WHERE r.source = 'manual_mount_2026-05-12'
DELETE r;

// Remove old compute stage relations
MATCH (:Enterprise)-[r:LOCATED_IN_STAGE]->(st:ChainStage)
WHERE r.source = 'manual_mount_2026-05-12'
  AND st.sub_track_id = 'SUB_005'
DELETE r;

// Remove old compute key capability relations
MATCH (:Enterprise)-[r:HAS_KEY_CAPABILITY]->(k:KeyCapability)
WHERE r.source = 'manual_mount_2026-05-12'
  AND k.sub_track_id = 'SUB_005'
DELETE r;

// Verify residual compute-old-mount relations
MATCH ()-[r]->(n)
WHERE r.source = 'manual_mount_2026-05-12'
  AND (
    (type(r)='FOCUSES_ON_SUB_TRACK' AND n.id='SUB_005') OR
    (type(r)='LOCATED_IN_STAGE' AND 'ChainStage' IN labels(n) AND n.sub_track_id='SUB_005') OR
    (type(r)='HAS_KEY_CAPABILITY' AND 'KeyCapability' IN labels(n) AND n.sub_track_id='SUB_005')
  )
RETURN type(r) AS rel_type, count(*) AS cnt;
