// Incremental import for company-info_with_url.xlsx
// 仅导入新增企业；已有企业不重复导入

LOAD CSV WITH HEADERS FROM 'file:///neo4j_enterprise_nodes_incremental.csv' AS row
MERGE (e:Enterprise {id: row.`id:ID`})
SET e.name = row.name,
    e.label = row.label,
    e.source_file = row.source_file,
    e.row_no = toInteger(row.row_no),
    e.core_technology = row.core_technology,
    e.technology_maturity = row.technology_maturity,
    e.possible_scenarios = row.possible_scenarios,
    e.business_model = row.business_model,
    e.delivery_capability = row.delivery_capability,
    e.certification_ip = row.certification_ip,
    e.founder_team_and_gap = row.founder_team_and_gap,
    e.recent_revenue_profit = row.recent_revenue_profit,
    e.competition_and_diff = row.competition_and_diff,
    e.match_level = row.match_level,
    e.website_url = row.website_url;

LOAD CSV WITH HEADERS FROM 'file:///neo4j_entity_nodes_incremental.csv' AS row
CALL {
  WITH row
  FOREACH (_ IN CASE WHEN row.label = 'Product' THEN [1] ELSE [] END |
    MERGE (n:Product {id: row.`id:ID`})
    SET n.name = row.name, n.label = row.label, n.normalized_name = row.normalized_name, n.source_file = row.source_file
  )
  FOREACH (_ IN CASE WHEN row.label = 'Capability' THEN [1] ELSE [] END |
    MERGE (n:Capability {id: row.`id:ID`})
    SET n.name = row.name, n.label = row.label, n.normalized_name = row.normalized_name, n.source_file = row.source_file
  )
  FOREACH (_ IN CASE WHEN row.label = 'Industry' THEN [1] ELSE [] END |
    MERGE (n:Industry {id: row.`id:ID`})
    SET n.name = row.name, n.label = row.label, n.normalized_name = row.normalized_name, n.source_file = row.source_file
  )
  FOREACH (_ IN CASE WHEN row.label = 'Scenario' THEN [1] ELSE [] END |
    MERGE (n:Scenario {id: row.`id:ID`})
    SET n.name = row.name, n.label = row.label, n.normalized_name = row.normalized_name, n.source_file = row.source_file
  )
  FOREACH (_ IN CASE WHEN row.label = 'Customer' THEN [1] ELSE [] END |
    MERGE (n:Customer {id: row.`id:ID`})
    SET n.name = row.name, n.label = row.label, n.normalized_name = row.normalized_name, n.source_file = row.source_file
  )
  FOREACH (_ IN CASE WHEN row.label = 'Supplier' THEN [1] ELSE [] END |
    MERGE (n:Supplier {id: row.`id:ID`})
    SET n.name = row.name, n.label = row.label, n.normalized_name = row.normalized_name, n.source_file = row.source_file
  )
  FOREACH (_ IN CASE WHEN row.label = 'DemandTag' THEN [1] ELSE [] END |
    MERGE (n:DemandTag {id: row.`id:ID`})
    SET n.name = row.name, n.label = row.label, n.normalized_name = row.normalized_name, n.source_file = row.source_file
  )
  RETURN 1 AS done
}
RETURN count(*) AS imported_entities;

LOAD CSV WITH HEADERS FROM 'file:///neo4j_relationships_incremental.csv' AS row
MATCH (a {id: row.`:START_ID`})
MATCH (b {id: row.`:END_ID`})
CALL {
  WITH row, a, b
  FOREACH (_ IN CASE WHEN row.`:TYPE` = 'PROVIDES_PRODUCT' THEN [1] ELSE [] END | MERGE (a)-[:PROVIDES_PRODUCT]->(b))
  FOREACH (_ IN CASE WHEN row.`:TYPE` = 'HAS_CAPABILITY' THEN [1] ELSE [] END | MERGE (a)-[:HAS_CAPABILITY]->(b))
  FOREACH (_ IN CASE WHEN row.`:TYPE` = 'SERVES_INDUSTRY' THEN [1] ELSE [] END | MERGE (a)-[:SERVES_INDUSTRY]->(b))
  FOREACH (_ IN CASE WHEN row.`:TYPE` = 'APPLIES_TO_SCENARIO' THEN [1] ELSE [] END | MERGE (a)-[:APPLIES_TO_SCENARIO]->(b))
  FOREACH (_ IN CASE WHEN row.`:TYPE` = 'HAS_CUSTOMER' THEN [1] ELSE [] END | MERGE (a)-[:HAS_CUSTOMER]->(b))
  FOREACH (_ IN CASE WHEN row.`:TYPE` = 'HAS_SUPPLIER' THEN [1] ELSE [] END | MERGE (a)-[:HAS_SUPPLIER]->(b))
  FOREACH (_ IN CASE WHEN row.`:TYPE` = 'HAS_DEMAND' THEN [1] ELSE [] END | MERGE (a)-[:HAS_DEMAND]->(b))
  RETURN 1 AS done
}
RETURN count(*) AS imported_relationships;
