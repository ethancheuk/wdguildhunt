import streamlit as st
from PIL import Image
import imagehash
from pathlib import Path

st.set_page_config(page_title="咪口小廢廢勿用", layout="wide")
st.title("咪口小廢廢勿用")

def load_images():
    folder = Path("images")
    folder.mkdir(exist_ok=True)
    return [p for p in folder.glob("*.*") if p.suffix.lower() in [".jpg", ".jpeg", ".png"]]

def crop_grid_area(img, left_pct, top_pct, right_pct, bottom_pct):
    w, h = img.size
    left = int(w * left_pct)
    top = int(h * top_pct)
    right = int(w * right_pct)
    bottom = int(h * bottom_pct)
    return img.crop((left, top, right, bottom))

db_paths = load_images()
if len(db_paths) == 0:
    st.warning("請喺 images/ 放入圖片")
    st.stop()

# 側邊欄調整裁剪範圍
st.sidebar.header("裁剪範圍調整")
left_pct = st.sidebar.slider("左邊", 0.0, 0.3, 0.05, 0.01)
top_pct = st.sidebar.slider("上面", 0.15, 0.45, 0.28, 0.01)
right_pct = st.sidebar.slider("右邊", 0.7, 1.0, 0.95, 0.01)
bottom_pct = st.sidebar.slider("下面", 0.6, 0.9, 0.78, 0.01)

uploaded = st.file_uploader("上傳查詢圖片", type=["jpg", "jpeg", "png"])

if uploaded:
    query_img = Image.open(uploaded)
    query_grid = crop_grid_area(query_img, left_pct, top_pct, right_pct, bottom_pct)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(query_img, caption="原圖", use_container_width=True)
    with col2:
        st.image(query_grid, caption="裁剪後", use_container_width=True)
    
    # 用目前裁剪範圍計算所有圖片
    query_hash = imagehash.phash(query_grid)
    
    results = []
    for path in db_paths:
        try:
            db_img = Image.open(path)
            db_grid = crop_grid_area(db_img, left_pct, top_pct, right_pct, bottom_pct)
            db_hash = imagehash.phash(db_grid)
            distance = query_hash - db_hash
            results.append((path, distance, db_grid))
        except:
            continue
    
    results.sort(key=lambda x: x[1])
    
    st.subheader("最相似格子佈局")
    cols = st.columns(3)
    for i, (path, dist, grid_img) in enumerate(results[:9]):
        similarity = max(0, 100 - dist * 3)
        with cols[i % 3]:
            st.image(grid_img, caption=f"相似度: {similarity:.0f}%", use_container_width=True)
