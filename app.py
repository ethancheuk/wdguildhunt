import streamlit as st
from PIL import Image
import imagehash
from pathlib import Path
import numpy as np

st.set_page_config(page_title="唔俾咪口小廢廢用", layout="wide")
st.title("唔俾咪口小廢廢用")

def load_images():
    folder = Path("images")
    folder.mkdir(exist_ok=True)
    return [p for p in folder.glob("*.*") if p.suffix.lower() in [".jpg", ".jpeg", ".png"]]

def crop_grid_area(img):
    """裁剪中間遊戲格子區域（根據你遊戲截圖調整比例）"""
    w, h = img.size
    # 中間格子大約佔畫面 30%-75% 高度
    left = int(w * 0.08)
    top = int(h * 0.32)
    right = int(w * 0.92)
    bottom = int(h * 0.72)
    return img.crop((left, top, right, bottom))

db_paths = load_images()
if len(db_paths) == 0:
    st.warning("請喺 images/ 放入圖片")
    st.stop()

@st.cache_data
def compute_grid_hashes(paths):
    hashes = {}
    for p in paths:
        try:
            img = Image.open(p)
            grid = crop_grid_area(img)
            hashes[p] = imagehash.phash(grid)
        except:
            continue
    return hashes

db_hashes = compute_grid_hashes(db_paths)

uploaded = st.file_uploader("上傳查詢圖片", type=["jpg", "jpeg", "png"])

if uploaded:
    query_img = Image.open(uploaded)
    query_grid = crop_grid_area(query_img)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(query_img, caption="原圖", use_container_width=True)
    with col2:
        st.image(query_grid, caption="裁剪後嘅格子區域", use_container_width=True)
    
    query_hash = imagehash.phash(query_grid)
    
    results = []
    for path, db_hash in db_hashes.items():
        distance = query_hash - db_hash
        results.append((path, distance))
    
    results.sort(key=lambda x: x[1])
    
    st.subheader("最相似格子佈局")
    cols = st.columns(3)
    for i, (path, dist) in enumerate(results[:9]):
        similarity = max(0, 100 - dist * 3)
        with cols[i % 3]:
            db_img = Image.open(path)
            db_grid = crop_grid_area(db_img)
            st.image(db_grid, caption=f"相似度: {similarity:.0f}%", use_container_width=True)
