import streamlit as st
from PIL import Image
import imagehash
from pathlib import Path

st.set_page_config(page_title="相似圖片搜尋", layout="wide")
st.title("🖼️ 相似圖片搜尋（感知哈希）")

def load_images():
    folder = Path("images")
    folder.mkdir(exist_ok=True)
    return [p for p in folder.glob("*.*") if p.suffix.lower() in [".jpg", ".jpeg", ".png"]]

db_paths = load_images()
if len(db_paths) == 0:
    st.warning("請喺 images/ 放入圖片")
    st.stop()

# 預先計算所有圖片嘅哈希
@st.cache_data
def compute_hashes(paths):
    hashes = {}
    for p in paths:
        try:
            img = Image.open(p)
            hashes[p] = imagehash.phash(img)
        except:
            continue
    return hashes

db_hashes = compute_hashes(db_paths)

uploaded = st.file_uploader("上傳查詢圖片", type=["jpg", "jpeg", "png"])

if uploaded:
    query_img = Image.open(uploaded)
    st.image(query_img, caption="查詢圖片", width=400)
    
    query_hash = imagehash.phash(query_img)
    
    # 計算同每張圖嘅距離（越小越似）
    results = []
    for path, db_hash in db_hashes.items():
        distance = query_hash - db_hash
        results.append((path, distance))
    
    results.sort(key=lambda x: x[1])  # 距離越小越相似
    
    st.subheader("最相似圖片")
    cols = st.columns(3)
    for i, (path, dist) in enumerate(results[:9]):
        similarity = max(0, 100 - dist * 2)  # 轉成百分比
        with cols[i % 3]:
            st.image(str(path), caption=f"相似度: {similarity:.0f}% (距離: {dist})")
