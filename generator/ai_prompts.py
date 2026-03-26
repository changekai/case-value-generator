# -*- coding: utf-8 -*-
"""
AI Prompt 定義模組
包含所有與 Gemini API 互動的 Prompt 定義
"""

# ─── 系統 Prompt（所有步驟共用） ────────────────────────
SYSTEM_PROMPT = """你是資策會數位轉型研究院的資深產業分析顧問。
你的任務是協助顧問為中小微企業AI創新應用輔導計畫產生支持論述。
請以繁體中文回應。
請只回傳要求的 JSON 格式，不要加入任何前言或解釋文字。
所有論述應具體、有說服力，可引用全球或台灣在地的產業趨勢數據或案例。"""


def build_expert_context(expert_input: dict) -> str:
    """
    將顧問觀點輸入組裝為 prompt 注入前綴。
    expert_input keys: core_argument, iii_angle, concern
    回傳空字串若無有效輸入。
    """
    parts = []
    core = (expert_input.get("core_argument") or "").strip()
    angle = (expert_input.get("iii_angle") or "").strip()
    concern = (expert_input.get("concern") or "").strip()

    if core:
        parts.append(f"【顧問核心論點】{core}")
    if angle:
        parts.append(f"【資策會切入角度】{angle}")
    if concern:
        parts.append(f"【預期挑戰問題】{concern}（請在論述中預先回應此顧慮）")

    if not parts:
        return ""

    return (
        "⚠️ 本文件由一位資深產業輔導顧問主導，以下是他／她的核心觀點，"
        "請圍繞這些論點展開分析，保持顧問的判斷語氣，"
        "讓輸出讀起來像一位有豐富實戰經驗的顧問在說話，而非通用 AI 分析：\n"
        + "\n".join(parts)
        + "\n\n"
    )


def get_m1_prompt(industry: str, transformation_topic: str, expert_context: str = "") -> str:
    """Step 1 — M1 全球趨勢洞察 Prompt"""
    return f"""{expert_context}針對「{industry}」行業中「{transformation_topic}」的AI轉型主題，
請從全球宏觀視角分析以下四個趨勢面向，
並以此支持「為什麼現在是導入AI的好時機」的論述。

請回傳以下 JSON 格式：
{{
  "technology_trend": "科技趨勢說明（2-3句，含具體數據或標竿案例）",
  "economics_trend": "經濟趨勢說明（2-3句）",
  "politics_trend": "法令政策趨勢說明（2-3句）",
  "application_trend": "應用趨勢說明（2-3句，含全球領先業者案例）",
  "summary": "一段綜合論述（4-5句），說明全球趨勢如何指向此轉型方向的必然性"
}}"""


def get_m2_prompt(industry: str, transformation_topic: str, expert_context: str = "") -> str:
    """Step 2 — M2 台灣在地市場分析 Prompt"""
    return f"""{expert_context}針對台灣「{industry}」行業的在地市場現況，
請分析導入「{transformation_topic}」的市場條件與痛點缺口。

請回傳以下 JSON 格式：
{{
  "market_size": "台灣市場規模描述（含數據或估算）",
  "supply_gap": ["供給端缺口1", "供給端缺口2", "供給端缺口3"],
  "demand_gap": ["需求端缺口1", "需求端缺口2", "需求端缺口3"],
  "pest_summary": "PEST分析摘要（政治/經濟/社會/科技各一句）",
  "topic_rationale": "選題方向說明（3-4句），說明為何此市場缺口指向這個AI應用題目"
}}"""


def get_c1_prompt(industry: str, transformation_topic: str, expert_context: str = "") -> str:
    """Step 3 — C1 社會需求與社會價值 Prompt"""
    return f"""{expert_context}針對「{industry}」行業的「{transformation_topic}」AI應用，
請論述其社會需求程度與社會價值。

請回傳以下 JSON 格式：
{{
  "social_need_score": "高/中/低",
  "social_need_reasons": ["社會需求理由1", "社會需求理由2", "社會需求理由3"],
  "social_value": "社會價值論述（3-4句，說明此應用對消費者、從業者、環境的正面影響）",
  "beneficiary_groups": ["受益群體1", "受益群體2", "受益群體3"]
}}"""


def get_c2_prompt(
    industry: str, transformation_topic: str, company_name: str, expert_context: str = ""
) -> str:
    """Step 4 — C2 潛在業者與競爭生態 Prompt"""
    return f"""{expert_context}針對台灣「{industry}」行業，
請描述「{transformation_topic}」相關的潛在目標業者生態系。
輔導業者為「{company_name}」。

請回傳以下 JSON 格式：
{{
  "primary_operator_type": "主營運商類型說明",
  "partner_types": [
    {{"type": "合作夥伴類型1", "role": "在生態系中的角色"}},
    {{"type": "合作夥伴類型2", "role": "在生態系中的角色"}},
    {{"type": "合作夥伴類型3", "role": "在生態系中的角色"}}
  ],
  "solution_providers": "解決方案業者類型說明",
  "target_scale": "潛在輔導規模（例：估計台灣有X家類似業者）",
  "competitive_landscape": "現有競爭或類似服務現況（2-3句）"
}}"""


def get_who_prompt(
    company_name: str,
    industry: str,
    transformation_topic: str,
    supplement: str = "",
    expert_context: str = "",
) -> str:
    """Step 5 — Who 業者可行性評估 Prompt"""
    supplement_line = f"\n補充資訊：{supplement}" if supplement else ""
    return f"""{expert_context}業者「{company_name}」是一家台灣的「{industry}」業者，
正在考慮導入「{transformation_topic}」AI應用。{supplement_line}

請從五個面向評估其可行性，並說明題目價值。

請回傳以下 JSON 格式：
{{
  "market_feasibility": "市場可行性評估（3-4句，含供需缺口說明）",
  "business_model": "商業模式評估（3-4句，說明營收邏輯與價值主張）",
  "target_customer": "目標客戶評估（說明目標客群特徵與規模）",
  "service_feasibility": "服務可行性評估（說明服務設計的可實現性）",
  "solution_feasibility": "解決方案可行性評估（AI技術成熟度、取得難易度）",
  "spillover_benefit": "外溢效益說明（此案成功後對整個行業的帶動效果）",
  "value_proposition": "題目整體價值主張（3-5句，統整論述為何值得投入資源）",
  "strategic_directions": ["策略方向1", "策略方向2", "策略方向3"]
}}"""
