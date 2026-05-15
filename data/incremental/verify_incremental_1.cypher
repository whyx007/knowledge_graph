MATCH (e:Enterprise)
WHERE e.source_file = 'company-info_with_url.xlsx'
RETURN count(e) AS incremental_enterprises;
