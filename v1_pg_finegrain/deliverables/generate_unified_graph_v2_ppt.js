const pptxgen = require('C:/Users/XCKF/.openclaw/workspace-product/node_modules/pptxgenjs');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'OpenClaw';
pptx.company = 'OpenClaw';
pptx.subject = '统一图谱V2评审汇报';
pptx.title = '统一图谱V2评审汇报';
pptx.lang = 'zh-CN';
pptx.theme = {
  headFontFace: 'Microsoft YaHei',
  bodyFontFace: 'Microsoft YaHei',
  lang: 'zh-CN'
};

const C = {
  navy: '0F2747',
  blue: '1F5EFF',
  cyan: '12B5CB',
  orange: 'FF8A3D',
  gold: 'F5B700',
  text: '1F2937',
  sub: '5B6472',
  light: 'F5F7FB',
  line: 'D7DDEA',
  white: 'FFFFFF',
  green: '21A366'
};

function header(slide, title, page) {
  slide.addShape(pptx.ShapeType.rect, { x:0, y:0, w:13.333, h:0.55, fill:{color:C.navy}, line:{color:C.navy} });
  slide.addText(title, { x:0.5, y:0.14, w:9.8, h:0.28, color:C.white, fontFace:'Microsoft YaHei', fontSize:24, bold:true });
  slide.addShape(pptx.ShapeType.line, { x:0.45, y:7.05, w:12.35, h:0, line:{ color:C.line, pt:1 } });
  slide.addText(String(page), { x:12.2, y:7.08, w:0.45, h:0.15, color:C.sub, fontSize:9, align:'right' });
}

function card(slide, x, y, w, h, title, bullets, color=C.blue) {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h, rectRadius:0.05, fill:{color:C.white}, line:{color:C.line, pt:1} });
  slide.addShape(pptx.ShapeType.rect, { x, y, w, h:0.1, fill:{color}, line:{color} });
  slide.addText(title, { x:x+0.15, y:y+0.18, w:w-0.3, h:0.28, fontSize:18, bold:true, color:C.navy, fontFace:'Microsoft YaHei' });
  slide.addText(bullets.map(t => ({ text:t, options:{ bullet:{indent:14} } })), {
    x:x+0.15, y:y+0.58, w:w-0.3, h:h-0.68, fontSize:13, color:C.text,
    fontFace:'Microsoft YaHei', breakLine:true, paraSpaceAfterPt:10, margin:2, valign:'top'
  });
}

function sectionTitle(slide, text, y=0.95) {
  slide.addText(text, { x:0.7, y, w:12, h:0.35, fontSize:22, bold:true, color:C.navy, fontFace:'Microsoft YaHei' });
}

// 1 cover
{
  const s = pptx.addSlide();
  s.background = { color: 'F7FAFF' };
  s.addShape(pptx.ShapeType.rect, { x:0, y:0, w:13.333, h:7.5, fill:{color:'F7FAFF'}, line:{color:'F7FAFF'} });
  s.addText('统一图谱 V2 阶段成果与范围建议', { x:0.85, y:1.55, w:9.6, h:0.65, fontFace:'Microsoft YaHei', fontSize:26, bold:true, color:C.navy });
  s.addText('——正式核心样板链已稳定，商业航天候选域已完成独立验证', { x:0.9, y:2.28, w:9.8, h:0.35, fontFace:'Microsoft YaHei', fontSize:16, color:C.blue });
  s.addText('企业—能力—技术方向—产业环节统一底座', { x:0.92, y:2.75, w:5.5, h:0.22, fontFace:'Microsoft YaHei', fontSize:11, color:C.sub });
  card(s, 0.95, 4.0, 2.9, 1.45, '正式核心域', ['光学检测 / 机器视觉','光通信 / 光模块','激光加工 / 光学装备'], C.blue);
  card(s, 4.15, 4.0, 2.5, 1.45, '扩展候选域', ['商业航天'], C.cyan);
  card(s, 6.95, 4.0, 2.5, 1.45, '版本建议', ['V2 采用 3+1+储备'], C.orange);
  card(s, 9.75, 4.0, 2.5, 1.45, '当前状态', ['主干可用','扩展可控'], C.gold);
}

