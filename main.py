import streamlit as st
import pandas as pd

# CSVを読み込む
df = pd.read_csv("inventory.csv")

# 1. 準備：スイッチ（page）を「home」にセットする
if "page" not in st.session_state:
    st.session_state.page = "home"

# 2. ホームページの表示
if st.session_state.page == "home":
    st.title(" 在庫管理システム")

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

    if st.button("倉庫管理ページへ移動"):
        st.session_state.page = "warehouse"
        st.rerun()
        
   # --- 在庫管理ページの表示 ------------------------------------------------------
    elif st.session_state.page == "warehouse":
        st.title("倉庫管理ページ")

        # home backボタン(B-a)
        if st.button("ホームページへ戻る"):
            st.session_state.page = "home"
            st.rerun() 

        st.divider()

        # 選択機能（modeA~C）
        warehouse_mode = st.radio("操作を選択してくださいさい", options=["商品検索", "在庫数更新", "新規登録"],horizontal=True)

        if warehouse_mode == "商品検索":
            st.subheader("商品検索")
            search_term = st.text_input("商品名を入力してください")
            if search_term:
                results = df[df["商品名"].str.contains(search_term, case=False, na=False)]
                if not results.empty:
                    st.dataframe(results)
                else:
                    st.info("該当する商品が見つかりませんでした。")
                    if st.button("この商品を新しく登録する"):
                        st.session_state.page = "新規登録"
                        st.rerun()

            st.divider()

            if st.button("選択画面に戻る"):
                st.session_state.page = "warehouse"
                st.rerun()

        elif warehouse_mode == "在庫数更新":
            st.subheader("在庫数更新")
            st.warning("在庫数を更新してください。")
            edited_df = st.experimental_data_editor(df, use_container_width=True, key="wh_edit")
            if st.button("更新を保存"):
                edited_df.to_csv("inventory.csv", index=False)
                st.success("在庫数が更新されました。")

            st.divider()

            if st.button("選択画面に戻る"):
                st.session_state.page = "warehouse"
                st.rerun()
                
        elif warehouse_mode == "新規登録":
            st.subheader("新規登録")
            st.info("新しい商品を在庫に追加してください。")
            new_product = {}
            new_product["ジャンル"] = st.text_input("ジャンル")
            new_product["商品名"] = st.text_input("商品名")
            new_product["売り場在庫"] = st.number_input("売り場在庫", min_value=0, step=1)
            new_product["売り場場所"] = st.text_input("売り場場所")
            new_product["倉庫在庫"] = st.number_input("倉庫在庫", min_value=0, step=1)
            new_product["倉庫場所"] = st.text_input("倉庫場所")
            new_product["納品予定日"] = st.text_input("納品予定日")
            new_product["座標X"] = st.number_input("座標X", min_value=0, step=1)
            new_product["座標Y"] = st.number_input("座標Y", min_value=0, step=1)
            new_product["場所ID"] = st.text_input("場所ID")
            if st.button("新規商品を追加"):
                df = pd.concat([df, pd.DataFrame([new_product])], ignore_index=True)
                df.to_csv("inventory.csv", index=False)
                st.success("新しい商品が在庫に追加されました。")

            st.divider()

            if st.button("選択画面に戻る"):
                st.session_state.page = "warehouse"
                st.rerun()

            
            