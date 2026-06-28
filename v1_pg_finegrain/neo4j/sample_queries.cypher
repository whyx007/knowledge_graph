// Sample queries for enterprise knowledge graph

// 1) Count nodes by label
MATCH (n)
RETURN labels(n) AS labels, count(*) AS cnt
ORDER BY cnt DESC;

// 2) Count relationships by type
MATCH ()-[r]->()
RETURN type(r) AS rel_type, count(*) AS cnt
ORDER BY cnt DESC;

// 3) Enterprise profile by exact name
MATCH (e:Enterprise {name: $name})
OPTIONAL MATCH (e)-[:PROVIDES_PRODUCT]->(p:Product)
OPTIONAL MATCH (e)-[:SERVES_INDUSTRY]->(i:Industry)
OPTIONAL MATCH (e)-[:APPLIES_TO_SCENARIO]->(s:Scenario)
OPTIONAL MATCH (e)-[:HAS_DEMAND]->(d:DemandTag)
RETURN e.name AS enterprise,
       collect(DISTINCT p.name)[0..20] AS products,
       collect(DISTINCT i.name)[0..20] AS industries,
       collect(DISTINCT s.name)[0..20] AS scenarios,
       collect(DISTINCT d.name)[0..20] AS demands;

// 4) Find enterprises by industry keyword
MATCH (e:Enterprise)-[:SERVES_INDUSTRY]->(i:Industry)
WHERE i.name CONTAINS $keyword
RETURN i.name AS industry, collect(DISTINCT e.name)[0..50] AS enterprises
ORDER BY industry;

// 5) Find enterprises by demand keyword
MATCH (e:Enterprise)-[:HAS_DEMAND]->(d:DemandTag)
WHERE d.name CONTAINS $keyword
RETURN d.name AS demand, collect(DISTINCT e.name)[0..50] AS enterprises
ORDER BY demand;

// 6) Customer/supplier view of an enterprise
MATCH (e:Enterprise {name: $name})
OPTIONAL MATCH (e)-[:HAS_CUSTOMER]->(c:Customer)
OPTIONAL MATCH (e)-[:HAS_SUPPLIER]->(s:Supplier)
RETURN e.name AS enterprise,
       collect(DISTINCT c.name)[0..30] AS customers,
       collect(DISTINCT s.name)[0..30] AS suppliers;