// 2 questions
{
  const s = pptx.addSlide(); header(s, '1. 这次汇报重点回答三个问题', 2);
  card(s, 0.8, 1.3, 3.8, 4.2, '问题1', ['统一图谱主干是否已经做实？'], C.blue);
  card(s, 4.75, 1.3, 3.8, 4.2, '问题2', ['统一图谱是否已经具备解释链，而不只是标签库？'], C.cyan);
  card(s, 8.7, 1.3, 3.8, 4.2, '问题3', ['商业航天是否应进入统一图谱 V2？'], C.orange);
  s.addText('今天不是讲“想做什么”，而是讲：已经做成了什么、验证到了哪一步、V2 该怎么拍板。', { x:0.85, y:6.05, w:11.9, h:0.3, fontSize:18, bold:true, color:C.navy, fontFace:'Microsoft YaHei' });
}

// 3 version layering
{
  const s = pptx.addSlide(); header(s, '2. 统一图谱 V2 建议采用分层范围治理', 3);
  card(s, 0.85, 1.25, 3.9, 4.8, 'A层：正式核心域', ['光学检测 / 机器视觉','光通信 / 光模块','激光加工 / 光学装备','特点：主数据、结构、企业挂接、查询、解释链均已验证'], C.blue);
  card(s, 4.9, 1.25, 3.6, 4.8, 'B层：扩展候选域', ['商业航天','特点：候选主数据、候选关系、企业 patch、查询模板均已验证','但样本成熟度仍低于 A层'], C.cyan);
  card(s, 8.7, 1.25, 3.6, 4.8, 'C层：研究储备域', ['其他尚未形成稳定主数据与 patch 验证的新方向','不进入本轮正式建设范围'], C.orange);
  s.addText('结论：V2 建议按“3+1+储备”推进，而不是继续平面扩张。', { x:0.9, y:6.25, w:11.5, h:0.28, fontSize:19, bold:true, color:C.navy, fontFace:'Microsoft YaHei' });
}

// 4 core trunk
{
  const s = pptx.addSlide(); header(s, '3. 三条正式核心样板链已形成稳定主干', 4);
  card(s, 0.85, 1.35, 3.75, 4.7, '光学检测 / 机器视觉', ['已完成主数据建模','已完成结构关系补齐','已完成企业挂接验证','已完成查询与解释链验证'], C.blue);
  card(s, 4.8, 1.35, 3.75, 4.7, '光通信 / 光模块', ['已完成主数据建模','已完成结构关系补齐','已完成企业挂接验证','已完成查询与解释链验证'], C.cyan);
  card(s, 8.75, 1.35, 3.75, 4.7, '激光加工 / 光学装备', ['已完成主数据建模','已完成结构关系补齐','已完成企业挂接验证','已完成查询与解释链验证'], C.orange);
  s.addText('统一图谱主干已经进入“可导入、可查询、可演示”的稳定状态。', { x:0.92, y:6.25, w:11.4, h:0.28, fontSize:19, bold:true, color:C.navy, fontFace:'Microsoft YaHei' });
}

// 5 structure
{
  const s = pptx.addSlide(); header(s, '4. 当前统一图谱已经从企业库升级为结构化统一图谱', 5);
  sectionTitle(s, '统一对象层');
  card(s, 0.9, 1.45, 2.0, 1.7, 'Enterprise', ['企业本体'], C.blue);
  card(s, 3.1, 1.45, 1.8, 1.7, 'SubTrack', ['子赛道'], C.cyan);
  card(s, 5.1, 1.45, 1.8, 1.7, 'ChainStage', ['产业链环节'], C.orange);
  card(s, 7.1, 1.45, 1.8, 1.7, 'KeyCapability', ['关键能力'], C.gold);
  card(s, 9.1, 1.45, 1.8, 1.7, 'TechDirection', ['技术方向'], C.blue);
  card(s, 11.1, 1.45, 1.5, 1.7, 'Scenario', ['应用场景'], C.cyan);
  s.addText('核心区别：现在查到的不只是“企业像什么”，而是“企业位于哪里、具备什么能力、能力由什么技术支撑”。', { x:0.9, y:4.25, w:11.6, h:0.45, fontSize:20, bold:true, color:C.navy, fontFace:'Microsoft YaHei', align:'center' });
  s.addShape(pptx.ShapeType.line, { x:1.2, y:5.3, w:10.6, h:0, line:{ color:'BFD2F8', pt:2 } });
  s.addText('企业  →  关键能力  →  技术方向  →  产业环节', { x:2.2, y:5.45, w:8.7, h:0.35, fontSize:24, bold:true, color:C.blue, fontFace:'Microsoft YaHei', align:'center' });
}

