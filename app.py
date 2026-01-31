import streamlit as st

st.title("こんにちは、Streamlit！")
st.write("ついに自分のアプリが動き出しました。")

name = st.text_input("お名前を教えてください")
if name:
    st.write(f"こんにちは、{name}さん！")