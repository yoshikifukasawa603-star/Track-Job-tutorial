import streamlit as st
import pandas as pd

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

# 在庫のサイドバー表示 (A-b)
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