// 6 explanation chain
{
  const s = pptx.addSlide(); header(s, '5. 技术路线—能力—产业环节的解释链已经建立', 6);
  card(s, 0.85, 1.4, 2.7, 1.6, '链路1', ['Capability -> DERIVES_FROM -> TechDirection'], C.blue);
  card(s, 3.65, 1.4, 2.7, 1.6, '链路2', ['KeyCapability -> SUPPORTED_BY -> TechDirection'], C.cyan);
  card(s, 6.45, 1.4, 2.7, 1.6, '链路3', ['TechDirection -> ENABLES_STAGE -> ChainStage'], C.orange);
  card(s, 9.25, 1.4, 3.0, 1.6, '链路4', ['Enterprise -> HAS_KEY_CAPABILITY -> KeyCapability'], C.gold);
  s.addShape(pptx.ShapeType.chevron, { x:1.7, y:4.0, w:1.7, h:0.7, fill:{color:'EAF0FF'}, line:{color:'BFD2F8'} });
  s.addText('企业具备\n高精度加工控制能力', { x:1.78, y:4.15, w:1.52, h:0.35, fontSize:16, bold:true, align:'center', color:C.navy, fontFace:'Microsoft YaHei' });
  s.addShape(pptx.ShapeType.chevron, { x:3.75, y:4.0, w:1.7, h:0.7, fill:{color:'EAFBF7'}, line:{color:'BFEFE0'} });
  s.addText('能力由\n精密驱动与微振动控制技术支撑', { x:3.83, y:4.06, w:1.52, h:0.42, fontSize:13, bold:true, align:'center', color:C.navy, fontFace:'Microsoft YaHei' });
  s.addShape(pptx.ShapeType.chevron, { x:5.8, y:4.0, w:1.9, h:0.7, fill:{color:'FFF3E8'}, line:{color:'FFD0AF'} });
  s.addText('技术支撑\n振镜/加工头/执行单元等环节', { x:5.93, y:4.06, w:1.62, h:0.42, fontSize:13, bold:true, align:'center', color:C.navy, fontFace:'Microsoft YaHei' });
  s.addShape(pptx.ShapeType.chevron, { x:8.05, y:4.0, w:3.2, h:0.7, fill:{color:'FFF9E8'}, line:{color:'F5E3A0'} });
  s.addText('推荐结果不再只是“词像”，而是具备结构化解释理由', { x:8.2, y:4.18, w:2.85, h:0.28, fontSize:15, bold:true, align:'center', color:C.navy, fontFace:'Microsoft YaHei' });
}

// 7 queries
{
  const s = pptx.addSlide(); header(s, '6. 当前主图谱查询能力已能支撑后续推荐基础', 7);
  card(s, 0.85, 1.35, 3.0, 4.7, '已支持查询', ['按子赛道看企业','按环节找企业','看某企业在产业链中的位置','从关键能力反查企业与环节','从场景反查环节与企业'], C.blue);
  card(s, 4.15, 1.35, 3.0, 4.7, '意味着什么', ['图谱不只用于展示','已开始支撑需求推荐基础','已开始支撑协同推荐基础','已开始支撑寻源匹配基础'], C.cyan);
  card(s, 7.45, 1.35, 4.8, 4.7, '核心价值', ['过去：只能看企业标签','现在：能看企业位于哪个环节、具备哪些能力、技术方向支撑哪些环节','这为后续推荐能力提供了真正的统一底座'], C.orange);
}

// 8 commercial space worth adding
{
  const s = pptx.addSlide(); header(s, '7. 商业航天已具备进入 V2 评审的基础', 8);
  card(s, 0.85, 1.2, 3.8, 4.9, '已完成', ['研究版','标准口径','候选主数据五件套','候选关系表五件套','候选 patch 验证','候选企业 patch 验证','候选域查询模板'], C.blue);
  card(s, 4.9, 1.2, 3.6, 4.9, '已验证结果', ['SubTrack: 1','ChainStage: 10','KeyCapability: 8','ApplicationScenario: 8','TechDirection: 8','候选企业数: 4'], C.cyan);
  card(s, 8.8, 1.2, 3.4, 4.9, '结论', ['商业航天已经不是规划项','已完成独立候选域验证','可以进入 V2 范围评审','但当前成熟度仍低于正式核心域'], C.orange);
}

