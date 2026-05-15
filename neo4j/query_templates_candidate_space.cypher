// 商业航天候选域查询模板
// 说明：
// 1. 当前商业航天是候选域，企业节点与正式主图谱共用同一批 Enterprise
// 2. 查询时务必按 SUB_SPACE_001 / STG_SPACE_* / KCAP_SPACE_* / TD_SPACE_* 过滤
// 3. 否则容易混入原有光电子三条样板链关系

// ========================================
// 0. 商业航天候选域企业总览
// ========================================
MATCH (e:Enterprise)-[:FOCUSES_ON_SUB_TRACK]->(s:SubTrack {id: 'SUB_SPACE_001'})
OPTIONAL MATCH (e)-[:LOCATED_IN_STAGE]->(st:ChainStage)
WHERE st.id STARTS WITH 'STG_SPACE_'
OPTIONAL MATCH (e)-[:HAS_KEY_CAPABILITY]->(k:KeyCapability)
WHERE k.id STARTS WITH 'KCAP_SPACE_'
RETURN e.name AS enterprise,
       collect(DISTINCT st.name) AS space_stages,
       collect(DISTINCT k.name) AS space_key_capabilities
ORDER BY enterprise;

// ========================================
// 1. 商业航天候选域按环节找企业
// :param stageId => 'STG_SPACE_007';
// ========================================
MATCH (st:ChainStage {id: $stageId})
MATCH (e:Enterprise)-[:LOCATED_IN_STAGE]->(st)
MATCH (e)-[:FOCUSES_ON_SUB_TRACK]->(:SubTrack {id: 'SUB_SPACE_001'})
OPTIONAL MATCH (e)-[:HAS_KEY_CAPABILITY]->(k:KeyCapability)
WHERE k.id STARTS WITH 'KCAP_SPACE_'
RETURN st.name AS stage,
       e.name AS enterprise,
       collect(DISTINCT k.name) AS key_capabilities
ORDER BY enterprise;

// ========================================
// 2. 查看某企业在商业航天候选域中的位置
// :param enterpriseName => '西安中科天塔科技股份有限公司';
// ========================================
MATCH (e:Enterprise {name: $enterpriseName})-[:FOCUSES_ON_SUB_TRACK]->(:SubTrack {id: 'SUB_SPACE_001'})
OPTIONAL MATCH (e)-[:LOCATED_IN_STAGE]->(st:ChainStage)
WHERE st.id STARTS WITH 'STG_SPACE_'
OPTIONAL MATCH (e)-[:HAS_KEY_CAPABILITY]->(k:KeyCapability)
WHERE k.id STARTS WITH 'KCAP_SPACE_'
RETURN e.name AS enterprise,
       collect(DISTINCT st.name) AS space_stages,
       collect(DISTINCT k.name) AS space_key_capabilities;

// ========================================
// 3. 查看某企业“正式样板链关系 vs 商业航天候选域关系”对照
// :param enterpriseName => '西安朗威科技有限公司';
// ========================================
MATCH (e:Enterprise {name: $enterpriseName})
OPTIONAL MATCH (e)-[:FOCUSES_ON_SUB_TRACK]->(s1:SubTrack)
WITH e, collect(DISTINCT s1.name) AS all_subtracks
OPTIONAL MATCH (e)-[:LOCATED_IN_STAGE]->(st1:ChainStage)
WITH e, all_subtracks, collect(DISTINCT st1.name) AS all_stages
OPTIONAL MATCH (e)-[:HAS_KEY_CAPABILITY]->(k1:KeyCapability)
WITH e, all_subtracks, all_stages, collect(DISTINCT k1.name) AS all_key_capabilities
OPTIONAL MATCH (e)-[:FOCUSES_ON_SUB_TRACK]->(:SubTrack {id: 'SUB_SPACE_001'})
OPTIONAL MATCH (e)-[:LOCATED_IN_STAGE]->(st2:ChainStage)
WHERE st2.id STARTS WITH 'STG_SPACE_'
OPTIONAL MATCH (e)-[:HAS_KEY_CAPABILITY]->(k2:KeyCapability)
WHERE k2.id STARTS WITH 'KCAP_SPACE_'
RETURN e.name AS enterprise,
       all_subtracks,
       all_stages,
       all_key_capabilities,
       collect(DISTINCT st2.name) AS candidate_space_stages,
       collect(DISTINCT k2.name) AS candidate_space_key_capabilities;

// ========================================
// 4. 商业航天候选域按关键能力找企业
// :param keycapId => 'KCAP_SPACE_007';
// ========================================
MATCH (k:KeyCapability {id: $keycapId})
MATCH (e:Enterprise)-[:HAS_KEY_CAPABILITY]->(k)
MATCH (e)-[:FOCUSES_ON_SUB_TRACK]->(:SubTrack {id: 'SUB_SPACE_001'})
OPTIONAL MATCH (e)-[:LOCATED_IN_STAGE]->(st:ChainStage)
WHERE st.id STARTS WITH 'STG_SPACE_'
RETURN k.name AS key_capability,
       e.name AS enterprise,
       collect(DISTINCT st.name) AS stages
ORDER BY enterprise;

// ========================================
// 5. 商业航天候选域技术方向 -> 环节
// ========================================
MATCH (t:TechDirection)-[:ENABLES_STAGE]->(st:ChainStage)
WHERE t.id STARTS WITH 'TD_SPACE_' AND st.id STARTS WITH 'STG_SPACE_'
RETURN t.name AS tech_direction,
       collect(DISTINCT st.name) AS enabled_stages
ORDER BY tech_direction;

// ========================================
// 6. 商业航天候选域应用场景 -> 环节
// ========================================
MATCH (a:ApplicationScenario)-[:DRIVES_STAGE]->(st:ChainStage)
WHERE a.id STARTS WITH 'ASCN_SPACE_' AND st.id STARTS WITH 'STG_SPACE_'
RETURN a.name AS application_scenario,
       collect(DISTINCT st.name) AS driven_stages
ORDER BY application_scenario;
