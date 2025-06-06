# 📄 Gemini OCR アプリ

Google の Gemini Generative AI を活用して画像からテキストを抽出する **Streamlit** 製 OCR アプリです。ローカル環境でも Docker でも手軽に動かせます。

なお、本アプリのコードは gemini-2.5-pro-preview-06-05 の Vibe Coding で生成されています。

---

## 🚀 主な機能

| 機能        | 説明                                                                |
| --------- | ----------------------------------------------------------------- |
| 画像アップロード  | JPG / PNG 形式の画像をドラッグ＆ドロップでアップロードできます。                             |
| モデル選択     | **Gemini 2.5 Flash**（高速・低コスト）と **Gemini 2.5 Pro**（高精度）をワンクリックで切替。 |
| OCR 実行    | ボタンを押すだけで画像内テキストを抽出し、右側ペインに表示。                                    |
| Docker 対応 | `GOOGLE_API_KEY` を渡すだけでどこでも同じ環境を再現可能。                             |

---

## 📂 ディレクトリ構成

```text
├── .dockerignore
├── .env.example
├── .gitignore
├── .streamlit/
│   └── .gitignore
├── Dockerfile
├── LICENSE
├── app.py
└── requirements.txt
```

---

## 🛠️ 前提条件

* **Python 3.11** 以上（ローカル実行の場合）
* **Google API Key**（Gemini API）
* Docker（オプション）

---

## ⬇️ 使い方

### 1. ローカル環境で実行

```bash
# 1. リポジトリをクローン
$ git clone https://github.com/e-triad/gemini-ocr-app.git
$ cd gemini-ocr-app

# 2. 仮想環境を作成
$ python -m venv venv
$ source venv/bin/activate  # Windows は venv\Scripts\activate

# 3. 依存関係をインストール
$ pip install --upgrade pip
$ pip install -r requirements.txt

# 4. API キーを設定（どちらか）
#   4‑A. 環境変数
$ export GOOGLE_API_KEY="YOUR_KEY"
#   4‑B. Streamlit Secrets
$ echo "GOOGLE_API_KEY='YOUR_KEY'" > .streamlit/secrets.toml

# 5. アプリを起動
$ streamlit run app.py --server.port 8090
```

ブラウザが自動で開かない場合は [http://localhost:8090](http://localhost:8090) を開いてください。

### 2. Docker で実行

```bash
# ビルド
$ docker build -t gemini-ocr-app .

# 実行（ポート 8090 をホストに公開）
$ docker run --rm -p 8090:8090 --env-file .env gemini-ocr-app
```

ブラウザで [http://localhost:8090](http://localhost:8090) を開くとアプリにアクセスできます。

---

## 🔑 環境変数

| 変数名              | 必須 | 用途                     |
| ---------------- | -- | ---------------------- |
| `GOOGLE_API_KEY` | ✔︎ | Gemini API への認証に使用します。 |

`.env.example` をコピーして `.env` を作成すると便利です（Docker を使わない場合は `.env` をロードする方法を各自実装してください）。

---

## 📜 ライセンス

このプロジェクトは **MIT License** のもとで公開されています。詳しくは [`LICENSE`](LICENSE) をご覧ください。

---

## 🙌 貢献

バグ報告・機能提案・プルリクエスト大歓迎です！お気軽に Issue を立ててください。

---

## ✨ クレジット

* [Streamlit](https://streamlit.io/)
* [Google Generative AI Python SDK](https://github.com/google-gemini/generative-ai-python)
* [Pillow](https://pillow.readthedocs.io/en/stable/)
