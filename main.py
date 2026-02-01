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

st.title(" 在庫管理システム")

# CSVを読み込む
df = pd.read_csv("inventory.csv")

# 売り場アラート (A-a) - 緊急度が高いので st.error (赤)
low_stock = df[df["売り場在庫"] < 5]
if not low_stock.empty:
    st.error("🚨 【緊急】売り場への補充が必要です！") # 赤色で表示
    st.dataframe(low_stock)

# 倉庫アラート (A-a) - 次のステップなので st.warning (黄)
low_stock_warehouse = df[df["倉庫在庫"] < 10]
if not low_stock_warehouse.empty:
    st.warning("⚠️ 【注意】倉庫在庫が少なくなっています。納品を確認してください。") # 黄色で表示
    st.dataframe(low_stock_warehouse)

# 在庫一覧表示 (A-b)
st.subheader("在庫一覧")
st.dataframe(df)

# 更新機能（B-c）
st.subheader("在庫数の更新")

edited_df = st.data_editor(df, use_container_width=True)

if st.button("更新を保存"):
    edited_df.to_csv("inventory.csv", index=False)
    st.success("在庫情報が更新されました！")

# 新商品追加機能（B-d）
st.subheader("新商品を追加")