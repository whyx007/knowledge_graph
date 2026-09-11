# Scripts

后续建议补充三类脚本：

1. PostgreSQL 抽取脚本：连接 PostgreSQL，导出 `data/staging/*.csv`。
2. 关键词初筛脚本：根据 `chain_substages.csv` 的关键词生成候选企业挂接。
3. 导入准备脚本：把 `data/mappings` 和 `data/staging` 同步到 `neo4j/import`。

当前已有脚本：

- `export_postgres_to_staging.sh`：从 PostgreSQL 导出企业和证据文本。
- `generate_substage_candidates.py`：基于关键词生成候选细分环节挂接。
- `prepare_neo4j_import.sh`：同步 CSV 到 Neo4j import 目录。
- `sync_project_from_neo4j.py`：以运行中的 v2 Neo4j 为准回写企业和挂接中间表，保留关系审计字段，并生成当前结构快照及约束/索引 Cypher。
- `preview_manual_company_updates.py`：只读比对人工确认 Excel 与现有 PostgreSQL，生成字段级更新预览、排除清单和后续事务更新暂存表；不会连接 Neo4j 或写数据库。
- `apply_manual_company_updates.py`：备份后将人工确认字段增量写入现有 PostgreSQL，并按 PostgreSQL ID 同步现有 Docker Neo4j；包含基线断言、事务、补偿回滚和逐字段验收。
- `supplement_new_company_fields.py`：依据遗漏被投企业名单，只补充上一批 46 家新增企业的空字段并同步 Neo4j；已有值保持不变。
- `delete_renamed_company_duplicate.py`：精确删除已更名企业的旧 PostgreSQL 行和旧 Neo4j 节点，保留新主体，并验证其他数据及关系不变。
- `set_all_companies_invested.py`：将现有 PostgreSQL 企业和 Neo4j 企业节点统一标记为 `is_invested=true`，并验证其他属性与关系不变。
- `match_invested_partners.py`：基于 PostgreSQL 被投标记与 v2 Neo4j 产业链挂载信息生成合作候选和分级建议。

候选挂接默认 `needs_review=true`，不能直接视为业务确认结果。
