# -*- coding: utf-8 -*-
"""
Gemini API 封裝模組
負責與 Google Gemini API 的所有互動
"""

import json
import re
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL, MAX_OUTPUT_TOKENS, TEMPERATURE
from generator.ai_prompts import SYSTEM_PROMPT


def _configure_client():
    """設定 Gemini API 客戶端"""
    genai.configure(api_key=GEMINI_API_KEY)


def _extract_json(text: str) -> dict:
    """
    從 AI 回應文字中提取 JSON 物件。
    處理可能包含 markdown code block 的情況。
    """
    # 嘗試移除 markdown code block 標記
    cleaned = text.strip()
    # 移除 ```json ... ``` 或 ``` ... ```
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(1).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # 嘗試找到第一個 { 和最後一個 } 之間的內容
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(cleaned[start : end + 1])
            except json.JSONDecodeError:
                pass
        raise ValueError(f"無法解析 AI 回應為 JSON：{text[:200]}...")


def call_gemini(prompt: str, retry_count: int = 1) -> dict:
    """
    呼叫 Gemini API 並返回 JSON 結構化結果。

    Args:
        prompt: 使用者 prompt
        retry_count: 重試次數（預設 1 次）

    Returns:
        解析後的 JSON dict

    Raises:
        ValueError: JSON 解析失敗
        Exception: API 呼叫失敗
    """
    _configure_client()

    # 嘗試使用 system_instruction（需 SDK >= 0.4.0），
    # 若不支援則退回至合併 prompt 的方式
    model_kwargs = {
        "model_name": GEMINI_MODEL,
        "generation_config": genai.GenerationConfig(
            max_output_tokens=MAX_OUTPUT_TOKENS,
            temperature=TEMPERATURE,
        ),
    }
    use_system_instruction = True
    try:
        model = genai.GenerativeModel(
            system_instruction=SYSTEM_PROMPT, **model_kwargs
        )
    except TypeError:
        # 舊版 SDK 不支援 system_instruction
        use_system_instruction = False
        model = genai.GenerativeModel(**model_kwargs)

    # 若無法使用 system_instruction，將 system prompt 合併到 user prompt 前面
    if use_system_instruction:
        full_prompt = prompt
    else:
        full_prompt = f"[系統指令]\n{SYSTEM_PROMPT}\n\n[使用者指令]\n{prompt}"

    last_error = None
    for attempt in range(retry_count + 1):
        try:
            response = model.generate_content(full_prompt)
            result = _extract_json(response.text)
            return result
        except Exception as e:
            last_error = e
            if attempt < retry_count:
                continue
            raise last_error


# ─── 預設骨架內容（API 失敗時使用） ────────────────────

DEFAULT_M1 = {
    "technology_trend": "（AI 分析暫時無法取得，請手動補充科技趨勢資料）",
    "economics_trend": "（AI 分析暫時無法取得，請手動補充經濟趨勢資料）",
    "politics_trend": "（AI 分析暫時無法取得，請手動補充法令政策趨勢資料）",
    "application_trend": "（AI 分析暫時無法取得，請手動補充應用趨勢資料）",
    "summary": "（AI 分析暫時無法取得，請手動補充綜合論述）",
}

DEFAULT_M2 = {
    "market_size": "（AI 分析暫時無法取得）",
    "supply_gap": ["供給端缺口待補充", "供給端缺口待補充", "供給端缺口待補充"],
    "demand_gap": ["需求端缺口待補充", "需求端缺口待補充", "需求端缺口待補充"],
    "pest_summary": "（AI 分析暫時無法取得）",
    "topic_rationale": "（AI 分析暫時無法取得）",
}

DEFAULT_C1 = {
    "social_need_score": "中",
    "social_need_reasons": ["社會需求待補充", "社會需求待補充", "社會需求待補充"],
    "social_value": "（AI 分析暫時無法取得）",
    "beneficiary_groups": ["受益群體待補充", "受益群體待補充", "受益群體待補充"],
}

DEFAULT_C2 = {
    "primary_operator_type": "（AI 分析暫時無法取得）",
    "partner_types": [
        {"type": "待補充", "role": "待補充"},
        {"type": "待補充", "role": "待補充"},
        {"type": "待補充", "role": "待補充"},
    ],
    "solution_providers": "（AI 分析暫時無法取得）",
    "target_scale": "（AI 分析暫時無法取得）",
    "competitive_landscape": "（AI 分析暫時無法取得）",
}

DEFAULT_WHO = {
    "market_feasibility": "（AI 分析暫時無法取得）",
    "business_model": "（AI 分析暫時無法取得）",
    "target_customer": "（AI 分析暫時無法取得）",
    "service_feasibility": "（AI 分析暫時無法取得）",
    "solution_feasibility": "（AI 分析暫時無法取得）",
    "spillover_benefit": "（AI 分析暫時無法取得）",
    "value_proposition": "（AI 分析暫時無法取得）",
    "strategic_directions": ["策略方向待補充", "策略方向待補充", "策略方向待補充"],
}
