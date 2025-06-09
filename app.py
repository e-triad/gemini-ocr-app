import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import os
import datetime

# --- ページ設定 ---
st.set_page_config(
    page_title="Gemini OCRアプリ",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Gemini OCR アプリ")
st.caption("アップロードした画像からテキストを抽出します。")

# --- Gemini APIキーの設定 ---
google_api_key = os.environ.get("GOOGLE_API_KEY")
if not google_api_key:
    try:
        google_api_key = st.secrets["GOOGLE_API_KEY"]
    except (KeyError, FileNotFoundError):
        st.error("⚠️ Gemini APIキーが設定されていません。")
        st.info("Docker環境では -e GOOGLE_API_KEY='YOUR_API_KEY' を、ローカル環境では .streamlit/secrets.toml を設定してください。")
        st.stop()

if google_api_key:
    genai.configure(api_key=google_api_key)
else:
    st.error("APIキーの取得に失敗しました。アプリケーションを停止します。")
    st.stop()

# --- 料金単価の定義 ---
PRICING = {
    "gemini-2.5-pro-preview-06-05": {"input": 3.50, "output": 10.50},
    "gemini-2.5-flash-preview-05-20": {"input": 0.15, "output": 0.60}
}

# --- ★★★ セッションステートの初期化 ★★★ ---
# 累計料金、履歴リストなどを初期化
if 'total_cost' not in st.session_state:
    st.session_state.total_cost = 0
if 'history' not in st.session_state:
    st.session_state.history = []
if 'ocr_result' not in st.session_state:
    st.session_state.ocr_result = None
if 'run_ocr' not in st.session_state:
    st.session_state.run_ocr = False


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
        1. 左側のエリアに画像ファイルをアップロードします。
        2. **「OCRを実行する」**ボタンをクリックします。
        3. 右側のエリアに抽出されたテキストと利用料金が表示されます。
        4. 「実行履歴」タブで過去の実行結果も確認できます。
        """
    )
    st.divider()
    st.info("このアプリはGoogleのGemini APIを使用しています。")
    st.subheader("💰 セッション内累計料金")
    st.metric(label="Total Cost (USD)", value=f"${st.session_state.total_cost:,.8f}")
    st.caption("※このセッション内での累計料金の概算です。")


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
                # 実行時に古い結果をクリア
                st.session_state.ocr_result = None

                st.session_state.run_ocr = True
                img_byte_arr = io.BytesIO()
                image_format = image.format if image.format in ['JPEG', 'PNG'] else 'PNG'
                image.save(img_byte_arr, format=image_format)
                st.session_state.image_bytes = img_byte_arr.getvalue()
                st.session_state.model_name_on_run = model_name
                # ボタンが押されたら即座に再実行してspinnerを表示
                st.rerun()

        except Exception as e:
            st.error(f"画像の読み込み中にエラーが発生しました: {e}")

# --- 右カラム：OCR結果表示 ---
with right_column:
    # --- 処理の実行部分 ---
    if st.session_state.run_ocr:
        with st.spinner(f"`{st.session_state.model_name_on_run}` で処理を実行中..."):
            try:
                image_to_process = Image.open(io.BytesIO(st.session_state.image_bytes))
                model = genai.GenerativeModel(st.session_state.model_name_on_run)
                prompt = "この画像に写っているテキストを、見たままの形式（改行など）をできるだけ維持して、すべて正確に抽出してください。"

                response = model.generate_content([prompt, image_to_process])

                # --- 料金計算 ---
                usage_metadata = response.usage_metadata
                prompt_tokens = usage_metadata.prompt_token_count
                candidates_tokens = usage_metadata.candidates_token_count

                model_pricing = PRICING.get(st.session_state.model_name_on_run, {"input": 0, "output": 0})
                input_cost = (prompt_tokens / 1_000_000) * model_pricing["input"]
                output_cost = (candidates_tokens / 1_000_000) * model_pricing["output"]
                total_cost_this_run = input_cost + output_cost

                # --- ★★★ 結果をセッションに保存 ★★★ ---
                st.session_state.total_cost += total_cost_this_run

                # 最新の結果を保存
                result_data = {
                    "timestamp": datetime.datetime.now(),
                    "model_name": st.session_state.model_name_on_run,
                    "text": response.text,
                    "prompt_tokens": prompt_tokens,
                    "candidates_tokens": candidates_tokens,
                    "input_cost": input_cost,
                    "output_cost": output_cost,
                    "total_cost_this_run": total_cost_this_run
                }
                st.session_state.ocr_result = result_data
                # 履歴リストの先頭に追加
                st.session_state.history.insert(0, result_data)

            except Exception as e:
                st.error(f"OCR処理中にエラーが発生しました: {e}")
                st.session_state.ocr_result = None # エラー時は結果をクリア
            finally:
                st.session_state.run_ocr = False
                st.rerun()

    # --- ★★★ 結果の表示部分（タブ化） ★★★ ---
    st.header("📝 結果と履歴")
    # 履歴タブに件数を表示
    history_count = len(st.session_state.history)
    tab1, tab2 = st.tabs(["今回の実行結果", f"実行履歴 ({history_count})"])

    # --- 「今回の実行結果」タブ ---
    with tab1:
        if st.session_state.ocr_result:
            result = st.session_state.ocr_result

            st.markdown("### 抽出されたテキスト")
            st.markdown(result["text"])
            st.divider()
            st.subheader("📊 利用料金詳細")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("入力トークン数", f"{result['prompt_tokens']:,}")
                st.caption(f"($ {result['input_cost']:,.8f})")
            with col2:
                st.metric("出力トークン数", f"{result['candidates_tokens']:,}")
                st.caption(f"($ {result['output_cost']:,.8f})")

            st.success(f"**今回の利用料金 (概算): ${result['total_cost_this_run']:,.8f}**")
            st.caption("※料金はモデルの公式料金体系に基づいた概算値です。")
        else:
            st.info("画像をアップロードして「OCRを実行する」ボタンを押してください。")

    # --- 「実行履歴」タブ ---
    with tab2:
        if not st.session_state.history:
            st.info("まだ実行履歴はありません。")
        else:
            st.caption("過去の実行結果を新しい順に表示しています。")
            for i, item in enumerate(st.session_state.history):
                # expanderを使って各履歴を折りたたみ表示
                with st.expander(f"**{item['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}** | `{item['model_name']}` | **${item['total_cost_this_run']:,.8f}**"):
                    st.markdown("##### 料金詳細")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("合計料金(USD)", f"${item['total_cost_this_run']:,.8f}")
                    c2.metric("入力トークン", f"{item['prompt_tokens']:,}")
                    c3.metric("出力トークン", f"{item['candidates_tokens']:,}")

                    st.markdown("##### 抽出テキスト")
                    # text_areaにユニークなキーを設定
                    st.text_area("Text", value=item['text'], height=150, disabled=True, key=f"history_text_{i}")
