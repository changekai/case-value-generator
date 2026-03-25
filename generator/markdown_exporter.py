# -*- coding: utf-8 -*-
"""
Markdown 匯出模組
將分析結果組裝為 Markdown 格式字串
"""

from datetime import datetime
from config import ORG_NAME


def export_markdown(analysis: dict) -> str:
    """
    將分析結果匯出為 Markdown 字串。

    Args:
        analysis: build_analysis() 的回傳結果

    Returns:
        完整的 Markdown 字串
    """
    meta = analysis["meta"]
    m1 = analysis["m1_macro"]
    m2 = analysis["m2_market"]
    c1 = analysis["c1_customer"]
    c2 = analysis["c2_competitor"]
    who = analysis["who_evaluation"]
    we = analysis["we_contribution"]

    company = meta["company_name"]
    industry = meta["industry"]
    topic = meta["transformation_topic"]
    date_str = datetime.now().strftime("%Y-%m-%d")

    # 組裝供給端缺口
    supply_gaps = "\n".join(
        [f"- {g}" for g in m2.get("supply_gap", ["（待補充）"])]
    )
    # 組裝需求端缺口
    demand_gaps = "\n".join(
        [f"- {g}" for g in m2.get("demand_gap", ["（待補充）"])]
    )
    # 組裝社會需求理由
    social_reasons = "\n".join(
        [f"- {r}" for r in c1.get("social_need_reasons", ["（待補充）"])]
    )
    # 組裝受益群體
    beneficiaries = "\n".join(
        [f"- {b}" for b in c1.get("beneficiary_groups", ["（待補充）"])]
    )
    # 組裝合作夥伴
    partners = "\n".join(
        [
            f"- **{p.get('type', '待補充')}**：{p.get('role', '待補充')}"
            for p in c2.get("partner_types", [])
        ]
    )
    # 組裝策略方向
    strategies = "\n".join(
        [f"- {s}" for s in who.get("strategic_directions", ["（待補充）"])]
    )
    # 組裝資策會輔導階段
    we_stages = ""
    for stage in we.get("stages", []):
        outputs = "、".join(stage.get("outputs", []))
        we_stages += f"""
### {stage['stage']}
{stage['description']}

**產出物**：{outputs}
"""

    # 組裝警告訊息
    warnings_section = ""
    if meta.get("warnings"):
        warnings_list = "\n".join([f"- ⚠️ {w}" for w in meta["warnings"]])
        warnings_section = f"""
---

## ⚠️ 生成警告

{warnings_list}
"""

    md = f"""# 潛在案源價值說明
## {company} — {industry}｜{topic}
> 生成日期：{date_str}｜{ORG_NAME}

---

## WHAT：為什麼選這個題目？

### M1 全球趨勢洞察（Macro Environment）

#### 科技趨勢
{m1.get('technology_trend', '（待補充）')}

#### 經濟趨勢
{m1.get('economics_trend', '（待補充）')}

#### 法令政策趨勢
{m1.get('politics_trend', '（待補充）')}

#### 應用趨勢
{m1.get('application_trend', '（待補充）')}

**趨勢綜合論述**

{m1.get('summary', '（待補充）')}

---

### M2 台灣在地市場分析（Market Environment）

**市場規模**：{m2.get('market_size', '（待補充）')}

**供給端缺口**
{supply_gaps}

**需求端缺口**
{demand_gaps}

**PEST 分析摘要**：{m2.get('pest_summary', '（待補充）')}

**選題方向**：{m2.get('topic_rationale', '（待補充）')}

---

### C1 社會需求與社會價值（Customer）

**社會需求程度**：{c1.get('social_need_score', '中')}

**需求理由**
{social_reasons}

**社會價值**：{c1.get('social_value', '（待補充）')}

**受益群體**
{beneficiaries}

---

### C2 潛在業者與競爭生態（Competitor）

**主營運商**：{c2.get('primary_operator_type', '（待補充）')}

**合作夥伴生態系**
{partners}

**解決方案業者**：{c2.get('solution_providers', '（待補充）')}

**潛在輔導規模**：{c2.get('target_scale', '（待補充）')}

**競爭現況**：{c2.get('competitive_landscape', '（待補充）')}

---

## WHO：為什麼是這家業者？

### 五項可行性評估

| 面向 | 評估結論 |
|------|---------|
| 市場可行性 | {who.get('market_feasibility', '（待補充）')} |
| 商業模式 | {who.get('business_model', '（待補充）')} |
| 目標客戶 | {who.get('target_customer', '（待補充）')} |
| 服務可行性 | {who.get('service_feasibility', '（待補充）')} |
| 解決方案可行性 | {who.get('solution_feasibility', '（待補充）')} |

**外溢效益**：{who.get('spillover_benefit', '（待補充）')}

**題目整體價值主張**

{who.get('value_proposition', '（待補充）')}

**策略方向**
{strategies}

---

## WE：資策會能提供什麼？

{we.get('headline', '')}
{we_stages}
{warnings_section}

---

*本文件由案源價值論述生成系統自動產生｜{ORG_NAME}*
"""
    return md.strip()
