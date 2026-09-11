# 当前 Neo4j 结构快照

> 数据来源：Docker 容器 `neo4j-kg-v2-finegrain`。
> 生成时间：`2026-08-12T03:47:27.260076+00:00`。
> 本文件由 `scripts/sync_project_from_neo4j.py` 生成；属性“完整”表示当前该类型的所有实体都包含该属性，不代表存在性约束。

## 节点类型

| 标签 | 当前节点数 |
|---|---:|
| `ChainSegment` | 27 |
| `ChainStage` | 123 |
| `ChainSubstage` | 475 |
| `Enterprise` | 525 |
| `IndustryChain` | 9 |
| `MountAuditDecision` | 506 |
| `MountAuditSnapshot` | 506 |

## 关系类型

| 类型 | 当前关系数 |
|---|---:|
| `HAS_SEGMENT` | 27 |
| `HAS_STAGE` | 123 |
| `HAS_SUBSTAGE` | 475 |
| `LOCATED_IN_SUBSTAGE` | 1246 |
| `UPSTREAM_OF` | 121 |

## 约束

| 名称 | 类型 | 实体 | 标签/类型 | 属性 |
|---|---|---|---|---|
| `chain_segment_id` | UNIQUENESS | NODE | ChainSegment | segment_id |
| `chain_stage_id` | UNIQUENESS | NODE | ChainStage | stage_id |
| `chain_substage_id` | UNIQUENESS | NODE | ChainSubstage | substage_id |
| `enterprise_id` | UNIQUENESS | NODE | Enterprise | enterprise_id |
| `industry_chain_id` | UNIQUENESS | NODE | IndustryChain | chain_id |

## 用户索引

Neo4j 自动创建的节点/关系 LOOKUP 索引未列入可重建脚本。

| 名称 | 类型 | 实体 | 标签/类型 | 属性 |
|---|---|---|---|---|
| `enterprise_embedding` | VECTOR | NODE | Enterprise | embedding |
| `enterprise_text` | FULLTEXT | NODE | Enterprise | enterprise_name, embedding_text |

## 节点属性

| 标签 | 属性 | 当前类型 | 已填充 | 完整 |
|---|---|---|---:|---|
| `ChainSegment` | `chain_id` | String | 27 | 是 |
| `ChainSegment` | `segment_id` | String | 27 | 是 |
| `ChainSegment` | `segment_name` | String | 27 | 是 |
| `ChainSegment` | `segment_order` | Long | 27 | 是 |
| `ChainStage` | `chain_id` | String | 123 | 是 |
| `ChainStage` | `definition` | String | 123 | 是 |
| `ChainStage` | `exclude_criteria` | String | 123 | 是 |
| `ChainStage` | `include_criteria` | String | 123 | 是 |
| `ChainStage` | `keywords` | String | 123 | 是 |
| `ChainStage` | `segment_id` | String | 123 | 是 |
| `ChainStage` | `stage_id` | String | 123 | 是 |
| `ChainStage` | `stage_name` | String | 123 | 是 |
| `ChainStage` | `stage_order` | Long | 123 | 是 |
| `ChainSubstage` | `definition` | String | 475 | 是 |
| `ChainSubstage` | `keywords` | String | 475 | 是 |
| `ChainSubstage` | `stage_id` | String | 475 | 是 |
| `ChainSubstage` | `substage_id` | String | 475 | 是 |
| `ChainSubstage` | `substage_name` | String | 475 | 是 |
| `Enterprise` | `cert_ip` | String | 525 | 是 |
| `Enterprise` | `core_tech` | String | 523 | 否 |
| `Enterprise` | `customers` | String | 479 | 否 |
| `Enterprise` | `domain` | String | 525 | 是 |
| `Enterprise` | `embedding` | DoubleArray | 525 | 是 |
| `Enterprise` | `embedding_model` | String | 525 | 是 |
| `Enterprise` | `embedding_text` | String | 525 | 是 |
| `Enterprise` | `embedding_updated_at` | DateTime | 525 | 是 |
| `Enterprise` | `enterprise_id` | String | 525 | 是 |
| `Enterprise` | `enterprise_name` | String | 525 | 是 |
| `Enterprise` | `industry` | String | 512 | 否 |
| `Enterprise` | `is_invested` | Boolean | 525 | 是 |
| `Enterprise` | `last_sync_at` | String, DateTime | 525 | 是 |
| `Enterprise` | `products` | String | 516 | 否 |
| `Enterprise` | `scenario` | String | 522 | 否 |
| `Enterprise` | `source_pk` | String | 525 | 是 |
| `Enterprise` | `source_system` | String | 525 | 是 |
| `Enterprise` | `suppliers` | String | 479 | 否 |
| `IndustryChain` | `chain_id` | String | 9 | 是 |
| `IndustryChain` | `chain_name` | String | 9 | 是 |
| `IndustryChain` | `description` | String | 9 | 是 |
| `IndustryChain` | `domain_name` | String | 9 | 是 |
| `IndustryChain` | `maturity_level` | String | 9 | 是 |
| `IndustryChain` | `pilot_flag` | Boolean | 9 | 是 |
| `MountAuditDecision` | `batch_id` | String | 506 | 是 |
| `MountAuditDecision` | `chain` | String | 506 | 是 |
| `MountAuditDecision` | `confidence` | String | 506 | 是 |
| `MountAuditDecision` | `correction_batch_id` | String | 7 | 否 |
| `MountAuditDecision` | `decided_at` | DateTime | 506 | 是 |
| `MountAuditDecision` | `decision` | String | 506 | 是 |
| `MountAuditDecision` | `edge_key` | String | 506 | 是 |
| `MountAuditDecision` | `enterprise_id` | String | 506 | 是 |
| `MountAuditDecision` | `enterprise_name` | String | 506 | 是 |
| `MountAuditDecision` | `evidence_quote` | String | 506 | 是 |
| `MountAuditDecision` | `method` | String | 506 | 是 |
| `MountAuditDecision` | `model` | String | 506 | 是 |
| `MountAuditDecision` | `previous_decision` | String | 7 | 否 |
| `MountAuditDecision` | `previous_reason` | String | 7 | 否 |
| `MountAuditDecision` | `reason` | String | 506 | 是 |
| `MountAuditDecision` | `snapshot_batch_id` | String | 506 | 是 |
| `MountAuditDecision` | `substage_id` | String | 506 | 是 |
| `MountAuditDecision` | `substage_name` | String | 506 | 是 |
| `MountAuditDecision` | `support_terms` | StringArray | 506 | 是 |
| `MountAuditSnapshot` | `batch_id` | String | 506 | 是 |
| `MountAuditSnapshot` | `chain` | String | 506 | 是 |
| `MountAuditSnapshot` | `confidence` | String | 506 | 是 |
| `MountAuditSnapshot` | `edge_key` | String | 506 | 是 |
| `MountAuditSnapshot` | `enterprise_id` | String | 506 | 是 |
| `MountAuditSnapshot` | `enterprise_name` | String | 506 | 是 |
| `MountAuditSnapshot` | `evidence` | String | 506 | 是 |
| `MountAuditSnapshot` | `needs_review` | Boolean | 506 | 是 |
| `MountAuditSnapshot` | `parent_stage` | String | 506 | 是 |
| `MountAuditSnapshot` | `segment` | String | 506 | 是 |
| `MountAuditSnapshot` | `snapshot_at` | DateTime | 506 | 是 |
| `MountAuditSnapshot` | `source_field` | String | 506 | 是 |
| `MountAuditSnapshot` | `source_system` | String | 506 | 是 |
| `MountAuditSnapshot` | `substage_id` | String | 506 | 是 |
| `MountAuditSnapshot` | `substage_name` | String | 506 | 是 |

