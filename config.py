# -*- coding: utf-8 -*-
"""
設定常數檔案
包含系統設定、顏色、字型、路徑等常數定義
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── Gemini API 設定 ─────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", "2048"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

# ─── 暫存檔案設定 ─────────────────────────────────────
TMP_DIR = os.getenv("TMP_DIR", "./tmp")
TMP_TTL_SECONDS = int(os.getenv("TMP_TTL_SECONDS", "3600"))

# ─── PPTX 設計規範 ────────────────────────────────────
PPTX_COLORS = {
    "primary": "1B3A6B",      # 深藍（主色調）
    "secondary": "E8F0FB",    # 淺藍（輔色）
    "accent": "FF6B35",       # 橘紅（強調）
    "white": "FFFFFF",
    "dark_text": "2D2D2D",
    "light_text": "FFFFFF",
    "gray": "888888",
}

PPTX_FONTS = {
    "title": "Microsoft JhengHei",       # 微軟正黑體
    "title_bold": "Microsoft JhengHei",   # 微軟正黑體 Bold
    "body": "Microsoft JhengHei",         # 微軟正黑體
}

PPTX_FONT_SIZES = {
    "cover_title": 32,
    "slide_title": 28,
    "subtitle": 20,
    "body": 16,
    "small": 12,
    "footer": 10,
}

# ─── 行業類別選項 ──────────────────────────────────────
INDUSTRY_OPTIONS = [
    "餐飲服務業",
    "零售業",
    "觀光旅遊業",
    "住宿業",
    "美容美髮業",
    "醫療健康業",
    "教育培訓業",
    "製造業",
    "物流運輸業",
    "農業食品業",
    "文化創意業",
    "不動產業",
    "金融服務業",
    "其他",
]

# ─── 生成步驟定義 ──────────────────────────────────────
GENERATION_STEPS = [
    {"step": 1, "name": "分析全球趨勢", "description": "生成 M1 內容（Macro + Trend）"},
    {"step": 2, "name": "分析台灣在地市場", "description": "生成 M2 內容（Market + Topic）"},
    {"step": 3, "name": "評估社會需求與價值", "description": "生成 C1 內容（Customer + Trade）"},
    {"step": 4, "name": "盤點潛在業者生態", "description": "生成 C2 內容（Competitor + Target）"},
    {"step": 5, "name": "評估業者可行性", "description": "生成 Who 內容（五項評估）"},
    {"step": 6, "name": "組裝輸出", "description": "生成 Markdown + PPTX"},
]

# ─── 資策會輔導價值（固定內容） ─────────────────────────
WE_CONTRIBUTION = {
    "headline": "全程陪伴輔導，促成落地實證並發揮AI賦能效益",
    "stages": [
        {
            "stage": "應用需求評估",
            "description": "盤點業者的技術體質與營運痛點，評估AI導入可行性",
            "outputs": ["AI準備度評估報告", "應用需求清單"],
        },
        {
            "stage": "應用服務設計",
            "description": "協助業者進行AI服務情境深度設計，媒合解決方案提供者",
            "outputs": ["服務情境設計文件", "解決方案媒合清單"],
        },
        {
            "stage": "專家指導優化",
            "description": "邀集產學研專家召開指導會議，優化提案構想",
            "outputs": ["指導會議紀錄", "優化建議報告"],
        },
        {
            "stage": "共創驗證規劃",
            "description": "協助業者擬定落地驗證規劃，導入AI解決方案",
            "outputs": ["落地驗證計畫書", "合作模式設計"],
        },
        {
            "stage": "落地實證擴散",
            "description": "實地跟案輔導，確保如期如質執行，並推廣成功經驗",
            "outputs": ["成果案例集", "擴散推廣活動"],
        },
    ],
}

# ─── 組織名稱 ──────────────────────────────────────────
ORG_NAME = "資策會數位轉型研究院"
PROJECT_NAME = "中小微AI創新應用輔導計畫"
