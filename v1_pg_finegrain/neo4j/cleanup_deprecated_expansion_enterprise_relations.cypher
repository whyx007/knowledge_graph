// Cleanup deprecated expansion enterprise relations after mainline merge
// Run this once in Neo4j to remove old expansion-enterprise relations that may conflict with mainline unified files.

// 1) Remove ALL enterprise relations written by old expansion enterprise patches
MATCH ()-[r]->()
WHERE type(r) IN ['FOCUSES_ON_SUB_TRACK','LOCATED_IN_STAGE','HAS_KEY_CAPABILITY']
  AND r.source = 'manual_expansion_patch_2026-05-12'
DELETE r;

// 2) Optional targeted cleanup for Jiuwei old compute mapping (safe even if step 1 already removed it)
MATCH (:Enterprise {id:'ENT_337B26DB83F2'})-[r:FOCUSES_ON_SUB_TRACK]->(:SubTrack {id:'SUB_005'}) DELETE r;
MATCH (:Enterprise {id:'ENT_337B26DB83F2'})-[r:LOCATED_IN_STAGE]->(:ChainStage)
WHERE endNode(r).id IN ['STG_005_002','STG_005_004'] DELETE r;
MATCH (:Enterprise {id:'ENT_337B26DB83F2'})-[r:HAS_KEY_CAPABILITY]->(:KeyCapability)
WHERE endNode(r).id IN ['KCAP_COMP_001','KCAP_COMP_002'] DELETE r;

// 3) Quick verify
MATCH ()-[r]->()
WHERE r.source = 'manual_expansion_patch_2026-05-12'
RETURN type(r) AS rel_type, count(*) AS cnt;
