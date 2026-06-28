// 统一图谱导入后验证脚本 v1

// ========================================
// 1. 节点数量检查
// ========================================
MATCH (n:IndustryDomain) RETURN 'IndustryDomain' AS label, count(n) AS cnt
UNION ALL
MATCH (n:SubTrack) RETURN 'SubTrack' AS label, count(n) AS cnt
UNION ALL
MATCH (n:ChainStage) RETURN 'ChainStage' AS label, count(n) AS cnt
UNION ALL
MATCH (n:KeyCapability) RETURN 'KeyCapability' AS label, count(n) AS cnt
UNION ALL
MATCH (n:ApplicationScenario) RETURN 'ApplicationScenario' AS label, count(n) AS cnt
ORDER BY label;

// ========================================
// 2. 统一关系数量检查
// ========================================
MATCH ()-[r:HAS_SUB_TRACK]->() RETURN 'HAS_SUB_TRACK' AS rel, count(r) AS cnt
UNION ALL
MATCH ()-[r:HAS_STAGE]->() RETURN 'HAS_STAGE' AS rel, count(r) AS cnt
UNION ALL
MATCH ()-[r:UPSTREAM_OF]->() RETURN 'UPSTREAM_OF' AS rel, count(r) AS cnt
UNION ALL
MATCH ()-[r:REQUIRES_CAPABILITY]->() RETURN 'REQUIRES_CAPABILITY' AS rel, count(r) AS cnt
UNION ALL
MATCH ()-[r:DRIVES_STAGE]->() RETURN 'DRIVES_STAGE' AS rel, count(r) AS cnt
UNION ALL
MATCH ()-[r:FOCUSES_ON_SUB_TRACK]->() RETURN 'FOCUSES_ON_SUB_TRACK' AS rel, count(r) AS cnt
UNION ALL
MATCH ()-[r:LOCATED_IN_STAGE]->() RETURN 'LOCATED_IN_STAGE' AS rel, count(r) AS cnt
UNION ALL
MATCH ()-[r:HAS_KEY_CAPABILITY]->() RETURN 'HAS_KEY_CAPABILITY' AS rel, count(r) AS cnt
UNION ALL
MATCH ()-[r:MAPPED_TO]->() RETURN 'MAPPED_TO' AS rel, count(r) AS cnt
ORDER BY rel;

// ========================================
// 3. 子赛道 -> 环节 骨架检查
// ========================================
MATCH (s:SubTrack)-[:HAS_STAGE]->(st:ChainStage)
RETURN s.name AS sub_track,
       count(st) AS stage_count,
       min(st.stage_order) AS min_stage_order,
       max(st.stage_order) AS max_stage_order
ORDER BY sub_track;

// ========================================
// 4. 企业挂接检查
// ========================================
MATCH (e:Enterprise)-[:FOCUSES_ON_SUB_TRACK]->(s:SubTrack)
RETURN s.name AS sub_track,
       count(DISTINCT e) AS enterprise_count,
       collect(DISTINCT e.name)[0..20] AS enterprises
ORDER BY enterprise_count DESC, sub_track;

// ========================================
// 5. 查询样例：某企业在统一图谱中的位置
// ========================================
MATCH (e:Enterprise {name: '中科慧远视觉技术（洛阳）有限公司'})
OPTIONAL MATCH (e)-[:FOCUSES_ON_SUB_TRACK]->(s:SubTrack)
OPTIONAL MATCH (e)-[:LOCATED_IN_STAGE]->(st:ChainStage)
OPTIONAL MATCH (e)-[:HAS_KEY_CAPABILITY]->(k:KeyCapability)
RETURN e.name AS enterprise,
       collect(DISTINCT s.name) AS sub_tracks,
       collect(DISTINCT st.name) AS stages,
       collect(DISTINCT k.name) AS key_capabilities;

// ========================================
// 6. 查询样例：按环节找企业
// ========================================
MATCH (st:ChainStage {id: 'STG_OC_009'})
OPTIONAL MATCH (e:Enterprise)-[:LOCATED_IN_STAGE]->(st)
RETURN st.name AS stage,
       collect(DISTINCT e.name) AS enterprises;

// ========================================
// 7. 查询样例：按场景反查环节
// ========================================
MATCH (a:ApplicationScenario {id: 'ASCN_MV_005'})-[:DRIVES_STAGE]->(st:ChainStage)
RETURN a.name AS scenario,
       collect(DISTINCT st.name) AS stages;
