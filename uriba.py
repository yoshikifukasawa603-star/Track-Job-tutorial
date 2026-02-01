import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("🗺️ 店舗レイアウト・在庫管理マップ")

# 1. データの読み込み
try:
    df = pd.read_csv('inventory (1).csv')
except FileNotFoundError:
    df = pd.read_csv('inventory.csv')

# 2. 棚の配置（マップレイアウト）
# ※CSVの「売り場場所」と名前が完全一致している必要があります
layout = {
    "チルドA-1": (0, 0), "チルドA-2": (1, 0), "チルドA-3": (2, 0),
    "冷蔵棚1": (0, 2), "冷蔵棚2": (1, 2),"冷蔵棚3": (2, 2),
    "野菜棚": (0, 3), "果物棚": (1, 3),
    "パン棚2": (0, 4), "飲料棚1": (1, 4), "飲料棚2": (2, 4)
}

# 3. 在庫条件に基づく表示ロジック
def get_status(row):
    if row['売り場在庫'] == 0:
        return 'RoyalBlue', f"欠品中<br>({row['納品予定日']}入荷)"
    elif row['売り場在庫'] <= 5:
        return 'Crimson', f"{row['商品名']}<br>在庫の場所:{row['倉庫場所']}"
    else:
        return 'MediumSeaGreen', f"{row['商品名']}<br>({row['売り場在庫']}個)"

df[['color', 'label']] = df.apply(lambda r: pd.Series(get_status(r)), axis=1)

# 4. マップの構築
fig = go.Figure()

# --- 先にすべての四角形（棚）を描画する ---
for i, row in df.iterrows():
    loc = row['売り場場所']
    if loc in layout:
        r, c = layout[loc]
        fig.add_shape(
            type="rect", x0=c, y0=r, x1=c+0.9, y1=r+0.8,
            line=dict(color="white", width=2),
            fillcolor=row['color'],
            opacity=0.8,
            layer="below" # 四角を下のレイヤーに固定
        )

# --- その後、すべての文字を上に乗せる ---
for i, row in df.iterrows():
    loc = row['売り場場所']
    if loc in layout:
        r, c = layout[loc]
        fig.add_trace(go.Scatter(
            x=[c + 0.45], y=[r + 0.4],
            mode="text",
            text=[row['label']],
            # 文字色を「黒」に変更し、視認性を上げます
            textfont=dict(size=13, color="black", family="Meiryo"),
            hoverinfo="none",
            showlegend=False
        ))

# 5. レイアウト調整
fig.update_layout(
    width=900, height=600,
    plot_bgcolor="white",
    xaxis=dict(range=[-0.5, 5.5], visible=False, fixedrange=True),
    yaxis=dict(range=[-0.5, 4.5], visible=False, fixedrange=True, scaleanchor="x"),
    margin=dict(l=20, r=20, t=20, b=20)
)

st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# デバッグ用：CSVが正しく読めているか確認（完成したら消してOK）
if st.checkbox("読み込んだデータを確認する"):
    st.write(df[['商品名', '売り場場所', '売り場在庫', '倉庫場所','倉庫在庫','納品予定日']])