## 关系属性

| 关系类型 | 属性 | 当前类型 | 已填充 | 完整 |
|---|---|---|---:|---|
| `LOCATED_IN_SUBSTAGE` | `audit_batch_id` | String | 1246 | 是 |
| `LOCATED_IN_SUBSTAGE` | `audit_confidence` | String | 1246 | 是 |
| `LOCATED_IN_SUBSTAGE` | `audit_decision` | String | 1246 | 是 |
| `LOCATED_IN_SUBSTAGE` | `audit_evidence` | String | 1246 | 是 |
| `LOCATED_IN_SUBSTAGE` | `audit_method` | String | 185 | 否 |
| `LOCATED_IN_SUBSTAGE` | `audit_model` | String | 1246 | 是 |
| `LOCATED_IN_SUBSTAGE` | `audit_reason` | String | 1246 | 是 |
| `LOCATED_IN_SUBSTAGE` | `audit_reviewed_at` | DateTime | 1246 | 是 |
| `LOCATED_IN_SUBSTAGE` | `audit_status` | String | 1246 | 是 |
| `LOCATED_IN_SUBSTAGE` | `audited_at` | DateTime | 185 | 否 |
| `LOCATED_IN_SUBSTAGE` | `confidence` | String | 1246 | 是 |
| `LOCATED_IN_SUBSTAGE` | `evidence` | String | 1246 | 是 |
| `LOCATED_IN_SUBSTAGE` | `match_basis` | String | 185 | 否 |
| `LOCATED_IN_SUBSTAGE` | `needs_review` | Boolean | 1246 | 是 |
| `LOCATED_IN_SUBSTAGE` | `source_field` | String | 1246 | 是 |
| `LOCATED_IN_SUBSTAGE` | `source_pk` | String | 1061 | 否 |
| `LOCATED_IN_SUBSTAGE` | `source_system` | String | 1246 | 是 |
| `LOCATED_IN_SUBSTAGE` | `status` | String | 1246 | 是 |
| `LOCATED_IN_SUBSTAGE` | `updated_at` | DateTime | 1061 | 否 |
| `UPSTREAM_OF` | `description` | String | 121 | 是 |
| `UPSTREAM_OF` | `relation_type` | String | 121 | 是 |

## 挂载审计批次

| 节点类型 | 批次 | 修正批次 | 节点数 |
|---|---|---|---:|
| `MountAuditSnapshot` | `mount-audit-20260810-v1` | `-` | 506 |
| `MountAuditDecision` | `mount-direct-profile-20260810-v1` | `mount-direct-profile-correction-20260810-v1` | 7 |
| `MountAuditDecision` | `mount-direct-profile-20260810-v1` | `-` | 499 |

## 重建入口

- 约束和用户索引：`neo4j/cypher/current_schema.cypher`
- 基础图谱和当前挂载：`neo4j/cypher/import_finegrain_base.cypher`
- 标准中间表：`data/mappings/*.csv`、`data/staging/*.csv`
- `Enterprise.embedding` 向量值和两个审计节点类型的数据未写入标准中间表；本快照记录其结构、数量和批次。
