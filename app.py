import streamlit as st
import cv2
import numpy as np
from PIL import Image
from pathlib import Path

st.set_page_config(page_title="位置比對", layout="wide")
st.title("📍 圖片位置比對（非 AI）")

def load_images():
    folder = Path("images")
    folder.mkdir(exist_ok=True)
    paths = [p for p in folder.glob("*.*") if p.suffix.lower() in [".jpg", ".jpeg", ".png"]]
    return paths

def pil_to_cv(img):
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def find_objects(img, template, threshold=0.6):
    """用模板匹配搵物件位置"""
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    temp_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    result = cv2.matchTemplate(img_gray, temp_gray, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)
    
    points = []
    for pt in zip(*locations[::-1]):
        points.append(pt)
    return points

# 讀取資料庫圖片
db_paths = load_images()
if len(db_paths) == 0:
    st.warning("請喺 images/ 放入圖片")
    st.stop()

st.sidebar.header("設定")
threshold = st.sidebar.slider("匹配門檻", 0.4, 0.9, 0.6, 0.05)

uploaded = st.file_uploader("上傳查詢圖片", type=["jpg", "jpeg", "png"])

if uploaded:
    query_pil = Image.open(uploaded).convert("RGB")
    query_cv = pil_to_cv(query_pil)
    st.image(query_pil, caption="查詢圖片", width=400)
    
    # 用第一張資料庫圖片作為模板示範（實際可改成特定物件模板）
    template_path = db_paths[0]
    template_pil = Image.open(template_path).convert("RGB")
    template_cv = pil_to_cv(template_pil)
    
    # 縮小模板（可選）
    h, w = template_cv.shape[:2]
    template_small = cv2.resize(template_cv, (w//4, h//4))
    
    query_points = find_objects(query_cv, template_small, threshold)
    
    st.write(f"查詢圖片搵到 {len(query_points)} 個匹配點")
    
    # 比較每張資料庫圖片
    results = []
    for path in db_paths:
        try:
            db_pil = Image.open(path).convert("RGB")
            db_cv = pil_to_cv(db_pil)
            db_points = find_objects(db_cv, template_small, threshold)
            
            # 簡單位置相似度：匹配點數量差異
            score = 1.0 / (1.0 + abs(len(query_points) - len(db_points)))
            results.append((path, score, len(db_points)))
        except:
            continue
    
    results.sort(key=lambda x: x[1], reverse=True)
    
    st.subheader("最相似圖片（按位置匹配）")
    cols = st.columns(3)
    for i, (path, score, count) in enumerate(results[:6]):
        with cols[i % 3]:
            st.image(str(path), caption=f"分數: {score:.2f} | 匹配點: {count}")
