# 当前 Neo4j 结构快照

> 数据来源：Docker 容器 `neo4j-kg-v2-finegrain`。
> 生成时间：`2026-09-18T06:12:43.648003+00:00`。
> 本文件由 `scripts/sync_project_from_neo4j.py` 生成；属性“完整”表示当前该类型的所有实体都包含该属性，不代表存在性约束。

## 节点类型

| 标签 | 当前节点数 |
|---|---:|
| `ChainSegment` | 27 |
| `ChainStage` | 130 |
| `ChainSubstage` | 496 |
| `Enterprise` | 530 |
| `IndustryChain` | 9 |
| `MountAuditDecision` | 767 |
| `MountAuditSnapshot` | 506 |

## 关系类型

| 类型 | 当前关系数 |
|---|---:|
| `HAS_SEGMENT` | 27 |
| `HAS_STAGE` | 130 |
| `HAS_SUBSTAGE` | 496 |
| `LOCATED_IN_SUBSTAGE` | 467 |
| `UPSTREAM_OF` | 140 |

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
| `ChainSegment` | `updated_at` | DateTime | 3 | 否 |
| `ChainStage` | `chain_id` | String | 130 | 是 |
| `ChainStage` | `definition` | String | 130 | 是 |
| `ChainStage` | `exclude_criteria` | String | 130 | 是 |
| `ChainStage` | `include_criteria` | String | 130 | 是 |
| `ChainStage` | `keywords` | String | 130 | 是 |
| `ChainStage` | `segment_id` | String | 130 | 是 |
| `ChainStage` | `stage_id` | String | 130 | 是 |
| `ChainStage` | `stage_name` | String | 130 | 是 |
| `ChainStage` | `stage_order` | Long | 130 | 是 |
| `ChainStage` | `updated_at` | DateTime | 11 | 否 |
| `ChainSubstage` | `chain_id` | String | 27 | 否 |
| `ChainSubstage` | `definition` | String | 496 | 是 |
| `ChainSubstage` | `keywords` | String | 496 | 是 |
| `ChainSubstage` | `stage_id` | String | 496 | 是 |
| `ChainSubstage` | `substage_id` | String | 496 | 是 |
| `ChainSubstage` | `substage_name` | String | 496 | 是 |
| `ChainSubstage` | `updated_at` | DateTime | 27 | 否 |
| `Enterprise` | `cert_ip` | String | 525 | 否 |
| `Enterprise` | `core_tech` | String | 527 | 否 |
| `Enterprise` | `customers` | String | 513 | 否 |
| `Enterprise` | `domain` | String | 525 | 否 |
| `Enterprise` | `embedding` | DoubleArray | 525 | 否 |
| `Enterprise` | `embedding_model` | String | 525 | 否 |
| `Enterprise` | `embedding_text` | String | 525 | 否 |
| `Enterprise` | `embedding_updated_at` | DateTime | 525 | 否 |
| `Enterprise` | `enterprise_id` | String | 530 | 是 |
| `Enterprise` | `enterprise_name` | String | 530 | 是 |
| `Enterprise` | `industry` | String | 512 | 否 |
| `Enterprise` | `is_invested` | Boolean | 526 | 否 |
| `Enterprise` | `last_profile_sync_at` | DateTime | 21 | 否 |
| `Enterprise` | `last_sync_at` | String, DateTime | 530 | 是 |
| `Enterprise` | `products` | String | 522 | 否 |
| `Enterprise` | `profile_source` | String | 21 | 否 |
| `Enterprise` | `scenario` | String | 522 | 否 |
| `Enterprise` | `source_pk` | String | 530 | 是 |
| `Enterprise` | `source_system` | String | 530 | 是 |
| `Enterprise` | `suppliers` | String | 517 | 否 |
| `IndustryChain` | `chain_id` | String | 9 | 是 |
| `IndustryChain` | `chain_name` | String | 9 | 是 |
| `IndustryChain` | `description` | String | 9 | 是 |
| `IndustryChain` | `domain_name` | String | 9 | 是 |
| `IndustryChain` | `maturity_level` | String | 9 | 是 |
| `IndustryChain` | `pilot_flag` | Boolean | 9 | 是 |
| `IndustryChain` | `scope_note` | String | 1 | 否 |
| `IndustryChain` | `source_file` | String | 1 | 否 |
| `IndustryChain` | `updated_at` | DateTime | 1 | 否 |
| `MountAuditDecision` | `action` | String | 261 | 否 |
| `MountAuditDecision` | `audit_batch_id` | String | 261 | 否 |
| `MountAuditDecision` | `batch_id` | String | 506 | 否 |
| `MountAuditDecision` | `chain` | String | 506 | 否 |
| `MountAuditDecision` | `confidence` | String | 506 | 否 |
| `MountAuditDecision` | `correction_batch_id` | String | 7 | 否 |
| `MountAuditDecision` | `decided_at` | DateTime | 767 | 是 |
| `MountAuditDecision` | `decision` | String | 506 | 否 |
| `MountAuditDecision` | `decision_id` | String | 261 | 否 |
| `MountAuditDecision` | `edge_key` | String | 506 | 否 |
| `MountAuditDecision` | `enterprise_id` | String | 767 | 是 |
| `MountAuditDecision` | `enterprise_name` | String | 767 | 是 |
| `MountAuditDecision` | `evidence_quote` | String | 506 | 否 |
| `MountAuditDecision` | `method` | String | 506 | 否 |
| `MountAuditDecision` | `model` | String | 506 | 否 |
| `MountAuditDecision` | `model_confidence` | String | 261 | 否 |
| `MountAuditDecision` | `model_decision` | String | 261 | 否 |
| `MountAuditDecision` | `model_evidence` | String | 261 | 否 |
| `MountAuditDecision` | `model_reason` | String | 261 | 否 |
| `MountAuditDecision` | `previous_audit_status` | String | 261 | 否 |
| `MountAuditDecision` | `previous_confidence` | String | 261 | 否 |
| `MountAuditDecision` | `previous_decision` | String | 7 | 否 |
| `MountAuditDecision` | `previous_reason` | String | 7 | 否 |
| `MountAuditDecision` | `previous_source_system` | String | 261 | 否 |
| `MountAuditDecision` | `previous_status` | String | 261 | 否 |
| `MountAuditDecision` | `reason` | String | 767 | 是 |
| `MountAuditDecision` | `reviewer` | String | 261 | 否 |
| `MountAuditDecision` | `snapshot_batch_id` | String | 506 | 否 |
| `MountAuditDecision` | `substage_id` | String | 767 | 是 |
| `MountAuditDecision` | `substage_name` | String | 767 | 是 |
| `MountAuditDecision` | `support_terms` | StringArray | 506 | 否 |
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
| `LOCATED_IN_SUBSTAGE` | `audit_batch_id` | String | 435 | 否 |
| `LOCATED_IN_SUBSTAGE` | `audit_confidence` | String | 435 | 否 |
| `LOCATED_IN_SUBSTAGE` | `audit_decision` | String | 435 | 否 |
| `LOCATED_IN_SUBSTAGE` | `audit_evidence` | String | 435 | 否 |
| `LOCATED_IN_SUBSTAGE` | `audit_last_action` | String | 261 | 否 |
| `LOCATED_IN_SUBSTAGE` | `audit_method` | String | 193 | 否 |
| `LOCATED_IN_SUBSTAGE` | `audit_model` | String | 435 | 否 |
| `LOCATED_IN_SUBSTAGE` | `audit_reason` | String | 435 | 否 |
| `LOCATED_IN_SUBSTAGE` | `audit_reviewed_at` | DateTime | 435 | 否 |
| `LOCATED_IN_SUBSTAGE` | `audit_status` | String | 451 | 否 |
| `LOCATED_IN_SUBSTAGE` | `audited_at` | DateTime | 174 | 否 |
| `LOCATED_IN_SUBSTAGE` | `confidence` | String | 467 | 是 |
| `LOCATED_IN_SUBSTAGE` | `evidence` | String | 467 | 是 |
| `LOCATED_IN_SUBSTAGE` | `evidence_product` | String | 23 | 否 |
| `LOCATED_IN_SUBSTAGE` | `match_basis` | String | 174 | 否 |
| `LOCATED_IN_SUBSTAGE` | `match_type` | String | 23 | 否 |
| `LOCATED_IN_SUBSTAGE` | `matched_terms` | StringArray | 23 | 否 |
| `LOCATED_IN_SUBSTAGE` | `needs_review` | Boolean | 467 | 是 |
| `LOCATED_IN_SUBSTAGE` | `review_reason` | String | 261 | 否 |
| `LOCATED_IN_SUBSTAGE` | `reviewed_at` | DateTime | 261 | 否 |
| `LOCATED_IN_SUBSTAGE` | `reviewed_by` | String | 261 | 否 |
| `LOCATED_IN_SUBSTAGE` | `source_field` | String | 464 | 否 |
| `LOCATED_IN_SUBSTAGE` | `source_file` | String | 23 | 否 |
| `LOCATED_IN_SUBSTAGE` | `source_pk` | String | 261 | 否 |
| `LOCATED_IN_SUBSTAGE` | `source_record` | String | 23 | 否 |
| `LOCATED_IN_SUBSTAGE` | `source_system` | String | 467 | 是 |
| `LOCATED_IN_SUBSTAGE` | `status` | String | 467 | 是 |
| `LOCATED_IN_SUBSTAGE` | `updated_at` | DateTime | 298 | 否 |
| `UPSTREAM_OF` | `description` | String | 140 | 是 |
| `UPSTREAM_OF` | `relation_type` | String | 121 | 否 |
| `UPSTREAM_OF` | `source_system` | String | 23 | 否 |
| `UPSTREAM_OF` | `updated_at` | DateTime | 23 | 否 |

## 挂载审计批次

| 节点类型 | 批次 | 修正批次 | 节点数 |
|---|---|---|---:|
| `MountAuditSnapshot` | `mount-audit-20260810-v1` | `-` | 506 |
| `MountAuditDecision` | `mount-direct-profile-20260810-v1` | `mount-direct-profile-correction-20260810-v1` | 7 |
| `MountAuditDecision` | `mount-direct-profile-20260810-v1` | `-` | 499 |
| `MountAuditDecision` | `None` | `-` | 261 |

## 重建入口

- 约束和用户索引：`neo4j/cypher/current_schema.cypher`
- 基础图谱和当前挂载：`neo4j/cypher/import_finegrain_base.cypher`
- 标准中间表：`data/mappings/*.csv`、`data/staging/*.csv`
- `Enterprise.embedding` 向量值和两个审计节点类型的数据未写入标准中间表；本快照记录其结构、数量和批次。
