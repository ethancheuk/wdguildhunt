import streamlit as st
from PIL import Image
import numpy as np
from pathlib import Path
from skimage.metrics import structural_similarity as ssim
import cv2

st.set_page_config(page_title="位置比對", layout="wide")
st.title("📍 圖片位置比對")

def load_images():
    folder = Path("images")
    folder.mkdir(exist_ok=True)
    return [p for p in folder.glob("*.*") if p.suffix.lower() in [".jpg", ".jpeg", ".png"]]

def resize_for_compare(img, size=(256, 256)):
    return cv2.resize(np.array(img.convert("L")), size)

db_paths = load_images()
if len(db_paths) == 0:
    st.warning("請喺 images/ 放入圖片")
    st.stop()

uploaded = st.file_uploader("上傳查詢圖片", type=["jpg", "jpeg", "png"])

if uploaded:
    query_img = Image.open(uploaded).convert("RGB")
    st.image(query_img, caption="查詢圖片", width=400)
    
    query_gray = resize_for_compare(query_img)
    
    results = []
    for path in db_paths:
        try:
            db_img = Image.open(path).convert("RGB")
            db_gray = resize_for_compare(db_img)
            score = ssim(query_gray, db_gray)
            results.append((path, score))
        except:
            continue
    
    results.sort(key=lambda x: x[1], reverse=True)
    
    st.subheader("最相似圖片（按結構相似度）")
    cols = st.columns(3)
    for i, (path, score) in enumerate(results[:9]):
        with cols[i % 3]:
            st.image(str(path), caption=f"相似度: {score:.3f}")
