// Neo4j LOAD CSV import template
// Adjust file URLs according to your Neo4j import directory.

LOAD CSV WITH HEADERS FROM 'file:///neo4j_enterprise_nodes.csv' AS row
MERGE (n:Enterprise {id: row.`id:ID`})
SET n.name = row.name,
    n.intro = row.intro,
    n.business_model = row.business_model,
    n.certification_ip = row.certification_ip,
    n.founder_team = row.founder_team,
    n.revenue_financing = row.revenue_financing,
    n.advantage = row.advantage,
    n.match_level = row.match_level,
    n.source_file = row.source_file,
    n.row_no = toInteger(row.row_no);

LOAD CSV WITH HEADERS FROM 'file:///neo4j_entity_nodes.csv' AS row
CALL {
  WITH row
  WITH row WHERE row.`:LABEL` = 'Product'
  MERGE (n:Product {id: row.`id:ID`})
  SET n.name = row.name, n.normalized_name = row.normalized_name, n.source_file = row.source_file
  RETURN count(*) AS _
}
RETURN 1;

LOAD CSV WITH HEADERS FROM 'file:///neo4j_entity_nodes.csv' AS row
CALL {
  WITH row
  WITH row WHERE row.`:LABEL` = 'Capability'
  MERGE (n:Capability {id: row.`id:ID`})
  SET n.name = row.name, n.normalized_name = row.normalized_name, n.source_file = row.source_file
  RETURN count(*) AS _
}
RETURN 1;

LOAD CSV WITH HEADERS FROM 'file:///neo4j_entity_nodes.csv' AS row
CALL {
  WITH row
  WITH row WHERE row.`:LABEL` = 'Industry'
  MERGE (n:Industry {id: row.`id:ID`})
  SET n.name = row.name, n.normalized_name = row.normalized_name, n.source_file = row.source_file
  RETURN count(*) AS _
}
RETURN 1;

LOAD CSV WITH HEADERS FROM 'file:///neo4j_entity_nodes.csv' AS row
CALL {
  WITH row
  WITH row WHERE row.`:LABEL` = 'Scenario'
  MERGE (n:Scenario {id: row.`id:ID`})
  SET n.name = row.name, n.normalized_name = row.normalized_name, n.source_file = row.source_file
  RETURN count(*) AS _
}
RETURN 1;

LOAD CSV WITH HEADERS FROM 'file:///neo4j_entity_nodes.csv' AS row
CALL {
  WITH row
  WITH row WHERE row.`:LABEL` = 'Customer'
  MERGE (n:Customer {id: row.`id:ID`})
  SET n.name = row.name, n.normalized_name = row.normalized_name, n.source_file = row.source_file
  RETURN count(*) AS _
}
RETURN 1;

LOAD CSV WITH HEADERS FROM 'file:///neo4j_entity_nodes.csv' AS row
CALL {
  WITH row
  WITH row WHERE row.`:LABEL` = 'Supplier'
  MERGE (n:Supplier {id: row.`id:ID`})
  SET n.name = row.name, n.normalized_name = row.normalized_name, n.source_file = row.source_file
  RETURN count(*) AS _
}
RETURN 1;

LOAD CSV WITH HEADERS FROM 'file:///neo4j_entity_nodes.csv' AS row
CALL {
  WITH row
  WITH row WHERE row.`:LABEL` = 'DemandTag'
  MERGE (n:DemandTag {id: row.`id:ID`})
  SET n.name = row.name, n.normalized_name = row.normalized_name, n.source_file = row.source_file
  RETURN count(*) AS _
}
RETURN 1;

LOAD CSV WITH HEADERS FROM 'file:///neo4j_relationships.csv' AS row
MATCH (a {id: row.`:START_ID`})
MATCH (b {id: row.`:END_ID`})
CALL apoc.create.relationship(a, row.`:TYPE`, {raw_value: row.raw_value, source_file: row.source_file, row_no: toInteger(row.row_no)}, b)
YIELD rel
RETURN count(rel);
