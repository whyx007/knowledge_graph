// Import relationships without APOC

LOAD CSV WITH HEADERS FROM 'file:///neo4j_relationships.csv' AS row
WITH row WHERE row.`:TYPE` = 'PROVIDES_PRODUCT'
MATCH (a:Enterprise {id: row.`:START_ID`})
MATCH (b:Product {id: row.`:END_ID`})
MERGE (a)-[r:PROVIDES_PRODUCT]->(b)
SET r.raw_value = row.raw_value,
    r.source_file = row.source_file,
    r.row_no = toInteger(row.row_no);

LOAD CSV WITH HEADERS FROM 'file:///neo4j_relationships.csv' AS row
WITH row WHERE row.`:TYPE` = 'HAS_CAPABILITY'
MATCH (a:Enterprise {id: row.`:START_ID`})
MATCH (b:Capability {id: row.`:END_ID`})
MERGE (a)-[r:HAS_CAPABILITY]->(b)
SET r.raw_value = row.raw_value,
    r.source_file = row.source_file,
    r.row_no = toInteger(row.row_no);

LOAD CSV WITH HEADERS FROM 'file:///neo4j_relationships.csv' AS row
WITH row WHERE row.`:TYPE` = 'SERVES_INDUSTRY'
MATCH (a:Enterprise {id: row.`:START_ID`})
MATCH (b:Industry {id: row.`:END_ID`})
MERGE (a)-[r:SERVES_INDUSTRY]->(b)
SET r.raw_value = row.raw_value,
    r.source_file = row.source_file,
    r.row_no = toInteger(row.row_no);

LOAD CSV WITH HEADERS FROM 'file:///neo4j_relationships.csv' AS row
WITH row WHERE row.`:TYPE` = 'APPLIES_TO_SCENARIO'
MATCH (a:Enterprise {id: row.`:START_ID`})
MATCH (b:Scenario {id: row.`:END_ID`})
MERGE (a)-[r:APPLIES_TO_SCENARIO]->(b)
SET r.raw_value = row.raw_value,
    r.source_file = row.source_file,
    r.row_no = toInteger(row.row_no);

LOAD CSV WITH HEADERS FROM 'file:///neo4j_relationships.csv' AS row
WITH row WHERE row.`:TYPE` = 'HAS_CUSTOMER'
MATCH (a:Enterprise {id: row.`:START_ID`})
MATCH (b:Customer {id: row.`:END_ID`})
MERGE (a)-[r:HAS_CUSTOMER]->(b)
SET r.raw_value = row.raw_value,
    r.source_file = row.source_file,
    r.row_no = toInteger(row.row_no);

LOAD CSV WITH HEADERS FROM 'file:///neo4j_relationships.csv' AS row
WITH row WHERE row.`:TYPE` = 'HAS_SUPPLIER'
MATCH (a:Enterprise {id: row.`:START_ID`})
MATCH (b:Supplier {id: row.`:END_ID`})
MERGE (a)-[r:HAS_SUPPLIER]->(b)
SET r.raw_value = row.raw_value,
    r.source_file = row.source_file,
    r.row_no = toInteger(row.row_no);

LOAD CSV WITH HEADERS FROM 'file:///neo4j_relationships.csv' AS row
WITH row WHERE row.`:TYPE` = 'HAS_DEMAND'
MATCH (a:Enterprise {id: row.`:START_ID`})
MATCH (b:DemandTag {id: row.`:END_ID`})
MERGE (a)-[r:HAS_DEMAND]->(b)
SET r.raw_value = row.raw_value,
    r.source_file = row.source_file,
    r.row_no = toInteger(row.row_no);
