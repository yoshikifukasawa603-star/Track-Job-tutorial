import streamlit as st
import pandas as pd
import sqlite3

# データベースの初期設定（ここは授業で習った通りに書いてみました）
def init_db():
    conn = sqlite3.connect('inventory_system.db')
    cursor = conn.cursor()
    # 従業員テーブルがなかったら作る
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# 最初にデータベースを準備する
init_db()

# --- ここからメインの処理 ---
st.title("在庫管理システム")

# サイドバーでログインか登録か選べるようにしました
menu = ["ログイン", "新規従業員登録"]
choice = st.sidebar.selectbox("メニューを選択してください", menu)

if choice == "ログイン":
    st.subheader("ログイン画面")
    
    # 入力フォーム
    user = st.text_input("従業員ID（ユーザー名）")
    pw = st.text_input("パスワード", type="password")
    
    if st.button("ログイン"):
        conn = sqlite3.connect('inventory_system.db')
        cursor = conn.cursor()
        # IDとパスワードが合ってるかチェック
        cursor.execute("SELECT * FROM employees WHERE username=? AND password=?", (user, pw))
        result = cursor.fetchone()
        conn.close()

        if result:
            st.success(f"ログイン成功！ {user}さん、お疲れ様です。")
            st.session_state["login_status"] = True # ログイン状態を保存
        else:
            st.error("従業員IDまたはパスワードが違います…")

elif choice == "新規従業員登録":
    st.subheader("従業員 新規登録")
    
    new_user = st.text_input("登録したい従業員ID")
    new_pw = st.text_input("登録したいパスワード", type="password")
    
    if st.button("登録実行"):
        if new_user == "" or new_pw == "":
            st.warning("空欄があると登録できません！")
        else:
            try:
                conn = sqlite3.connect('inventory_system.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO employees (username, password) VALUES (?, ?)", (new_user, new_pw))
                conn.commit()
                conn.close()
                st.success("登録完了！ログインメニューからログインしてください。")
            except sqlite3.IntegrityError:
                st.error("そのユーザー名はもう使われているみたいです。")

# ページ設定
st.set_page_config(page_title="在庫管理システム", layout="wide")

# CSVを読み込む
try:
    df = pd.read_csv("inventory.csv")
except FileNotFoundError:
    st.error("inventory.csv が見つかりません。")

# --- ページ移動ボタンを上部に配置 ---
if st.button("🗺️ 売り場マップ画面へ移動"):
    st.switch_page("pages/uriba.py")

st.divider()

#コメントアウトよ～ん

# 1. セッション状態の準備 (main.py内でのhome/warehouse切り替え)
if "page" not in st.session_state:
    st.session_state.page = "home"

# 2. ホームページの表示
if st.session_state.page == "home":
    st.title("🏠 ホーム：在庫アラート")

    low_stock = df[df["売り場在庫"] < 5]
    if not low_stock.empty:
        st.error("【緊急】売り場への補充が必要です！")
        st.dataframe(low_stock)

    low_stock_wh = df[df["倉庫在庫"] < 10]
    if not low_stock_wh.empty:
        st.warning("【注意】倉庫在庫が少なくなっています。")
        st.dataframe(low_stock_wh)

    if st.button("📦 倉庫管理操作ページへ"):
        st.session_state.page = "warehouse"
        st.rerun()

# 3. 倉庫管理（検索・更新・登録）の表示
elif st.session_state.page == "warehouse":
    st.title("📦 倉庫管理ページ")

    if st.button("🔙 ホームへ戻る"):
        st.session_state.page = "home"
        st.rerun()

    st.divider()
    warehouse_mode = st.radio("操作を選択", options=["商品検索", "在庫数更新", "新規登録"], horizontal=True)

    if warehouse_mode == "商品検索":
        search_term = st.text_input("商品名を入力")
        if search_term:
            results = df[df["商品名"].str.contains(search_term, case=False, na=False)]
            st.dataframe(results) if not results.empty else st.info("見つかりません。")

    elif warehouse_mode == "在庫数更新":
        edited_df = st.data_editor(df, use_container_width=True, key="wh_edit")
        if st.button("💾 更新を保存"):
            edited_df.to_csv("inventory.csv", index=False)
            st.success("保存しました！")

    elif warehouse_mode == "新規登録":
        st.subheader("🆕 新規登録")
        # （新規登録のフォーム部分は元のコードと同じ）