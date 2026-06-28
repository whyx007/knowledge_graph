# Scripts

后续建议补充三类脚本：

1. PostgreSQL 抽取脚本：连接 PostgreSQL，导出 `data/staging/*.csv`。
2. 关键词初筛脚本：根据 `chain_substages.csv` 的关键词生成候选企业挂接。
3. 导入准备脚本：把 `data/mappings` 和 `data/staging` 同步到 `neo4j/import`。

当前已有脚本：

- `export_postgres_to_staging.sh`：从 PostgreSQL 导出企业和证据文本。
- `generate_substage_candidates.py`：基于关键词生成候选细分环节挂接。
- `prepare_neo4j_import.sh`：同步 CSV 到 Neo4j import 目录。

候选挂接默认 `needs_review=true`，不能直接视为业务确认结果。
