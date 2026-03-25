# -*- coding: utf-8 -*-
"""
內容建構模組
將 AI 輸出組裝為結構化資料
"""

from generator.ai_client import (
    call_gemini,
    DEFAULT_M1,
    DEFAULT_M2,
    DEFAULT_C1,
    DEFAULT_C2,
    DEFAULT_WHO,
)
from generator.ai_prompts import (
    get_m1_prompt,
    get_m2_prompt,
    get_c1_prompt,
    get_c2_prompt,
    get_who_prompt,
)
from config import WE_CONTRIBUTION


def build_analysis(
    company_name: str,
    industry: str,
    transformation_topic: str,
    supplement: str = "",
    progress_callback=None,
) -> dict:
    """
    執行完整的分析流程（Step 1～6），依序呼叫 AI 並組裝結果。

    Args:
        company_name: 業者名稱
        industry: 行業類別
        transformation_topic: 轉型主題
        supplement: 補充說明
        progress_callback: 進度回呼函式 callback(step, step_name)

    Returns:
        完整的分析結果 dict
    """
    result = {}
    warnings = []

    def _update_progress(step: int, name: str):
        if progress_callback:
            progress_callback(step, name)

    # ─── Step 1: M1 全球趨勢洞察 ──────────────────────
    _update_progress(1, "分析全球趨勢")
    try:
        prompt = get_m1_prompt(industry, transformation_topic)
        result["m1_macro"] = call_gemini(prompt)
    except Exception as e:
        warnings.append(f"Step 1 全球趨勢分析失敗：{str(e)}")
        result["m1_macro"] = DEFAULT_M1.copy()

    # ─── Step 2: M2 台灣在地市場分析 ──────────────────
    _update_progress(2, "分析台灣在地市場")
    try:
        prompt = get_m2_prompt(industry, transformation_topic)
        result["m2_market"] = call_gemini(prompt)
    except Exception as e:
        warnings.append(f"Step 2 台灣市場分析失敗：{str(e)}")
        result["m2_market"] = DEFAULT_M2.copy()

    # ─── Step 3: C1 社會需求與社會價值 ────────────────
    _update_progress(3, "評估社會需求與價值")
    try:
        prompt = get_c1_prompt(industry, transformation_topic)
        result["c1_customer"] = call_gemini(prompt)
    except Exception as e:
        warnings.append(f"Step 3 社會需求分析失敗：{str(e)}")
        result["c1_customer"] = DEFAULT_C1.copy()

    # ─── Step 4: C2 潛在業者與競爭生態 ────────────────
    _update_progress(4, "盤點潛在業者生態")
    try:
        prompt = get_c2_prompt(industry, transformation_topic, company_name)
        result["c2_competitor"] = call_gemini(prompt)
    except Exception as e:
        warnings.append(f"Step 4 業者生態分析失敗：{str(e)}")
        result["c2_competitor"] = DEFAULT_C2.copy()

    # ─── Step 5: Who 業者可行性評估 ───────────────────
    _update_progress(5, "評估業者可行性")
    try:
        prompt = get_who_prompt(company_name, industry, transformation_topic, supplement)
        result["who_evaluation"] = call_gemini(prompt)
    except Exception as e:
        warnings.append(f"Step 5 業者可行性評估失敗：{str(e)}")
        result["who_evaluation"] = DEFAULT_WHO.copy()

    # ─── Step 6: We 資策會貢獻（固定內容） ────────────
    _update_progress(6, "組裝輸出")
    result["we_contribution"] = WE_CONTRIBUTION

    # 加入元資料
    result["meta"] = {
        "company_name": company_name,
        "industry": industry,
        "transformation_topic": transformation_topic,
        "supplement": supplement,
        "warnings": warnings,
    }

    return result
