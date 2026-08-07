#!/usr/bin/env python3
"""
通用被投企业合作匹配引擎

给定任意目标企业（可在或不在知识图谱中），自动找出被投企业中可合作的对象。
核心逻辑与行业无关：领域关键词映射 → PG 筛选 → Neo4j 交叉 → 多维度评分 → 路径生成。

切换领域只需在 DOMAIN_KEYWORD_MAP 和 DOMAIN_NEEDS 中添加一行，无需改动核心代码。

数据源：
  - PostgreSQL companies 表 (is_invested=true) → 判定被投身份
  - Neo4j Enterprise 节点 + 产业链挂载关系 → 提供企业画像和产业链位置

用法：
    python match_invested_partners.py "目标企业名"
    python match_invested_partners.py "目标企业名" --domain 半导体 --city 上海
    python match_invested_partners.py "目标企业名" --domain 新能源 --json result.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass, field
from typing import Optional

import psycopg2
from neo4j import GraphDatabase
from psycopg2.extras import RealDictCursor

# ── 配置 ──────────────────────────────────────────────

PG_DSN = os.getenv("PG_DSN", "postgresql://postgres:postgres@127.0.0.1:5432/ceo_brief")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7688")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4j2026")

# ── 领域→行业关键词映射表 ──────────────────────────────

DOMAIN_KEYWORD_MAP: dict[str, list[str]] = {
    "商业航天": [
        "航天", "商业航天", "航空航天", "卫星", "火箭", "航天设备",
        "卫星通信", "卫星遥感", "卫星导航", "航天动力", "空间",
    ],
    "半导体": [
        "半导体", "集成电路", "芯片", "晶圆", "先进封装",
        "光刻", "EDA", "IP", "射频", "功率器件",
    ],
    "新能源": [
        "新能源", "光伏", "储能", "动力电池", "锂电",
        "钠离子", "液流电池", "氢能", "燃料电池",
    ],
    "军工": [
        "军工", "国防", "武器装备", "军用", "导弹",
        "雷达", "电子对抗", "精确制导",
    ],
    "机器人": [
        "机器人", "人形机器人", "工业机器人", "具身智能",
        "协作机器人", "四足", "灵巧手",
    ],
    "光刻机": [
        "光刻", "半导体设备", "光学", "激光", "精密机械",
        "光学元件", "光学系统", "紫外",
    ],
    "低空经济": [
        "无人机", "eVTOL", "低空", "飞行汽车", "垂直起降",
        "城市空中交通", "通用航空",
    ],
}


# ── 领域→需求关键词映射表 ──────────────────────────────
# 每个领域的目标企业常见配套需求，用于 Step 5 评分中的"业务相关性"维度。
# 与 DOMAIN_KEYWORD_MAP 配套使用：前者用于 PG 粗筛，后者用于精排。

DOMAIN_NEEDS: dict[str, list[str]] = {
    "商业航天": ["卫星制造", "火箭动力", "测运控", "轻量化材料", "电源系统", "星载通信", "推进"],
    "半导体":   ["晶圆制造", "封装测试", "设备零部件", "半导体材料", "EDA工具", "检测量测"],
    "新能源":   ["电池材料", "BMS", "热管理", "逆变器", "系统集成", "储能"],
    "军工":     ["核心器件", "特种材料", "测试验证", "精密加工", "制导控制"],
    "机器人":   ["减速器", "伺服电机", "传感器", "控制器", "AI算法", "灵巧手"],
    "光刻机":   ["光学系统", "光源", "精密运动台", "特种材料", "检测量测"],
    "低空经济": ["飞控系统", "动力电池", "复合材料", "导航", "适航认证"],
}


def auto_detect_domain(target_name: str, target_desc: str = "") -> str:
    """根据目标企业名称和描述自动判定领域。"""
    combined = target_name + " " + target_desc
    scores: dict[str, int] = {}
    for domain, keywords in DOMAIN_KEYWORD_MAP.items():
        scores[domain] = sum(1 for kw in keywords if kw in combined)
    if not scores or max(scores.values()) == 0:
        return "半导体"  # 默认
    return max(scores, key=scores.get)


def get_industry_keywords(domain: str) -> list[str]:
    """获取某领域的行业关键词列表，用于 PG SQL 查询。"""
    return DOMAIN_KEYWORD_MAP.get(domain, DOMAIN_KEYWORD_MAP["半导体"])


# ── 数据结构 ──────────────────────────────────────────

@dataclass
class CompanyMatch:
    """一条匹配结果。"""
    name: str
    capabilities: list[str] = field(default_factory=list)
    products: list[str] = field(default_factory=list)
    industries: list[str] = field(default_factory=list)
    customers: list[str] = field(default_factory=list)
    city: str = ""
    score: float = 0.0
    tier: str = ""  # P0 / P1 / P2
    rationale: str = ""


# ── 步骤 1：获取目标企业画像 ──────────────────────────

def build_target_profile(
    name: str,
    domain: Optional[str] = None,
    desc: str = "",
    city: str = "",
) -> dict:
    """
    构建目标企业画像。
    优先从 PG 读取，若无则使用用户提供的描述 + 自动推断。
    """
    profile: dict = {
        "name": name,
        "domain": domain or auto_detect_domain(name, desc),
        "desc": desc,
        "city": city,
        "keywords": [],
        "needs": [],
        "mode": "整机集成商",
    }

    # 尝试从 PG 读取
    try:
        conn = psycopg2.connect(PG_DSN)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            "SELECT industry, core_tech, products, scenario, city FROM companies WHERE name = %s",
            (name,),
        )
        row = cur.fetchone()
        if row:
            profile["desc"] = f"行业: {row['industry'] or ''}; 技术: {row['core_tech'] or ''}; 产品: {row['products'] or ''}"
            profile["city"] = row["city"] or city
            profile["keywords"] = _extract_keywords(row["industry"] or "")
            profile["needs"] = _infer_needs(profile)
            cur.close()
            conn.close()
            print(f"  ✓ 目标企业在 PG 中有记录")
            return profile
        cur.close()
        conn.close()
    except Exception as e:
        print(f"  ⚠ PG 查询失败: {e}")

    # 不在 PG 中 — 使用提供的描述 + 关键词
    profile["keywords"] = _extract_keywords(desc)
    profile["needs"] = _infer_needs(profile)
    print(f"  ⚠ 目标企业不在 PG 中，使用描述推断画像")
    return profile


def _extract_keywords(text: str) -> list[str]:
    """从文本中提取中文关键词（简易实现）。"""
    if not text:
        return []
    # 去掉标点，按逗号/分号/空格等拆分
    parts = re.split(r"[，,；;、\s/]+", text)
    keywords = [p.strip() for p in parts if len(p.strip()) >= 2]
    return keywords[:10]


def _infer_needs(profile: dict) -> list[str]:
    """根据目标企业的领域，从 DOMAIN_NEEDS 中取预设需求关键词。"""
    return DOMAIN_NEEDS.get(profile.get("domain", ""), ["核心零部件", "材料", "测试验证"])


# ── 步骤 2-3：PG 筛选被投企业 ─────────────────────────

def query_invested_companies(industry_keywords: list[str]) -> list[dict]:
    """从 PG 中查询 is_invested=true 且行业匹配的企业。"""
    if not industry_keywords:
        return []

    # 构建 ILIKE 条件
    conditions = " OR ".join(
        f"industry ILIKE '%{kw}%'" for kw in industry_keywords[:8]
    )
    sql = f"""
        SELECT name, industry, core_tech, products, scenario, customers, city
        FROM companies
        WHERE is_invested = true
          AND ({conditions})
        ORDER BY name
    """

    try:
        conn = psycopg2.connect(PG_DSN)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        print(f"  ✓ PG 查询到 {len(rows)} 家被投企业")
        return rows
    except Exception as e:
        print(f"  ✗ PG 查询失败: {e}")
        return []


# ── 步骤 4：Neo4j 交叉匹配 ─────────────────────────────

def query_neo4j_for_companies(names: list[str]) -> list[dict]:
    """
    批量查询 v2 Neo4j，获取企业画像及其产业链挂载信息。
    """
    if not names:
        return []

    query = """
    UNWIND $names AS company_name
    MATCH (e:Enterprise {enterprise_name: company_name})
    OPTIONAL MATCH (e)-[:LOCATED_IN_SUBSTAGE]->(s:ChainSubstage)
    OPTIONAL MATCH (s)<-[:HAS_SUBSTAGE]-(st:ChainStage)
    OPTIONAL MATCH (st)<-[:HAS_STAGE]-(seg:ChainSegment)
    OPTIONAL MATCH (seg)<-[:HAS_SEGMENT]-(chain:IndustryChain)
    RETURN e.enterprise_name AS name,
           e.core_tech AS core_tech_neo4j,
           e.products AS products_neo4j,
           collect(DISTINCT s.substage_name)[0..5] AS capabilities,
           collect(DISTINCT chain.chain_name)[0..3] AS industries
    ORDER BY name
    """
    driver = GraphDatabase.driver(
        NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)
    )
    try:
        with driver.session() as session:
            rows = [dict(row) for row in session.run(query, names=names)]
    finally:
        driver.close()

    print(f"  ✓ Neo4j 返回 {len(rows)} 条匹配")
    return rows


def cross_reference(
    pg_companies: list[dict],
    neo4j_data: list[dict],
) -> tuple[list[dict], list[dict], list[dict]]:
    """
    交叉引用 PG 和 Neo4j 数据。
    返回 (matched, pg_only, neo4j_only)
    """
    pg_names = {c["name"] for c in pg_companies}
    neo4j_names = {d["name"] for d in neo4j_data}

    neo4j_dict = {d["name"]: d for d in neo4j_data}
    pg_dict = {c["name"]: c for c in pg_companies}

    matched_names = pg_names & neo4j_names
    pg_only_names = pg_names - neo4j_names
    neo4j_only_names = neo4j_names - pg_names

    # 合并数据
    matched = []
    for name in matched_names:
        merged = {**pg_dict[name], **neo4j_dict[name]}
        merged["source"] = "both"
        matched.append(merged)

    pg_only = []
    for name in pg_only_names:
        entry = {**pg_dict[name], "source": "pg_only"}
        pg_only.append(entry)

    neo4j_only = []
    for name in neo4j_only_names:
        entry = {**neo4j_dict[name], "source": "neo4j_only"}
        neo4j_only.append(entry)

    print(f"  ✓ 交叉匹配：PG∩Neo4j={len(matched)}, PG_only={len(pg_only)}, Neo4j_only={len(neo4j_only)}")
    return matched, pg_only, neo4j_only


# ── 步骤 5：评分 ──────────────────────────────────────

def score_company(company: dict, target_profile: dict) -> CompanyMatch:
    """
    对一家企业进行合作匹配度评分。
    返回带分数和分级的 CompanyMatch。
    """
    score = 0.0
    reasons: list[str] = []

    def _to_list(val):
        if isinstance(val, list):
            return [v for v in val if isinstance(v, str)]
        if isinstance(val, str) and val:
            return re.split(r'[，,;；、]+', val)
        return []
    # 拼接所有文本字段（处理 str 和 list 两种类型）
    def _safe_join(val):
        if isinstance(val, list):
            return " ".join(v for v in val if isinstance(v, str))
        return str(val) if val else ""

    all_text = " ".join(
        _safe_join(company.get(k, ""))
        for k in [
            "industry",
            "core_tech",
            "core_tech_neo4j",
            "products",
            "scenario",
            "customers",
        ]
    )
    all_text += " " + " ".join(
        v for v in company.get("capabilities", []) if isinstance(v, str)
    )
    all_text += " " + _safe_join(
        company.get("products_neo4j", company.get("products", []))
    )
    all_text += " " + " ".join(
        v for v in company.get("industries", []) if isinstance(v, str)
    )
    needs = target_profile.get("needs", [])
    keywords = target_profile.get("keywords", [])

    # 补充领域行业关键词
    domain_kw = get_industry_keywords(target_profile.get("domain", ""))
    all_keywords = list(set(needs + keywords + domain_kw))

    # 维度1：业务相关性 (40%)
    hit_count = 0
    for kw in all_keywords:
        if len(kw) >= 2 and kw in all_text:
            hit_count += 1
    relevance = min(hit_count / max(len(all_keywords), 1), 1.0) * 0.40
    if hit_count >= 3:
        reasons.append(f"高业务相关性({hit_count}项关键词命中)")
    score += relevance

    # 维度2：产业链位置 (25%)
    # 整机集成商 → 需要上游供应商（有产品/能力的更匹配）
    mode = target_profile.get("mode", "")
    has_products = bool(company.get("products_neo4j")) or bool(company.get("products"))
    has_capabilities = bool(company.get("capabilities"))
    if mode in ("整机集成商", "系统集成商"):
        # 有具体产品/能力的供应商加分
        if has_products and has_capabilities:
            score += 0.25
            reasons.append("直接上游供应商(有产品+能力)")
        elif has_products or has_capabilities:
            score += 0.15
            reasons.append("潜在供应商")
    else:
        # 零部件商 → 需要下游集成商或互补技术
        score += 0.10

    # 维度3：地理邻近性 (15%)
    target_city = target_profile.get("city", "")
    company_city = company.get("city", "")
    if target_city and company_city:
        if target_city in company_city or company_city in target_city:
            score += 0.15
            reasons.append(f"同城({company_city})")
        elif target_city[:2] == company_city[:2]:
            score += 0.08
            reasons.append(f"同省({company_city[:2]})")

    # 维度4：技术稀缺性 (10%)
    # 启发式：能力/产品带有"国内唯一"/"首款"/"独家"等
    rare_signals = ["国内唯一", "首款", "首个", "独家", "国际首创", "唯一"]
    for signal in rare_signals:
        if signal in all_text:
            score += 0.10
            reasons.append(f"技术稀缺({signal})")
            break

    # 维度5：数据完整度 (10%)
    field_count = sum(
        1
        for k in [
            "industry",
            "core_tech",
            "products",
            "scenario",
            "capabilities",
            "industries",
            "customers",
        ]
        if company.get(k)
    )
    score += 0.10 * min(field_count / 5, 1.0)

    # 分级
    if score >= 0.55:
        tier = "🔴 P0"
    elif score >= 0.40:
        tier = "🟡 P1"
    else:
        tier = "🟢 P2"

    cm = CompanyMatch(
        name=company["name"],
        capabilities=company.get("capabilities", []) or [],
        products=_to_list(company.get("products_neo4j")) or _to_list(company.get("products")),
        industries=company.get("industries", []),
        customers=company.get("customers", []),
        city=company.get("city", ""),
        score=round(score, 3),
        tier=tier,
        rationale="; ".join(reasons) if reasons else "一般匹配",
    )
    return cm


# ── 步骤 6：生成合作路径 ──────────────────────────────

def generate_pathways(
    scored: list[CompanyMatch],
    target_profile: dict,
) -> list[dict]:
    """根据评分结果生成合作路径建议。"""
    p0 = [m for m in scored if m.tier == "🔴 P0"]
    p1 = [m for m in scored if m.tier == "🟡 P1"]
    all_good = p0 + p1
    pathways = []

    # 路径规则1：每个需求方向取 top-3
    needs = target_profile.get("needs", [])
    if len(needs) >= 2 and len(p0) >= 2:
        # 取两个最大需求方向的前3家
        top = p0[:3] + p1[:3]
        pathways.append({
            "name": f"核心需求覆盖路径",
            "companies": [m.name for m in top],
            "rationale": f"覆盖 {needs[0]} 和 {needs[1]} 两个核心方向的最优供应商",
        })

    # 路径规则2：同城产业链
    target_city = target_profile.get("city", "")
    if target_city:
        local = [m for m in all_good if target_city in m.city or m.city in target_city]
        if len(local) >= 3:
            pathways.append({
                "name": f"{target_city}本地产业链闭环",
                "companies": [m.name for m in local[:6]],
                "rationale": f"全部位于{target_city}，物流和协作半径最优",
            })

    # 路径规则3：技术栈互补组合
    tech_groups = _group_by_tech(all_good)
    for group_name, members in tech_groups.items():
        if len(members) >= 3:
            pathways.append({
                "name": f"{group_name}技术栈",
                "companies": [m.name for m in members],
                "rationale": f"{group_name}方向互补技术打包",
            })

    # 去重，取前3条路径
    seen = set()
    unique_pathways = []
    for p in pathways:
        key = tuple(sorted(p["companies"]))
        if key not in seen:
            seen.add(key)
            unique_pathways.append(p)

    return unique_pathways[:3]


def _group_by_tech(matches: list[CompanyMatch]) -> dict[str, list[CompanyMatch]]:
    """按技术方向分组。"""
    groups: dict[str, list[CompanyMatch]] = {}

    tech_markers = {
        "通信组网": ["通信", "组网", "激光", "终端", "天线", "相控阵"],
        "卫星平台": ["卫星", "整星", "平台", "星座", "ODM"],
        "火箭动力": ["火箭", "推进", "发动机", "液体", "固体"],
        "材料结构": ["材料", "合金", "复合", "钛", "碳纤维", "防热"],
        "测试验证": ["检测", "试验", "测试", "仿真", "电磁"],
        "电源能源": ["电池", "电源", "储能"],
        "控制执行": ["伺服", "驱动", "作动器"],
        "光学载荷": ["光学", "镜头", "红外", "相机", "成像"],
    }

    for m in matches:
        all_text = " ".join(m.capabilities + m.products + m.industries)
        for group, markers in tech_markers.items():
            if any(kw in all_text for kw in markers):
                groups.setdefault(group, []).append(m)
                break

    return groups


# ── 主流程 ────────────────────────────────────────────

def match_partners(
    target_name: str,
    domain: Optional[str] = None,
    desc: str = "",
    city: str = "",
) -> dict:
    """
    主入口：给定目标企业名称，返回匹配结果。
    """
    print(f"\n{'='*60}")
    print(f"  目标企业: {target_name}")
    print(f"{'='*60}\n")

    # Step 1: 目标画像
    print("[Step 1] 构建目标企业画像...")
    profile = build_target_profile(target_name, domain, desc, city)
    print(f"  领域: {profile['domain']}")
    print(f"  城市: {profile.get('city', '未知')}")
    print(f"  需求: {profile['needs'][:5]}")

    # Step 2-3: PG 筛选被投企业
    print("\n[Step 2-3] 从 PG 筛选被投企业...")
    industry_keywords = get_industry_keywords(profile["domain"])
    print(f"  行业关键词: {industry_keywords[:5]}...")
    pg_companies = [
        company
        for company in query_invested_companies(industry_keywords)
        if company["name"] != target_name
    ]

    if not pg_companies:
        print("  ✗ 没有找到任何被投企业")
        return {"profile": profile, "matches": [], "pg_only": [], "pathways": []}

    # Step 4: Neo4j 交叉匹配
    print("\n[Step 4] Neo4j 交叉匹配...")
    pg_names = [c["name"] for c in pg_companies]
    neo4j_data = query_neo4j_for_companies(pg_names)
    matched, pg_only, neo4j_only = cross_reference(pg_companies, neo4j_data)

    # Step 5: 评分
    print("\n[Step 5] 评分 & 分级...")
    scored = [score_company(c, profile) for c in matched]
    scored.sort(key=lambda x: x.score, reverse=True)

    p0_count = sum(1 for m in scored if m.tier == "🔴 P0")
    p1_count = sum(1 for m in scored if m.tier == "🟡 P1")
    p2_count = sum(1 for m in scored if m.tier == "🟢 P2")
    print(f"  ✓ P0={p0_count}, P1={p1_count}, P2={p2_count}")

    # Step 6: 合作路径
    print("\n[Step 6] 生成合作路径...")
    pathways = generate_pathways(scored, profile)

    return {
        "profile": profile,
        "matches": scored,
        "pg_only": pg_only,
        "pathways": pathways,
    }


# ── 输出 ──────────────────────────────────────────────

def print_report(result: dict) -> None:
    """格式化打印匹配报告。"""
    profile = result["profile"]
    matches = result["matches"]
    pg_only = result["pg_only"]
    pathways = result["pathways"]

    print(f"\n{'='*60}")
    print(f"  📋 合作匹配报告：{profile['name']}")
    print(f"{'='*60}")
    print(f"  领域: {profile['domain']}")
    print(f"  城市: {profile.get('city', '未知')}")
    print(f"  需求: {' | '.join(profile.get('needs', [])[:5])}")
    print()

    # P0
    p0 = [m for m in matches if m.tier == "🔴 P0"]
    if p0:
        print(f"## 🔴 P0 — 核心战略合作 ({len(p0)} 家)")
        print()
        for m in p0[:15]:
            cap_preview = "、".join(m.capabilities[:3]) if m.capabilities else "—"
            prod_preview = "、".join(m.products[:2]) if m.products else "—"
            print(f"| **{m.name}** | {m.score} | {m.rationale} |")
            print(f"  能力: {cap_preview}")
            print(f"  产品: {prod_preview}")
            if m.city:
                print(f"  城市: {m.city}")
            print()

    # P1
    p1 = [m for m in matches if m.tier == "🟡 P1"]
    if p1:
        print(f"## 🟡 P1 — 关键配套 ({len(p1)} 家)")
        print()
        for m in p1[:20]:
            cap_preview = "、".join(m.capabilities[:2]) if m.capabilities else "—"
            prod_preview = "、".join(m.products[:2]) if m.products else "—"
            city_tag = f" [{m.city}]" if m.city else ""
            print(f"| **{m.name}**{city_tag} | {m.score} | {m.rationale} |")
        print()

    # P2 只统计
    p2_count = sum(1 for m in matches if m.tier == "🟢 P2")
    if p2_count:
        print(f"## 🟢 P2 — 潜力合作 ({p2_count} 家，不逐条展示)")
        print()

    # PG-only
    if pg_only:
        print(f"## ⚠️ 被投但 Neo4j 无数据 ({len(pg_only)} 家，需另外调研)")
        for c in pg_only:
            print(f"  - {c['name']} ({c.get('city', '?')})")
        print()

    # 合作路径
    if pathways:
        print(f"## 🎯 推荐合作路径 ({len(pathways)} 条)")
        print()
        for i, p in enumerate(pathways, 1):
            print(f"### 路径 {i}：{p['name']}")
            print(f"> {p['rationale']}")
            for name in p["companies"][:6]:
                print(f"  - {name}")
            print()


def save_json(result: dict, output_path: str) -> None:
    """保存结果到 JSON 文件。"""
    serializable = {
        "profile": result["profile"],
        "matches": [
            {
                "name": m.name,
                "score": m.score,
                "tier": m.tier,
                "rationale": m.rationale,
                "capabilities": m.capabilities,
                "products": m.products,
            }
            for m in result["matches"]
        ],
        "pg_only": [{"name": c["name"], "city": c.get("city", "")} for c in result["pg_only"]],
        "pathways": result["pathways"],
    }
    with open(output_path, "w") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)
    print(f"\n  💾 结果已保存: {output_path}")


# ── CLI ───────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="被投企业合作匹配引擎",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python match_invested_partners.py "西部航天科技（陕西）集团有限公司" --city 西安
  python match_invested_partners.py "南京芯邺科技有限公司" --domain 半导体 --desc "半导体封测代工厂" --city 南京
  python match_invested_partners.py "某光刻机光源企业" --domain 光刻机
        """,
    )
    parser.add_argument("target", help="目标企业名称")
    parser.add_argument("--domain", help="领域 (商业航天/半导体/新能源/军工/机器人/光刻机/低空经济)")
    parser.add_argument("--desc", default="", help="目标企业描述（不在数据库中时使用）")
    parser.add_argument("--city", default="", help="目标企业所在城市（用于地理邻近评分）")
    parser.add_argument("--json", default="", help="输出 JSON 文件路径")
    args = parser.parse_args()

    result = match_partners(
        target_name=args.target,
        domain=args.domain,
        desc=args.desc,
        city=args.city,
    )

    print_report(result)

    if args.json:
        save_json(result, args.json)


if __name__ == "__main__":
    main()
