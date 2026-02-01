import streamlit as st
import pandas as pd
import sqlite3

# --- ページ設定（一番最初に書くのがお作法です） ---
st.set_page_config(page_title="在庫管理システム", layout="wide")

# データベースの初期設定
def init_db():
    conn = sqlite3.connect('inventory_system.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# CSVの読み込み
try:
    df = pd.read_csv("inventory.csv")
except FileNotFoundError:
    st.error("inventory.csv が見つかりません。")
    df = pd.DataFrame() # エラー防止用に空の台帳を作る

# --- ログイン・会員登録機能（サイドバー） ---
st.sidebar.title("🔑 従業員認証")
menu = ["ログイン", "新規従業員登録"]
choice = st.sidebar.selectbox("メニューを選択してください", menu)

# ログイン状態の初期化
if "login_status" not in st.session_state:
    st.session_state["login_status"] = False

if choice == "ログイン":
    st.sidebar.subheader("ログイン画面")
    user = st.sidebar.text_input("従業員ID")
    pw = st.sidebar.text_input("パスワード", type="password")
    
    if st.sidebar.button("ログイン"):
        conn = sqlite3.connect('inventory_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE username=? AND password=?", (user, pw))
        result = cursor.fetchone()
        conn.close()

        if result:
            st.session_state["login_status"] = True
            st.sidebar.success(f"ログイン成功！ {user}さん")
        else:
            st.sidebar.error("IDまたはパスワードが違います")

elif choice == "新規従業員登録":
    st.sidebar.subheader("新規登録")
    new_user = st.sidebar.text_input("登録用ID")
    new_pw = st.sidebar.text_input("登録用パスワード", type="password")
    if st.sidebar.button("登録実行"):
        try:
            conn = sqlite3.connect('inventory_system.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO employees (username, password) VALUES (?, ?)", (new_user, new_pw))
            conn.commit()
            conn.close()
            st.sidebar.success("登録完了！")
        except sqlite3.IntegrityError:
            st.sidebar.error("そのIDは既に使われています")

# --- メインコンテンツ（ログインしている時だけ表示） ---
if st.session_state["login_status"]:
    st.title("📦 在庫管理メインパネル")

    if st.button("🗺️ 売り場マップ画面へ移動"):
        st.switch_page("pages/uriba.py")

    st.divider()

    # 1. 画面切り替えスイッチ
    if "page" not in st.session_state:
        st.session_state.page = "home"

    # 2. ホーム（アラート表示）
    if st.session_state.page == "home":
        st.subheader("🏠 ホーム：在庫アラート")
        
        # 売り場アラート
        low_stock = df[df["売り場在庫"] < 5]
        if not low_stock.empty:
            st.error("🚨 【緊急】売り場への補充が必要です！")
            st.dataframe(low_stock)
            cols = st.columns(len(low_stock))
            for i, (index, row) in enumerate(low_stock.iterrows()):
                with cols[i]:
                    st.metric(label=row["商品名"], value=f"{row['売り場在庫']}個", delta=f"{row['売り場在庫']-5}不足", delta_color="inverse")

        # 倉庫アラート
        low_stock_wh = df[df["倉庫在庫"] < 10]
        if not low_stock_wh.empty:
            st.warning("⚠️ 【注意】倉庫在庫が少なくなっています。")
            wh_cols = st.columns(len(low_stock_wh))
            for i, (index, row) in enumerate(low_stock_wh.iterrows()):
                with wh_cols[i]:
                    st.metric(label=f"📦 {row['商品名']}", value=f"{row['倉庫在庫']}個", delta="補充が必要", delta_color="off")

        if st.button("📦 倉庫管理操作ページへ"):
            st.session_state.page = "warehouse"
            st.rerun()

    # 3. 倉庫管理ページ
    elif st.session_state.page == "warehouse":
        st.subheader("🏭 倉庫管理詳細")
        if st.button("🔙 ホームへ戻る"):
            st.session_state.page = "home"
            st.rerun()
        
        mode = st.radio("操作を選択", ["商品検索", "在庫数更新", "新規登録"], horizontal=True)
        # （ここに各モードの処理を書く）

else:
    st.info("左側のメニューからログインしてください。")