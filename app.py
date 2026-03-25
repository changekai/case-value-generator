# -*- coding: utf-8 -*-
"""
案源價值論述生成系統 — Flask 主程式
提供前端頁面與 API 端點
"""

import os
import uuid
import threading
import time
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_file
from config import TMP_DIR, TMP_TTL_SECONDS, INDUSTRY_OPTIONS, GENERATION_STEPS

app = Flask(__name__)

# ─── 任務儲存（記憶體層級） ────────────────────────────
tasks = {}

# ─── 確保 tmp 目錄存在 ────────────────────────────────
os.makedirs(TMP_DIR, exist_ok=True)


# ─── 暫存檔案自動清理 ────────────────────────────────
def cleanup_old_files():
    """每 10 分鐘清理超過 TTL 的暫存檔案"""
    while True:
        time.sleep(600)  # 每 10 分鐘執行一次
        now = time.time()
        try:
            for filename in os.listdir(TMP_DIR):
                filepath = os.path.join(TMP_DIR, filename)
                if os.path.isfile(filepath):
                    file_age = now - os.path.getmtime(filepath)
                    if file_age > TMP_TTL_SECONDS:
                        os.remove(filepath)
        except Exception:
            pass

        # 清理過期任務
        expired = [
            tid for tid, t in tasks.items()
            if now - t.get("created_at", now) > TMP_TTL_SECONDS
        ]
        for tid in expired:
            tasks.pop(tid, None)


cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True)
cleanup_thread.start()


# ─── 前端路由 ──────────────────────────────────────────

@app.route("/")
def index():
    """渲染主頁面"""
    return render_template("index.html", industries=INDUSTRY_OPTIONS)


# ─── API 端點 ──────────────────────────────────────────

@app.route("/api/generate", methods=["POST"])
def api_generate():
    """
    啟動非同步生成任務
    Body: { company_name, industry, transformation_topic, supplement }
    Response: { task_id: str }
    """
    data = request.get_json()

    # 驗證必填欄位
    company_name = data.get("company_name", "").strip()
    industry = data.get("industry", "").strip()
    transformation_topic = data.get("transformation_topic", "").strip()
    supplement = data.get("supplement", "").strip()

    if not company_name:
        return jsonify({"error": "請輸入業者名稱"}), 400
    if not industry:
        return jsonify({"error": "請選擇行業類別"}), 400
    if not transformation_topic:
        return jsonify({"error": "請輸入轉型主題"}), 400

    # 建立任務
    task_id = str(uuid.uuid4())[:8]
    tasks[task_id] = {
        "status": "processing",
        "step": 0,
        "step_name": "準備中",
        "progress": 0,
        "result": None,
        "error": None,
        "created_at": time.time(),
        "input": {
            "company_name": company_name,
            "industry": industry,
            "transformation_topic": transformation_topic,
            "supplement": supplement,
        },
    }

    # 在背景線程執行生成
    thread = threading.Thread(
        target=_run_generation,
        args=(task_id,),
        daemon=True,
    )
    thread.start()

    return jsonify({"task_id": task_id})


def _run_generation(task_id: str):
    """背景生成任務"""
    task = tasks.get(task_id)
    if not task:
        return

    try:
        # 延遲匯入避免循環依賴
        from generator.content_builder import build_analysis
        from generator.markdown_exporter import export_markdown
        from generator.pptx_exporter import export_pptx

        inp = task["input"]
        total_steps = len(GENERATION_STEPS)

        def progress_callback(step, step_name):
            task["step"] = step
            task["step_name"] = step_name
            task["progress"] = int((step / total_steps) * 100)

        # 執行分析
        analysis = build_analysis(
            company_name=inp["company_name"],
            industry=inp["industry"],
            transformation_topic=inp["transformation_topic"],
            supplement=inp["supplement"],
            progress_callback=progress_callback,
        )

        # 生成 Markdown
        md_content = export_markdown(analysis)

        # 生成 PPTX
        pptx_path = os.path.join(TMP_DIR, f"{task_id}.pptx")
        try:
            export_pptx(analysis, pptx_path)
            pptx_ok = True
        except Exception as e:
            pptx_ok = False
            task["pptx_error"] = str(e)

        # 儲存 Markdown 到檔案
        md_path = os.path.join(TMP_DIR, f"{task_id}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        task["status"] = "done"
        task["step"] = total_steps
        task["step_name"] = "完成"
        task["progress"] = 100
        task["result"] = {
            "markdown": md_content,
            "md_path": md_path,
            "pptx_path": pptx_path if pptx_ok else None,
            "pptx_ok": pptx_ok,
            "warnings": analysis["meta"].get("warnings", []),
        }

    except Exception as e:
        task["status"] = "error"
        task["error"] = str(e)


@app.route("/api/status/<task_id>")
def api_status(task_id):
    """
    查詢任務進度
    Response: { status, step, step_name, progress }
    """
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "任務不存在"}), 404

    response = {
        "status": task["status"],
        "step": task["step"],
        "step_name": task["step_name"],
        "progress": task["progress"],
    }

    if task["status"] == "error":
        response["error"] = task.get("error", "未知錯誤")

    if task["status"] == "done":
        result = task.get("result", {})
        response["pptx_ok"] = result.get("pptx_ok", False)
        response["warnings"] = result.get("warnings", [])

    return jsonify(response)


@app.route("/api/result/<task_id>/markdown")
def api_result_markdown(task_id):
    """
    取得 Markdown 內容
    Response: { content: str }
    """
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "任務不存在"}), 404
    if task["status"] != "done":
        return jsonify({"error": "任務尚未完成"}), 400

    content = task["result"]["markdown"]
    return jsonify({"content": content})


@app.route("/api/result/<task_id>/download/markdown")
def api_download_markdown(task_id):
    """下載 Markdown 檔案"""
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "任務不存在"}), 404
    if task["status"] != "done":
        return jsonify({"error": "任務尚未完成"}), 400

    md_path = task["result"]["md_path"]
    if not os.path.exists(md_path):
        return jsonify({"error": "檔案已過期，請重新生成"}), 410

    company = task["input"]["company_name"]
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{date_str}_{company}_案源價值說明.md"

    return send_file(
        md_path,
        as_attachment=True,
        download_name=filename,
        mimetype="text/markdown; charset=utf-8",
    )


@app.route("/api/result/<task_id>/download/pptx")
def api_download_pptx(task_id):
    """下載 PPTX 檔案"""
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "任務不存在"}), 404
    if task["status"] != "done":
        return jsonify({"error": "任務尚未完成"}), 400

    result = task["result"]
    if not result.get("pptx_ok"):
        return jsonify({"error": "PPTX 生成失敗，請重試"}), 500

    pptx_path = result["pptx_path"]
    if not os.path.exists(pptx_path):
        return jsonify({"error": "檔案已過期，請重新生成"}), 410

    company = task["input"]["company_name"]
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{date_str}_{company}_案源價值說明.pptx"

    return send_file(
        pptx_path,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )


# ─── 啟動伺服器 ────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
