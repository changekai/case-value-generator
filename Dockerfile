# 建立在 Python 3.9 基礎映像檔之上（根據專案需求支援 Python 3.9+）
FROM python:3.9-slim

# 設定工作目錄
WORKDIR /app

# 設定環境變數
# 避免 Python 寫入 .pyc 檔案
ENV PYTHONDONTWRITEBYTECODE=1 
# 確保 Python 輸出直接印到終端機，不進行緩衝
ENV PYTHONUNBUFFERED=1
# 指定預設暫存目錄
ENV TMP_DIR=/app/tmp

# 複製 requirements.txt 並安裝依賴
# 先複製此檔案可利用 Docker 緩衝層機制，若依賴沒變就不用重新安裝
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 複製專案原始碼到容器內
COPY . .

# 建立暫存目錄並給予讀寫權限，避免產生權限錯誤
RUN mkdir -p /app/tmp && chmod 777 /app/tmp

# 暴露 Flask 預設運行的 5000 Port
EXPOSE 5000

# 啟動 Flask 伺服器
#CMD ["python", "app.py"]
CMD ["gunicorn", "--workers", "1", "--threads", "4", "--bind", "0.0.0.0:5000", "app:app"]
