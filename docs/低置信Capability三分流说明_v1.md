# 低置信 Capability 三分流说明（v1）

对应文件：
- `data/mappings/capability_low_confidence_triage_v1.csv`

## 1. 目的
在高置信 Capability 已并入 `unified_rel_capability_to_keycapability_v2.csv` 后，剩下的低置信能力不应继续混放在一个候选池里。

因此本轮把它们拆成三类：
1. **正式并入候选**
2. **保留候选**
3. **转 TechDirection**

---

## 2. 三类定义

### 2.1 正式并入候选
定义：
- 虽然置信度不高于 0.80
- 但语义上已经比较稳定地落在某个 KeyCapability 上
- 且已有企业案例可以支撑

当前代表：
- 贴片机等 -> 规模制造与交付能力
- 精密驱动技术 -> 高精度加工控制能力

### 2.2 保留候选
定义：
- 目前看起来能映射，但还缺更多样本或更稳定规则
- 暂不适合直接写进正式映射表

当前代表：
- 时间门控成像
- 激光穿透成像
- 高精度晶圆键合
- 光谱分析探测芯片
- 空间微振动控制技术

### 2.3 转 TechDirection
定义：
- 这类内容更像“技术主题/底层工艺/技术路线”
- 不像“可交付能力”
- 如果硬塞到 KeyCapability，会让能力层失真

当前代表：
- 单光子探测
- 皮秒级时间分辨
- 片上光电集成芯片技术
- 晶体外延技术
- 通信光交换芯片

---

## 3. 当前最重要的建模判断
统一图谱中的：
- **KeyCapability** 应该表示企业可交付、可解释、可推荐的能力
- **TechDirection** 更适合承载底层技术路线、核心工艺、探测原理、芯片技术方向

如果不做这层分流，后面会出现：
- 能力层混入大量底层技术名词
- 推荐逻辑变成“技术词相似”，而不是“能力可交付”
- 场景推荐与环节推荐失真

---

## 4. 当前结论
本轮建议：
- 不再继续把低置信能力一股脑往 KeyCapability 塞
- 先明确哪些可以下一轮进入 v3
- 哪些继续保留
- 哪些应该等待 TechDirection 主数据正式建立

---

## 5. 下一步建议
1. 基于 `capability_low_confidence_triage_v1.csv` 先生成 TechDirection 候选表
2. 把“正式并入候选”整理成 `unified_rel_capability_to_keycapability_v3.csv`
3. 再跑一次 Neo4j 导入和回查验证

---

## 6. 一句话结论

> 低置信 Capability 不是“再纠结一下就能直接并入”，其中一部分本来就不该在 KeyCapability 层，而应转入 TechDirection。
