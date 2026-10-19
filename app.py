import streamlit as st
import cv2
import numpy as np
from PIL import Image
from pathlib import Path

st.set_page_config(page_title="物品位置比對", layout="wide")
st.title("📍 物品位置比對")

def load_images():
    folder = Path("images")
    folder.mkdir(exist_ok=True)
    return [p for p in folder.glob("*.*") if p.suffix.lower() in [".jpg", ".jpeg", ".png"]]

def pil_to_cv(img):
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def simple_match(img1, img2, threshold=0.3):
    """簡單比較兩張圖嘅相似度"""
    # 統一大小
    img1 = cv2.resize(img1, (200, 200))
    img2 = cv2.resize(img2, (200, 200))
    
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    # 計算差異
    diff = cv2.absdiff(img1_gray, img2_gray)
    score = 1.0 - (np.mean(diff) / 255.0)
    return score

db_paths = load_images()
if len(db_paths) == 0:
    st.warning("請喺 images/ 放入圖片")
    st.stop()

uploaded = st.file_uploader("上傳查詢圖片", type=["jpg", "jpeg", "png"])

if uploaded:
    query_pil = Image.open(uploaded).convert("RGB")
    query_cv = pil_to_cv(query_pil)
    st.image(query_pil, caption="查詢圖片", width=400)
    
    results = []
    for path in db_paths:
        try:
            db_pil = Image.open(path).convert("RGB")
            db_cv = pil_to_cv(db_pil)
            score = simple_match(query_cv, db_cv)
            results.append((path, score))
        except Exception as e:
            continue
    
    results.sort(key=lambda x: x[1], reverse=True)
    
    st.subheader("最相似圖片")
    cols = st.columns(3)
    for i, (path, score) in enumerate(results[:9]):
        with cols[i % 3]:
            st.image(str(path), caption=f"相似度: {score:.2f}")
