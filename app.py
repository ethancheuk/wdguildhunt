import streamlit as st
from PIL import Image
from pathlib import Path
import json

st.set_page_config(page_title="物品搜尋", layout="wide")
st.title("📍 物品搜尋")

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

st.sidebar.header("搜尋條件")

# 龍頭
dragon_dir = st.sidebar.selectbox("龍頭方向", ["不限", "up", "down", "left", "right"])

# 面具
mask_count = st.sidebar.number_input("面具數量", 0, 2, 0)

# 刀
knife_count = st.sidebar.number_input("刀數量", 0, 1, 0)
knife_dir = st.sidebar.selectbox("刀方向", ["不限", "up", "down", "left", "right"])

# 貝殼
shell_count = st.sidebar.number_input("貝殼數量", 0, 2, 0)

# 王冠
crown_count = st.sidebar.number_input("王冠數量", 0, 2, 0)
crown_dir = st.sidebar.selectbox("王冠方向", ["不限", "up", "down", "left", "right"])

# 杖
staff_count = st.sidebar.number_input("杖數量", 0, 1, 0)
staff_dir = st.sidebar.selectbox("杖方向", ["不限", "up", "down", "left", "right"])

# 鉤
hook_count = st.sidebar.number_input("鉤數量", 0, 1, 0)
hook_dir = st.sidebar.selectbox("鉤方向", ["不限", "up", "down", "left", "right"])

# 天秤
scale_count = st.sidebar.number_input("天秤數量", 0, 1, 0)
scale_dir = st.sidebar.selectbox("天秤方向", ["不限", "up", "down", "left", "right"])

# 鑽石
diamond_count = st.sidebar.number_input("鑽石數量", 0, 5, 0)

if st.sidebar.button("搜尋"):
    results = []
    for path in db_paths:
        data = IMAGE_DATA.get(path.name, {})
        match = True
        
        if dragon_dir != "不限" and data.get("dragon") != dragon_dir:
            match = False
        if mask_count > 0 and data.get("mask", 0) != mask_count:
            match = False
        if knife_count > 0 and data.get("knife", 0) != knife_count:
            match = False
        if knife_dir != "不限" and data.get("knife_dir") != knife_dir:
            match = False
        if shell_count > 0 and data.get("shell", 0) != shell_count:
            match = False
        if crown_count > 0 and data.get("crown", 0) != crown_count:
            match = False
        if crown_dir != "不限" and data.get("crown_dir") != crown_dir:
            match = False
        if staff_count > 0 and data.get("staff", 0) != staff_count:
            match = False
        if staff_dir != "不限" and data.get("staff_dir") != staff_dir:
            match = False
        if hook_count > 0 and data.get("hook", 0) != hook_count:
            match = False
        if hook_dir != "不限" and data.get("hook_dir") != hook_dir:
            match = False
        if scale_count > 0 and data.get("scale", 0) != scale_count:
            match = False
        if scale_dir != "不限" and data.get("scale_dir") != scale_dir:
            match = False
        if diamond_count > 0 and data.get("diamond", 0) != diamond_count:
            match = False
        
        if match:
            results.append(path)
    
    st.subheader(f"搵到 {len(results)} 張")
    if results:
        cols = st.columns(3)
        for i, p in enumerate(results[:15]):
            with cols[i % 3]:
                st.image(str(p), caption=p.name, use_container_width=True)
    else:
        st.info("冇結果")
else:
    st.info("請喺左邊輸入條件，然後撳搜尋")
    st.write(f"資料庫有 {len(IMAGE_DATA)} 筆描述")
