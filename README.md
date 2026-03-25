# 案源價值論述生成系統

> AI 驅動的案源價值論述自動生成工具 — 協助資策會顧問快速產出潛在案源價值說明文件。

## 功能特色

- **2M2C + 4T 分析框架**：自動分析全球趨勢(M1)、台灣市場(M2)、社會需求(C1)、競爭生態(C2)
- **三層敘事結構**：What（為什麼選題）→ Who（為什麼選他）→ We（資策會能做什麼）
- **雙格式輸出**：Markdown 全文 + PPTX 9 頁簡報
- **即時進度回饋**：六步驟進度條，每步驟 AI 呼叫狀態即時可見
- **Gemini AI 驅動**：使用 Google Gemini API 生成高品質分析內容

## 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 設定環境變數

```bash
cp .env.example .env
# 編輯 .env，填入 Gemini API Key
```

```
GEMINI_API_KEY=你的_API_KEY
GEMINI_MODEL=gemini-2.0-flash
```

### 3. 啟動伺服器

```bash
python app.py
```

瀏覽器開啟 http://localhost:5000

## 專案結構

```
project/
├── app.py                  # Flask 主程式（API + 前端路由）
├── config.py               # 設定常數
├── requirements.txt
├── .env.example
├── generator/
│   ├── __init__.py
│   ├── ai_prompts.py       # Prompt 模板
│   ├── ai_client.py        # Gemini API 封裝
│   ├── content_builder.py  # 內容組裝
│   ├── markdown_exporter.py # Markdown 匯出
│   └── pptx_exporter.py    # PPTX 簡報匯出
├── templates/
│   └── index.html          # 前端頁面
├── static/
│   ├── app.js              # 前端互動邏輯
│   └── style.css           # 自訂樣式
└── tmp/                    # 暫存檔案目錄（自動建立）
```

## API 端點

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/generate` | POST | 啟動生成任務 |
| `/api/status/<task_id>` | GET | 查詢進度 |
| `/api/result/<task_id>/markdown` | GET | 取得 Markdown 內容 |
| `/api/result/<task_id>/download/markdown` | GET | 下載 Markdown 檔案 |
| `/api/result/<task_id>/download/pptx` | GET | 下載 PPTX 簡報 |

## 技術棧

- **後端**：Python 3.9+ / Flask
- **AI**：Google Gemini API (`google-genai`)
- **前端**：HTML + Tailwind CSS + Vanilla JS
- **簡報生成**：python-pptx
- **Markdown 渲染**：marked.js

## 注意事項

- 需要有效的 Gemini API Key 才能正常生成
- 暫存檔案預設 1 小時後自動清理
- PPTX 使用微軟正黑體，請確認系統已安裝
