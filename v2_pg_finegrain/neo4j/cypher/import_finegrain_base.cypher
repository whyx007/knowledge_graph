CREATE CONSTRAINT industry_chain_id IF NOT EXISTS
FOR (n:IndustryChain) REQUIRE n.chain_id IS UNIQUE;

CREATE CONSTRAINT chain_segment_id IF NOT EXISTS
FOR (n:ChainSegment) REQUIRE n.segment_id IS UNIQUE;

CREATE CONSTRAINT chain_stage_id IF NOT EXISTS
FOR (n:ChainStage) REQUIRE n.stage_id IS UNIQUE;

CREATE CONSTRAINT chain_substage_id IF NOT EXISTS
FOR (n:ChainSubstage) REQUIRE n.substage_id IS UNIQUE;

CREATE CONSTRAINT enterprise_id IF NOT EXISTS
FOR (n:Enterprise) REQUIRE n.enterprise_id IS UNIQUE;

LOAD CSV WITH HEADERS FROM 'file:///chain_master.csv' AS row
MERGE (c:IndustryChain {chain_id: row.chain_id})
SET c.domain_name = row.domain_name,
    c.chain_name = row.chain_name,
    c.maturity_level = row.maturity_level,
    c.pilot_flag = row.pilot_flag = 'true',
    c.description = row.description;

LOAD CSV WITH HEADERS FROM 'file:///chain_segments.csv' AS row
MATCH (c:IndustryChain {chain_id: row.chain_id})
MERGE (s:ChainSegment {segment_id: row.segment_id})
SET s.chain_id = row.chain_id,
    s.segment_name = row.segment_name,
    s.segment_order = toInteger(row.segment_order)
MERGE (c)-[:HAS_SEGMENT]->(s);

LOAD CSV WITH HEADERS FROM 'file:///chain_stages.csv' AS row
MATCH (seg:ChainSegment {segment_id: row.segment_id})
MERGE (st:ChainStage {stage_id: row.stage_id})
SET st.chain_id = row.chain_id,
    st.segment_id = row.segment_id,
    st.stage_name = row.stage_name,
    st.stage_order = toInteger(row.stage_order),
    st.definition = row.definition,
    st.include_criteria = row.include_criteria,
    st.exclude_criteria = row.exclude_criteria,
    st.keywords = row.keywords
MERGE (seg)-[:HAS_STAGE]->(st);

LOAD CSV WITH HEADERS FROM 'file:///chain_substages.csv' AS row
MATCH (st:ChainStage {stage_id: row.stage_id})
MERGE (sub:ChainSubstage {substage_id: row.substage_id})
SET sub.stage_id = row.stage_id,
    sub.substage_name = row.substage_name,
    sub.definition = row.definition,
    sub.keywords = row.keywords
MERGE (st)-[:HAS_SUBSTAGE]->(sub);

LOAD CSV WITH HEADERS FROM 'file:///substage_to_substage.csv' AS row
MATCH (from:ChainSubstage {substage_id: row.from_substage_id})
MATCH (to:ChainSubstage {substage_id: row.to_substage_id})
MERGE (from)-[r:UPSTREAM_OF]->(to)
SET r.relation_type = row.relation_type,
    r.description = row.description;

LOAD CSV WITH HEADERS FROM 'file:///enterprises.csv' AS row
WITH row WHERE row.enterprise_id IS NOT NULL AND row.enterprise_id <> ''
MERGE (e:Enterprise {enterprise_id: row.enterprise_id})
SET e.enterprise_name = row.enterprise_name,
    e.source_system = row.source_system,
    e.source_pk = row.source_pk,
    e.is_invested = coalesce(toBoolean(row.is_invested), true),
    e.last_sync_at = row.last_sync_at;

LOAD CSV WITH HEADERS FROM 'file:///enterprise_to_substage.csv' AS row
WITH row WHERE row.enterprise_id IS NOT NULL AND row.enterprise_id <> ''
MATCH (e:Enterprise {enterprise_id: row.enterprise_id})
MATCH (sub:ChainSubstage {substage_id: row.substage_id})
MERGE (e)-[r:LOCATED_IN_SUBSTAGE]->(sub)
SET r.confidence = row.confidence,
    r.evidence = row.evidence,
    r.source_field = row.source_field,
    r.source_system = row.source_system,
    r.needs_review = row.needs_review = 'true',
    r.source = nullIf(row.source, ''),
    r.source_pk = nullIf(row.source_pk, ''),
    r.updated_at = CASE WHEN row.updated_at IS NULL OR row.updated_at = '' THEN null ELSE datetime(row.updated_at) END,
    r.status = nullIf(row.status, ''),
    r.audit_status = nullIf(row.audit_status, ''),
    r.audit_decision = nullIf(row.audit_decision, ''),
    r.audit_confidence = nullIf(row.audit_confidence, ''),
    r.audit_evidence = nullIf(row.audit_evidence, ''),
    r.audit_reason = nullIf(row.audit_reason, ''),
    r.audit_model = nullIf(row.audit_model, ''),
    r.audit_method = nullIf(row.audit_method, ''),
    r.audit_batch_id = nullIf(row.audit_batch_id, ''),
    r.audit_reviewed_at = CASE WHEN row.audit_reviewed_at IS NULL OR row.audit_reviewed_at = '' THEN null ELSE datetime(row.audit_reviewed_at) END,
    r.audited_at = CASE WHEN row.audited_at IS NULL OR row.audited_at = '' THEN null ELSE datetime(row.audited_at) END,
    r.match_basis = nullIf(row.match_basis, '');
