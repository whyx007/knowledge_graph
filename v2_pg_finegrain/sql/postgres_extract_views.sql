-- PostgreSQL extraction views for V2 fine-grain graph.
-- Confirmed database: ceo_brief
-- Confirmed tables: companies, trainees
-- Do not include passwords in this SQL file.

CREATE OR REPLACE VIEW kg_v2_enterprises AS
SELECT
  ('ENT_PG_' || id::text) AS enterprise_id,
  id::text AS source_pk,
  name AS enterprise_name,
  domain,
  city,
  industry,
  scenario,
  website,
  status,
  maturity,
  created_at,
  'postgresql' AS source_system,
  now() AS last_sync_at,
  is_invested
FROM companies;

DROP VIEW IF EXISTS kg_v2_enterprise_evidence;

CREATE VIEW kg_v2_enterprise_evidence AS
SELECT
  ('ENT_PG_' || c.id::text) AS enterprise_id,
  c.id::text AS source_pk,
  c.name AS enterprise_name,
  c.domain,
  c.industry,
  c.core_tech,
  c.products,
  c.scenario,
  c.cert_ip,
  c.homepage_html,
  concat_ws(' ',
    c.domain,
    c.industry,
    c.core_tech,
    c.products,
    c.scenario,
    c.cert_ip,
    c.homepage_html
  ) AS evidence_text,
  'domain,industry,core_tech,products,scenario' AS source_field,
  'postgresql' AS source_system,
  now() AS extracted_at
FROM companies c;

-- Suggested downstream process:
-- 1. Export kg_v2_enterprises to data/staging/enterprises.csv.
-- 2. Match kg_v2_enterprise_evidence against chain_substages.csv keywords.
-- 3. Write reviewed mappings to data/staging/enterprise_to_substage.csv.

CREATE OR REPLACE VIEW kg_v2_trainee_enterprise_evidence AS
SELECT
  t.id::text AS trainee_id,
  t.name AS trainee_name,
  t.company_name,
  t.position,
  t.industry_sector,
  t.sub_sector,
  concat_ws(' ',
    t.company_intro,
    t.work_field,
    t.industry_sector,
    t.sub_sector,
    t.upstream_downstream,
    t.desired_links,
    t.dev_plan
  ) AS evidence_text,
  'trainees' AS source_system,
  now() AS extracted_at
FROM trainees t;
