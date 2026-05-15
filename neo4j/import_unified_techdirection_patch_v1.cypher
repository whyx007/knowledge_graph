// TechDirection import patch v1

LOAD CSV WITH HEADERS FROM 'file:///unified_tech_directions_v1.csv' AS row
MERGE (s:SubTrack {id: row.sub_track_id})
MERGE (t:TechDirection {id: row.tech_direction_id})
SET t.name = row.tech_direction_name,
    t.description = row.description,
    t.sub_track_id = row.sub_track_id;

LOAD CSV WITH HEADERS FROM 'file:///unified_rel_techdirection_to_stage_v1.csv' AS row
MATCH (t:TechDirection {id: row.start_id})
MATCH (st:ChainStage {id: row.end_id})
MERGE (t)-[r:ENABLES_STAGE]->(st)
SET r.confidence = toFloat(row.confidence),
    r.source = row.source;
