// DEPRECATED after 2026-05-13 mainline merge.
// Do not run this file anymore.
// Enterprise mappings for 光计算 have been merged into mainline unified_rel_enterprise_to_*_legacyid.csv.
// Running this file again may reintroduce conflicting relations (e.g. old Jiuwei compute mapping).
RETURN 'DEPRECATED: use neo4j/import_unified_enterprise_patch_legacyid.cypher and optionally neo4j/cleanup_deprecated_expansion_enterprise_relations.cypher' AS message;
