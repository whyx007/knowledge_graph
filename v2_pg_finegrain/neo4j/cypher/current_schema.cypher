// Generated from neo4j-kg-v2-finegrain by sync_project_from_neo4j.py.
// Neo4j-managed LOOKUP indexes are intentionally omitted.

CREATE CONSTRAINT `chain_segment_id` IF NOT EXISTS FOR (n:`ChainSegment`) REQUIRE (n.`segment_id`) IS UNIQUE;

CREATE CONSTRAINT `chain_stage_id` IF NOT EXISTS FOR (n:`ChainStage`) REQUIRE (n.`stage_id`) IS UNIQUE;

CREATE CONSTRAINT `chain_substage_id` IF NOT EXISTS FOR (n:`ChainSubstage`) REQUIRE (n.`substage_id`) IS UNIQUE;

CREATE CONSTRAINT `enterprise_id` IF NOT EXISTS FOR (n:`Enterprise`) REQUIRE (n.`enterprise_id`) IS UNIQUE;

CREATE CONSTRAINT `industry_chain_id` IF NOT EXISTS FOR (n:`IndustryChain`) REQUIRE (n.`chain_id`) IS UNIQUE;

CREATE VECTOR INDEX `enterprise_embedding` IF NOT EXISTS FOR (n:`Enterprise`) ON (n.`embedding`) OPTIONS {indexConfig: {`vector.dimensions`: 1024,`vector.hnsw.ef_construction`: 100,`vector.hnsw.m`: 16,`vector.quantization.enabled`: true,`vector.similarity_function`: 'COSINE'}};

CREATE FULLTEXT INDEX `enterprise_text` IF NOT EXISTS FOR (n:`Enterprise`) ON EACH [n.`enterprise_name`, n.`embedding_text`] OPTIONS {indexConfig: {`fulltext.analyzer`: 'standard-no-stop-words',`fulltext.eventually_consistent`: false}};
