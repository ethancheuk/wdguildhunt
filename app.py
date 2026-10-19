import streamlit as st
from PIL import Image
from pathlib import Path
import json

st.set_page_config(page_title="物品搜尋", layout="wide")
st.title("📍 物品搜尋")

desc_file = Path("descriptions.json")
if desc_file.exists():
    with open(desc_file, "r", encoding="utf-8") as f:
        data_list = json.load(f)
    IMAGE_DATA = {item["檔名"]: item for item in data_list}
else:
    IMAGE_DATA = {}
    st.warning("搵唔到 descriptions.json")

def load_images():
    folder = Path("images")
    folder.mkdir(exist_ok=True)
    return list(folder.glob("*.png")) + list(folder.glob("*.jpg"))

db_paths = load_images()

st.sidebar.header("搜尋條件")

dragon_dir = st.sidebar.selectbox("龍頭方向", ["不限", "up", "down", "left", "right"])
mask_count = st.sidebar.number_input("面具數量", 0, 2, 0)
knife_count = st.sidebar.number_input("刀數量", 0, 1, 0)
knife_dir = st.sidebar.selectbox("刀方向", ["不限", "up", "down", "left", "right"])
shell_count = st.sidebar.number_input("貝殼數量", 0, 2, 0)

# 王冠（支援 2 個方向）
crown_count = st.sidebar.number_input("王冠數量", 0, 2, 0)
crown_dirs = []
if crown_count >= 1:
    crown_dir1 = st.sidebar.selectbox("王冠方向 1", ["不限", "up", "down", "left", "right"])
    crown_dirs.append(crown_dir1)
if crown_count >= 2:
    crown_dir2 = st.sidebar.selectbox("王冠方向 2", ["不限", "up", "down", "left", "right"])
    crown_dirs.append(crown_dir2)

staff_count = st.sidebar.number_input("杖數量", 0, 1, 0)
staff_dir = st.sidebar.selectbox("杖方向", ["不限", "up", "down", "left", "right"])
hook_count = st.sidebar.number_input("鉤數量", 0, 1, 0)
hook_dir = st.sidebar.selectbox("鉤方向", ["不限", "up", "down", "left", "right"])
scale_count = st.sidebar.number_input("天秤數量", 0, 1, 0)
scale_dir = st.sidebar.selectbox("天秤方向", ["不限", "up", "down", "left", "right"])
diamond_count = st.sidebar.number_input("鑽石數量", 0, 5, 0)

if st.sidebar.button("搜尋"):
    results = []
    for path in db_paths:
        data = IMAGE_DATA.get(path.name, {})
        match = True
        
        if dragon_dir != "不限" and data.get("龍頭方向") != dragon_dir:
            match = False
        if mask_count > 0 and str(data.get("面具數量", "0")) != str(mask_count):
            match = False
        if knife_count > 0 and str(data.get("刀數量", "0")) != str(knife_count):
            match = False
        if knife_dir != "不限" and data.get("刀方向") != knife_dir:
            match = False
        if shell_count > 0 and str(data.get("貝殼數量", "0")) != str(shell_count):
            match = False
        
        # 王冠
        crowns_str = data.get("王冠方向", "")
        crowns = [c.strip() for c in crowns_str.split(",") if c.strip()] if crowns_str else []
        if crown_count > 0 and len(crowns) != crown_count:
            match = False
        for d in crown_dirs:
            if d != "不限" and d not in crowns:
                match = False
        
        if staff_count > 0 and str(data.get("杖數量", "0")) != str(staff_count):
            match = False
        if staff_dir != "不限" and data.get("杖方向") != staff_dir:
            match = False
        if hook_count > 0 and str(data.get("鉤數量", "0")) != str(hook_count):
            match = False
        if hook_dir != "不限" and data.get("鉤方向") != hook_dir:
            match = False
        if scale_count > 0 and str(data.get("天秤數量", "0")) != str(scale_count):
            match = False
        if scale_dir != "不限" and data.get("天秤方向") != scale_dir:
            match = False
        if diamond_count > 0 and str(data.get("鑽石數量", "0")) != str(diamond_count):
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
