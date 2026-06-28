// Unified graph schema v1

CREATE CONSTRAINT enterprise_id_unique IF NOT EXISTS
FOR (n:Enterprise) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT product_id_unique IF NOT EXISTS
FOR (n:Product) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT capability_id_unique IF NOT EXISTS
FOR (n:Capability) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT industry_id_unique IF NOT EXISTS
FOR (n:Industry) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT scenario_id_unique IF NOT EXISTS
FOR (n:Scenario) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT customer_id_unique IF NOT EXISTS
FOR (n:Customer) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT supplier_id_unique IF NOT EXISTS
FOR (n:Supplier) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT demandtag_id_unique IF NOT EXISTS
FOR (n:DemandTag) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT industrydomain_id_unique IF NOT EXISTS
FOR (n:IndustryDomain) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT subtrack_id_unique IF NOT EXISTS
FOR (n:SubTrack) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT chainstage_id_unique IF NOT EXISTS
FOR (n:ChainStage) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT techdirection_id_unique IF NOT EXISTS
FOR (n:TechDirection) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT keycapability_id_unique IF NOT EXISTS
FOR (n:KeyCapability) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT applicationscenario_id_unique IF NOT EXISTS
FOR (n:ApplicationScenario) REQUIRE n.id IS UNIQUE;
