# SEM Particle Analyzer Dockerfile
FROM python:3.9-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムパッケージの更新とOpenCVに必要なライブラリをインストール
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libatlas-base-dev \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

# Pythonの依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルをコピー
COPY . .

# ポート8501を公開（Streamlitのデフォルトポート）
EXPOSE 8501

# ヘルスチェック
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Streamlitアプリケーションを起動
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true", "--server.fileWatcherType=none", "--browser.gatherUsageStats=false"]