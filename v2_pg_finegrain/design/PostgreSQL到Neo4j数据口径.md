# PostgreSQL 到 Neo4j 数据口径

## 1. 总体口径

PostgreSQL 是新版企业与业务事实的数据源，Neo4j 是图谱查询和关系展示服务。两者之间通过标准中间表衔接。

不建议当前阶段做实时同步。

## 2. 标准中间表

### chain_master.csv

产业链主数据，所有产业链平级维护。

关键字段：

- `chain_id`
- `domain_name`
- `chain_name`
- `maturity_level`
- `pilot_flag`

### chain_segments.csv

产业链分段。

关键字段：

- `segment_id`
- `chain_id`
- `segment_name`
- `segment_order`

### chain_stages.csv

一级环节。

关键字段：

- `stage_id`
- `chain_id`
- `segment_id`
- `stage_name`
- `stage_order`
- `definition`
- `include_criteria`
- `exclude_criteria`
- `keywords`

### chain_substages.csv

二级细分环节。

关键字段：

- `substage_id`
- `stage_id`
- `substage_name`
- `definition`
- `keywords`

### enterprises.csv

企业标准表。

关键字段：

- `enterprise_id`
- `enterprise_name`
- `source_system`
- `source_pk`
- `is_invested`

### enterprise_to_substage.csv

企业到二级细分环节的挂接关系。

关键字段：

- `enterprise_id`
- `substage_id`
- `confidence`
- `evidence`
- `source_field`
- `needs_review`

可选审计字段：

- `source`
- `source_pk`
- `updated_at`

## 3. PostgreSQL 抽取建议

优先抽取以下字段：

- 企业名称
- 主营业务
- 产品名称
- 技术关键词
- 应用场景
- 客户行业
- 融资材料摘要
- 官网或资料来源 URL

## 4. 复核规则

以下情况必须进入人工复核：

- 仅能判断产业链，不能判断一级环节。
- 只能判断一级环节，不能判断二级细分环节。
- 同一企业可挂多个细分环节，但证据不足。
- 企业描述来自大模型推断，缺少原始字段支撑。
