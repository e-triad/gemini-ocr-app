import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import os # osモジュールをインポート

# --- ページ設定 ---
st.set_page_config(
    page_title="Gemini OCRアプリ",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Gemini OCR アプリ")
st.caption("アップロードした画像からテキストを抽出します。")

# --- Gemini APIキーの設定 (Docker/ローカル両対応) ---
# 1. 環境変数からAPIキーを取得 (Docker環境向け)
google_api_key = os.environ.get("GOOGLE_API_KEY")

# 2. 環境変数がない場合、StreamlitのSecretsから取得 (ローカル開発向け)
if not google_api_key:
    try:
        google_api_key = st.secrets["GOOGLE_API_KEY"]
    except (KeyError, FileNotFoundError):
        st.error("⚠️ Gemini APIキーが設定されていません。")
        st.info("Docker環境では -e GOOGLE_API_KEY='YOUR_API_KEY' を、ローカル環境では .streamlit/secrets.toml を設定してください。")
        st.stop()

# 3. APIキーが取得できた場合のみ、genaiを構成
if google_api_key:
    genai.configure(api_key=google_api_key)
else:
    st.error("APIキーの取得に失敗しました。アプリケーションを停止します。")
    st.stop()


# --- サイドバー ---
with st.sidebar:
    st.header("⚙️ 設定")
    model_choice = st.radio(
        "使用するモデルを選択してください:",
        ("Gemini 2.5 Flash", "Gemini 2.5 Pro"),
        captions=["⚡ 高速・低コストなモデル", "✨ 高精度なモデル"]
    )
    if model_choice == "Gemini 2.5 Flash":
        model_name = "gemini-2.5-flash-preview-05-20"
    else:
        model_name = "gemini-2.5-pro-preview-06-05"

    st.divider()
    st.markdown(
        """
        ### 使い方
        1. 左側のエリアに画像ファイルをアップロードします。(JPG, PNG)
        2. **「OCRを実行する」**ボタンをクリックします。
        3. 右側のエリアに抽出されたテキストが表示されます。
        """
    )
    st.divider()
    st.info("このアプリはGoogleのGemini APIを使用しています。")


# --- メイン画面のレイアウト ---
left_column, right_column = st.columns(2)

# --- 左カラム：画像アップロード ---
with left_column:
    st.header("🖼️ 画像のアップロード")
    uploaded_file = st.file_uploader(
        "OCRしたい画像をここにアップロードしてください",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="アップロードされた画像", use_column_width=True)

            if st.button("🔍 OCRを実行する", use_container_width=True, type="primary"):
                st.session_state.run_ocr = True
                img_byte_arr = io.BytesIO()
                image_format = image.format if image.format in ['JPEG', 'PNG'] else 'PNG'
                image.save(img_byte_arr, format=image_format)
                st.session_state.image_bytes = img_byte_arr.getvalue()
                st.session_state.model_name_on_run = model_name
        except Exception as e:
            st.error(f"画像の読み込み中にエラーが発生しました: {e}")

# --- 右カラム：OCR結果表示 ---
with right_column:
    st.header("📝 OCR結果")
    if 'run_ocr' in st.session_state and st.session_state.run_ocr:
        with st.spinner(f"`{st.session_state.model_name_on_run}` で処理を実行中..."):
            try:
                image_to_process = Image.open(io.BytesIO(st.session_state.image_bytes))
                model = genai.GenerativeModel(st.session_state.model_name_on_run)
                prompt = "この画像に写っているテキストを、見たままの形式（改行など）をできるだけ維持して、すべて正確に抽出してください。"
                response = model.generate_content([prompt, image_to_process])
                st.markdown(response.text)
            except Exception as e:
                st.error(f"OCR処理中にエラーが発生しました: {e}")
            finally:
                st.session_state.run_ocr = False
    else:
        st.info("画像をアップロードして「OCRを実行する」ボタンを押してください。")
