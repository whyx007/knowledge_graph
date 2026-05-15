// 统一图谱查询模板
// 适用于统一图谱 v1
// 建议参数：
// :param subTrackId => 'SUB_001';
// :param stageId => 'STG_MV_008';
// :param enterpriseName => '中科慧远视觉技术（洛阳）有限公司';
// :param capabilityKeyword => '检测';
// :param scenarioKeyword => '锂电';
// :param limit => 20;

// ========================================
// 0. 查看所有子赛道与企业数量
// ========================================
MATCH (s:SubTrack)
OPTIONAL MATCH (e:Enterprise)-[:FOCUSES_ON_SUB_TRACK]->(s)
RETURN s.id AS sub_track_id,
       s.name AS sub_track,
       count(DISTINCT e) AS enterprise_count
ORDER BY sub_track_id;

// ========================================
// 1. 按子赛道看企业
// ========================================
MATCH (s:SubTrack {id: $subTrackId})
OPTIONAL MATCH (e:Enterprise)-[:FOCUSES_ON_SUB_TRACK]->(s)
OPTIONAL MATCH (e)-[:LOCATED_IN_STAGE]->(st:ChainStage)
RETURN s.name AS sub_track,
       e.name AS enterprise,
       collect(DISTINCT st.name)[0..5] AS stages
ORDER BY enterprise;

// ========================================
// 2. 按环节找企业
// ========================================
MATCH (st:ChainStage {id: $stageId})
OPTIONAL MATCH (e:Enterprise)-[:LOCATED_IN_STAGE]->(st)
OPTIONAL MATCH (e)-[:HAS_KEY_CAPABILITY]->(k:KeyCapability)
RETURN st.name AS stage,
       e.name AS enterprise,
       collect(DISTINCT k.name)[0..10] AS key_capabilities
ORDER BY enterprise;

// ========================================
// 3. 查看某企业在统一图谱中的位置
// ========================================
MATCH (e:Enterprise {name: $enterpriseName})
OPTIONAL MATCH (e)-[:FOCUSES_ON_SUB_TRACK]->(s:SubTrack)
OPTIONAL MATCH (e)-[:LOCATED_IN_STAGE]->(st:ChainStage)
OPTIONAL MATCH (e)-[:HAS_KEY_CAPABILITY]->(k:KeyCapability)
RETURN e.name AS enterprise,
       collect(DISTINCT s.name)[0..5] AS sub_tracks,
       collect(DISTINCT st.name)[0..10] AS stages,
       collect(DISTINCT k.name)[0..20] AS key_capabilities;

// ========================================
// 4. 从关键能力反查企业与环节
// ========================================
MATCH (k:KeyCapability)
WHERE k.name CONTAINS $capabilityKeyword
OPTIONAL MATCH (e:Enterprise)-[:HAS_KEY_CAPABILITY]->(k)
OPTIONAL MATCH (e)-[:LOCATED_IN_STAGE]->(st:ChainStage)
RETURN k.name AS key_capability,
       e.name AS enterprise,
       collect(DISTINCT st.name)[0..10] AS stages
ORDER BY key_capability, enterprise
LIMIT coalesce($limit, 20);

// ========================================
// 5. 从场景反查环节与企业
// ========================================
MATCH (a:ApplicationScenario)
WHERE a.name CONTAINS $scenarioKeyword
OPTIONAL MATCH (a)-[:DRIVES_STAGE]->(st:ChainStage)
OPTIONAL MATCH (e:Enterprise)-[:LOCATED_IN_STAGE]->(st)
RETURN a.name AS application_scenario,
       collect(DISTINCT st.name)[0..10] AS driven_stages,
       collect(DISTINCT e.name)[0..coalesce($limit, 20)] AS enterprises;

// ========================================
// 6. 查看某子赛道完整结构骨架
// ========================================
MATCH (s:SubTrack {id: $subTrackId})-[:HAS_STAGE]->(st:ChainStage)
OPTIONAL MATCH (st)-[:REQUIRES_CAPABILITY]->(k:KeyCapability)
RETURN s.name AS sub_track,
       st.stage_order AS stage_order,
       st.name AS stage,
       collect(DISTINCT k.name)[0..10] AS required_capabilities
ORDER BY stage_order;

// ========================================
// 7. 某子赛道中的上下游关系
// ========================================
MATCH (s:SubTrack {id: $subTrackId})-[:HAS_STAGE]->(a:ChainStage)
MATCH (a)-[:UPSTREAM_OF]->(b:ChainStage)
RETURN s.name AS sub_track,
       a.stage_order AS from_order,
       a.name AS upstream_stage,
       b.stage_order AS to_order,
       b.name AS downstream_stage
ORDER BY from_order;

// ========================================
// 8. 图形化：企业-环节-能力
// ========================================
MATCH (e:Enterprise {name: $enterpriseName})
OPTIONAL MATCH (e)-[r1:FOCUSES_ON_SUB_TRACK]->(s:SubTrack)
OPTIONAL MATCH (e)-[r2:LOCATED_IN_STAGE]->(st:ChainStage)
OPTIONAL MATCH (e)-[r3:HAS_KEY_CAPABILITY]->(k:KeyCapability)
RETURN e, r1, s, r2, st, r3, k;