// 9 positioning
{
  const s = pptx.addSlide(); header(s, '8. 商业航天建议纳入 V2，但不与三条正式样板链同成熟度并表', 9);
  card(s, 0.95, 1.45, 3.2, 4.6, '判断1：结构口径', ['基本稳定','10 个标准环节','8 个关键能力','8 个技术方向'], C.blue);
  card(s, 4.45, 1.45, 3.2, 4.6, '判断2：企业验证', ['已有第一轮企业 patch','样本仍偏少','交叉企业边界仍需治理'], C.cyan);
  card(s, 7.95, 1.45, 4.1, 4.6, '建议定位', ['纳入统一图谱 V2','定位为：扩展候选域 / 候选正式域','不建议直接表述为“第四条成熟正式样板链”'], C.orange);
  s.addText('结论：建议纳入，但采用受控纳入，而不是完全等价并表。', { x:1.0, y:6.25, w:11.2, h:0.25, fontSize:19, bold:true, color:C.navy, fontFace:'Microsoft YaHei', align:'center' });
}

// 10 3+1
{
  const s = pptx.addSlide(); header(s, '9. 统一图谱 V2 建议范围：3+1+储备', 10);
  card(s, 0.9, 1.35, 3.7, 4.7, '3 条正式核心域', ['光学检测 / 机器视觉','光通信 / 光模块','激光加工 / 光学装备'], C.blue);
  card(s, 4.85, 1.35, 3.0, 4.7, '1 条扩展候选域', ['商业航天'], C.cyan);
  card(s, 8.15, 1.35, 4.1, 4.7, '储备方向', ['其他尚未完成研究版、候选主数据、patch 验证的新方向','暂不进入本轮正式建设范围'], C.orange);
  s.addText('V2 不是“再多加几个行业”，而是“正式主干稳定推进 + 候选扩展域受控试运行”。', { x:0.95, y:6.22, w:11.4, h:0.3, fontSize:18, bold:true, color:C.navy, fontFace:'Microsoft YaHei' });
}

// 11 next step
{
  const s = pptx.addSlide(); header(s, '10. 下一阶段重点：从图谱建模转向产品化与评审化验证', 11);
  card(s, 0.9, 1.45, 3.6, 4.5, '正式主干', ['围绕三条正式核心域继续做产品化查询与推荐模板'], C.blue);
  card(s, 4.85, 1.45, 3.6, 4.5, '商业航天', ['继续补企业样本、候选域治理、版本治理说明'], C.cyan);
  card(s, 8.8, 1.45, 3.4, 4.5, '交付资产', ['把演示、评审、版本治理资产整理为可复用交付件'], C.orange);
  s.addText('下一步最值得做的，不是继续证明能不能建，而是基于已做成的主干进入更稳定的产品化验证。', { x:0.95, y:6.15, w:11.4, h:0.34, fontSize:18, bold:true, color:C.navy, fontFace:'Microsoft YaHei', align:'center' });
}

// 12 final recommendation
{
  const s = pptx.addSlide(); header(s, '11. 最终建议', 12);
  s.addShape(pptx.ShapeType.roundRect, { x:0.95, y:1.55, w:11.35, h:2.25, rectRadius:0.08, fill:{color:'EEF4FF'}, line:{color:'CFE0FF', pt:1.2} });
  s.addText('建议统一图谱 V2 采用“3条正式核心域 + 1条商业航天扩展候选域 + 其他方向储备”的分层推进方式。', { x:1.35, y:2.1, w:10.55, h:1.1, fontSize:24, bold:true, color:C.navy, align:'center', valign:'mid', fontFace:'Microsoft YaHei' });
  card(s, 1.4, 4.45, 2.8, 1.35, '正式核心域', ['继续做深'], C.blue);
  card(s, 5.2, 4.45, 2.8, 1.35, '商业航天', ['进入 V2，但按候选正式域治理'], C.cyan);
  card(s, 9.0, 4.45, 2.8, 1.35, '其他方向', ['继续储备'], C.orange);
  s.addText('“先把主干做稳，再把扩展做可控。”', { x:3.5, y:6.35, w:6.3, h:0.28, fontSize:22, bold:true, align:'center', color:C.green, fontFace:'Microsoft YaHei' });
}

pptx.writeFile({ fileName: 'C:/Users/XCKF/.openclaw/workspace-kg-prototype/deliverables/统一图谱V2评审汇报.pptx' });
