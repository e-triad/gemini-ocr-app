import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- ページ設定 ---
st.set_page_config(
    page_title="Gemini OCRアプリ",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Gemini OCR アプリ")
st.caption("アップロードした画像からテキストを抽出します。")

# --- Gemini APIキーの設定 ---
# StreamlitのSecrets機能からAPIキーを取得
try:
    # st.secrets['GOOGLE_API_KEY']で環境変数を参照
    google_api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=google_api_key)
except (KeyError, FileNotFoundError):
    st.error("⚠️ Gemini APIキーが設定されていません。")
    st.info("StreamlitのSecretsに `GOOGLE_API_KEY = 'YOUR_API_KEY'` を設定してください。")
    st.stop()


# --- サイドバー ---
with st.sidebar:
    st.header("⚙️ 設定")
    # st.radioを使用してモデルを選択
    model_choice = st.radio(
        "使用するモデルを選択してください:",
        ("Gemini 2.5 Flash", "Gemini 2.5 Pro"),
        captions=["⚡ 高速・低コストなモデル", "✨ 高精度なモデル"]
    )
    # 選択に応じてモデル名を決定
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
# st.columnsで画面を左右に分割
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
            # アップロードされた画像を表示
            image = Image.open(uploaded_file)
            st.image(image, caption="アップロードされた画像", use_column_width=True)

            # OCR実行ボタン
            if st.button("🔍 OCRを実行する", use_container_width=True, type="primary"):
                # st.session_stateを使って、ボタンが押された状態と画像データを保持
                st.session_state.run_ocr = True
                
                # PIL Imageをバイトデータに変換して保存（再実行時のため）
                img_byte_arr = io.BytesIO()
                # 画像のフォーマットを維持しつつ保存
                image_format = image.format if image.format in ['JPEG', 'PNG'] else 'PNG'
                image.save(img_byte_arr, format=image_format)
                st.session_state.image_bytes = img_byte_arr.getvalue()
                
                # 実行時のモデル名も保存
                st.session_state.model_name_on_run = model_name

        except Exception as e:
            st.error(f"画像の読み込み中にエラーが発生しました: {e}")

# --- 右カラム：OCR結果表示 ---
with right_column:
    st.header("📝 OCR結果")

    # セッションステートに `run_ocr` フラグがあるかチェック
    if 'run_ocr' in st.session_state and st.session_state.run_ocr:
        # スピナーで処理中であることを表示
        with st.spinner(f"`{st.session_state.model_name_on_run}` で処理を実行中..."):
            try:
                # セッションステートから画像バイトデータを読み込み
                image_to_process = Image.open(io.BytesIO(st.session_state.image_bytes))

                # Geminiモデルの初期化
                model = genai.GenerativeModel(st.session_state.model_name_on_run)

                # Geminiへのプロンプト（指示文）
                prompt = "この画像に写っているテキストを、見たままの形式（改行など）をできるだけ維持して、すべて正確に抽出してください。"

                # Gemini APIを呼び出してOCR実行
                response = model.generate_content([prompt, image_to_process])

                # 結果をマークダウンで表示
                st.markdown(response.text)

            except Exception as e:
                st.error(f"OCR処理中にエラーが発生しました: {e}")
            finally:
                # 処理が終わったらフラグをリセットし、再実行に備える
                st.session_state.run_ocr = False
    else:
        st.info("画像をアップロードして「OCRを実行する」ボタンを押してください。")
