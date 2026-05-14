MATCH (e:Enterprise {id:'ENT_B881DA0DA218'})
SET e.name='希烽光电科技（南京）有限公司',
    e.source_file='company-info_with_url.xlsx',
    e.core_technology='硅光子集成技术、FMCW（调频连续波）激光雷达芯片技术、光学相控阵（OPA）技术、光电芯片设计与封装测试技术。',
    e.technology_maturity='处于研发到小批量试产阶段。核心硅光芯片已完成流片验证，正向车规级量产和系统级集成推进。',
    e.possible_scenarios='消费电子（AR/VR 3D传感）、智慧城市与安防监控流量检测、无人机低空避障、低轨卫星通信。',
    e.business_model='B2B（Fabless模式）。主要通过研发设计光电芯片，交由代工厂生产后，向客户销售芯片或光引擎模组；或提供NRE（定制研发）服务。',
    e.delivery_capability='具备工程样片及小批量交付能力。大规模量产交付高度依赖外部硅光Fab（代工厂）的产能及自身车规级封测产线的建设进度。',
    e.certification_ip='拥有多项硅光子集成、激光雷达芯片相关的发明专利；属于科技型中小企业。车规级AEC-Q系列认证预估在推进中。',
    e.founder_team_and_gap='团队：由海归硅光子领域资深博士及行业专家组成，具备深厚的硅光芯片设计、流片及产业化经验。短板：Fabless模式下流片成本极高，资金消耗快；作为初创企业，缺乏大规模车规级量产及工程化交付的历史经验；市场教育及客户验证周期长。',
    e.recent_revenue_profit='',
    e.competition_and_diff='竞对：洛微科技、识光微电子，以及海外的SiLC Technologies、Aeva等。技术差异：希烽光电侧重于通过硅光工艺实现极高集成度的FMCW与OPA单片集成，旨在从底层芯片架构上大幅降低激光雷达的BOM成本、功耗及体积，抗干扰能力更强。',
    e.match_level='手工补录',
    e.website_url='';

MERGE (p1:Product {id:'PROD_XF_001'}) SET p1.name='硅光集成芯片';
MERGE (p2:Product {id:'PROD_XF_002'}) SET p2.name='固态激光雷达发射/接收光引擎芯片';
MERGE (p3:Product {id:'PROD_XF_003'}) SET p3.name='FMCW激光雷达扫描芯片';
MERGE (p4:Product {id:'PROD_XF_004'}) SET p4.name='光通信硅光芯片';
MERGE (e)-[:PROVIDES_PRODUCT]->(p1)
MERGE (e)-[:PROVIDES_PRODUCT]->(p2)
MERGE (e)-[:PROVIDES_PRODUCT]->(p3)
MERGE (e)-[:PROVIDES_PRODUCT]->(p4)

MERGE (c1:Capability {id:'CAP_XF_001'}) SET c1.name='硅光子集成技术';
MERGE (c2:Capability {id:'CAP_XF_002'}) SET c2.name='FMCW激光雷达芯片技术';
MERGE (c3:Capability {id:'CAP_XF_003'}) SET c3.name='光学相控阵（OPA）技术';
MERGE (c4:Capability {id:'CAP_XF_004'}) SET c4.name='光电芯片设计与封装测试技术';
MERGE (e)-[:HAS_CAPABILITY]->(c1)
MERGE (e)-[:HAS_CAPABILITY]->(c2)
MERGE (e)-[:HAS_CAPABILITY]->(c3)
MERGE (e)-[:HAS_CAPABILITY]->(c4)

MERGE (i1:Industry {id:'IND_XF_001'}) SET i1.name='智能汽车/自动驾驶';
MERGE (i2:Industry {id:'IND_XF_002'}) SET i2.name='机器人';
MERGE (i3:Industry {id:'IND_XF_003'}) SET i3.name='光通信/数据中心';
MERGE (e)-[:SERVES_INDUSTRY]->(i1)
MERGE (e)-[:SERVES_INDUSTRY]->(i2)
MERGE (e)-[:SERVES_INDUSTRY]->(i3)

MERGE (s1:Scenario {id:'SCN_XF_001'}) SET s1.name='车载高级辅助驾驶与自动驾驶避障导航';
MERGE (s2:Scenario {id:'SCN_XF_002'}) SET s2.name='工业机器视觉';
MERGE (s3:Scenario {id:'SCN_XF_003'}) SET s3.name='数据中心内部高速数据传输';
MERGE (e)-[:APPLIES_TO_SCENARIO]->(s1)
MERGE (e)-[:APPLIES_TO_SCENARIO]->(s2)
MERGE (e)-[:APPLIES_TO_SCENARIO]->(s3)

MERGE (d1:DemandTag {id:'DEM_XF_001'}) SET d1.name='产业资本';
MERGE (d2:DemandTag {id:'DEM_XF_002'}) SET d2.name='车企或Tier1联合开发项目';
MERGE (d3:DemandTag {id:'DEM_XF_003'}) SET d3.name='稳定的硅光晶圆代工产能与先进制程支持';
MERGE (e)-[:HAS_DEMAND]->(d1)
MERGE (e)-[:HAS_DEMAND]->(d2)
MERGE (e)-[:HAS_DEMAND]->(d3);
