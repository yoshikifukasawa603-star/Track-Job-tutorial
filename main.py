import streamlit as st
import pandas as pd

# CSVを読み込む
df = pd.read_csv("inventory.csv")

# 1. 準備
if "page" not in st.session_state:
    st.session_state.page = "home"

# 2. ホームページの表示
if st.session_state.page == "home":
    st.title("🏠 在庫管理システム")

    # --- 売り場アラート（赤） ---
    low_stock = df[df["売り場在庫"] < 5]
    if not low_stock.empty:
        st.error("🚨 【緊急】売り場への補充が必要です！")
        st.dataframe(low_stock)
        
        st.write("### 補充が必要な商品")
        cols = st.columns(len(low_stock))
        for i, (index, row) in enumerate(low_stock.iterrows()):
            with cols[i]:
                # st.image を st.metric に修正
                st.metric(
                    label=row["商品名"], 
                    value=f"{row['売り場在庫']}個", 
                    delta=f"{row['売り場在庫'] - 5}個不足", 
                    delta_color="inverse"
                )

    # --- 倉庫アラート（黄） ---
    low_stock_wh = df[df["倉庫在庫"] < 10]
    if not low_stock_wh.empty:
        st.warning("⚠️ 【注意】倉庫在庫が少なくなっています。")
        st.dataframe(low_stock_wh)
        
        st.write("### 倉庫の在庫状況（早めの手配を！）")
        wh_cols = st.columns(len(low_stock_wh)) # 変数名を統一
        for i, (index, row) in enumerate(low_stock_wh.iterrows()):
            with wh_cols[i]:
                st.metric(
                    label=f"📦 {row['商品名']}", 
                    value=f"{row['倉庫在庫']}個", 
                    delta="補充が必要", 
                    delta_color="off"
                )

    if st.button("倉庫管理ページへ移動"):
        st.session_state.page = "warehouse"
        st.rerun()

# 3. 在庫管理ページの表示
elif st.session_state.page == "warehouse":
    st.title(" 倉庫管理ページ")

    if st.button(" ホームページへ戻る"):
        st.session_state.page = "home"
        st.rerun()

    st.divider()

    # 操作の選択
    warehouse_mode = st.radio("操作を選択してください", options=["商品検索", "在庫数更新", "新規登録"], horizontal=True)

    if warehouse_mode == "商品検索":
        st.subheader(" 商品検索")
        search_term = st.text_input("商品名を入力してください")
        if search_term:
            results = df[df["商品名"].str.contains(search_term, case=False, na=False)]
            if not results.empty:
                st.dataframe(results)
            else:
                st.info("該当する商品が見つかりませんでした。")

    elif warehouse_mode == "在庫数更新":
        st.subheader(" 在庫数更新")
        # 最新の関数 st.data_editor を使います
        edited_df = st.data_editor(df, use_container_width=True, key="wh_edit")
        if st.button(" 更新を保存"):
            edited_df.to_csv("inventory.csv", index=False)
            st.success("在庫数が更新されました！")

    elif warehouse_mode == "新規登録":
        st.subheader("🆕 新規登録")
        
        new_item = {}
        col1, col2 = st.columns(2)
        with col1:
            new_item["ジャンル"] = st.text_input("ジャンル")
            new_item["商品名"] = st.text_input("商品名")
            new_item["場所ID"] = st.text_input("場所ID")
        with col2:
            new_item["座標X"] = st.number_input("座標X", min_value=0, step=1)
            new_item["座標Y"] = st.number_input("座標Y", min_value=0, step=1)
            new_item["納品予定日"] = st.text_input("納品予定日")

        if st.button(" 新規商品を追加"):
            df = pd.concat([df, pd.DataFrame([new_item])], ignore_index=True)
            df.to_csv("inventory.csv", index=False)
            st.success("商品を追加しました！")
            st.rerun()