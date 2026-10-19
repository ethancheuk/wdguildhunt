import streamlit as st
from PIL import Image
from pathlib import Path
import json

st.set_page_config(page_title="物品搜尋", layout="wide")
st.title("📍 物品搜尋")

# 讀取描述
desc_file = Path("descriptions.json")
if desc_file.exists():
    with open(desc_file, "r", encoding="utf-8") as f:
        IMAGE_DATA = json.load(f)
else:
    IMAGE_DATA = {}
    st.warning("搵唔到 descriptions.json")

def load_images():
    folder = Path("images")
    folder.mkdir(exist_ok=True)
    return list(folder.glob("*.png")) + list(folder.glob("*.jpg"))

db_paths = load_images()

# 搜尋表單
st.sidebar.header("搜尋條件")
dragon = st.sidebar.selectbox("龍頭方向", ["不限", "up", "down", "left", "right"])
mask = st.sidebar.number_input("面具數量", 0, 5, 0)

if st.sidebar.button("搜尋"):
    results = []
    for path in db_paths:
        data = IMAGE_DATA.get(path.name, {})
        match = True
        
        if dragon != "不限" and data.get("dragon") != dragon:
            match = False
        if mask > 0 and data.get("mask", 0) != mask:
            match = False
        
        if match:
            results.append(path)
    
    st.subheader(f"搵到 {len(results)} 張")
    if results:
        cols = st.columns(3)
        for i, p in enumerate(results[:12]):
            with cols[i % 3]:
                st.image(str(p), caption=p.name)
    else:
        st.info("冇結果")
else:
    st.info("請喺左邊輸入條件")
    st.write(f"資料庫有 {len(IMAGE_DATA)} 筆描述")
