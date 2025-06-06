# Dockerfile

# 1. ベースイメージとしてPython 3.11のスリム版を使用
FROM python:3.11-slim

# 2. コンテナ内の作業ディレクトリを設定
WORKDIR /app

# 3. 依存関係ファイルを先にコピーし、ライブラリをインストール
#    （requirements.txtに変更がなければキャッシュが利用され、ビルドが高速化する）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. アプリケーションのコードをコンテナにコピー
COPY . .

# 5. Streamlitが使用するポート8090を外部に公開するよう設定
EXPOSE 8090

# 6. コンテナ起動時に実行するコマンド
#    --server.address=0.0.0.0 を指定して、コンテナ外部からのアクセスを許可する
CMD ["streamlit", "run", "app.py", "--server.port", "8090", "--server.address=0.0.0.0"]
