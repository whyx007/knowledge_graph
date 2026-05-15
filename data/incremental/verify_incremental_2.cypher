MATCH (e:Enterprise)-[r]->()
WHERE e.source_file = 'company-info_with_url.xlsx'
RETURN type(r) AS rel_type, count(r) AS cnt
ORDER BY cnt DESC;
