import streamlit as st
import cv2
import numpy as np
from PIL import Image
from pathlib import Path

st.set_page_config(page_title="咪口小廢廢勿用", layout="wide")
st.title("咪口小廢廢勿用")

def load_images():
    folder = Path("images")
    folder.mkdir(exist_ok=True)
    return [p for p in folder.glob("*.*") if p.suffix.lower() in [".jpg", ".jpeg", ".png"]]

def pil_to_cv(img):
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def find_item_positions(img_cv, template_cv, threshold=0.55):
    """搵模板喺圖片入面嘅位置"""
    img_gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    temp_gray = cv2.cvtColor(template_cv, cv2.COLOR_BGR2GRAY)
    
    # 縮細模板以提高匹配機會
    h, w = temp_gray.shape
    temp_small = cv2.resize(temp_gray, (w//3, h//3))
    
    result = cv2.matchTemplate(img_gray, temp_small, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)
    
    positions = []
    for pt in zip(*locations[::-1]):
        positions.append((pt[0], pt[1]))
    
    # 去除太近嘅重複點
    filtered = []
    for pos in positions:
        if not any(abs(pos[0]-f[0]) < 30 and abs(pos[1]-f[1]) < 30 for f in filtered):
            filtered.append(pos)
    return filtered

db_paths = load_images()
if len(db_paths) == 0:
    st.warning("請喺 images/ 放入圖片")
    st.stop()

st.sidebar.header("設定")
threshold = st.sidebar.slider("匹配門檻", 0.4, 0.8, 0.55, 0.05)

uploaded = st.file_uploader("上傳查詢圖片", type=["jpg", "jpeg", "png"])

if uploaded:
    query_pil = Image.open(uploaded).convert("RGB")
    query_cv = pil_to_cv(query_pil)
    st.image(query_pil, caption="查詢圖片", width=400)
    
    # 用第一張資料庫圖片作為參考模板
    if len(db_paths) > 0:
        ref_img = Image.open(db_paths[0]).convert("RGB")
        ref_cv = pil_to_cv(ref_img)
        
        # 從參考圖提取幾個小區域作為模板（簡單示範）
        h, w = ref_cv.shape[:2]
        templates = [
            ref_cv[int(h*0.4):int(h*0.55), int(w*0.3):int(w*0.45)],  # 中間區域
            ref_cv[int(h*0.5):int(h*0.65), int(w*0.2):int(w*0.35)],
        ]
        
        query_positions = []
        for temp in templates:
            if temp.size > 0:
                pos = find_item_positions(query_cv, temp, threshold)
                query_positions.extend(pos)
        
        st.write(f"查詢圖片搵到 {len(query_positions)} 個匹配點")
        
        # 比較每張資料庫圖片
        results = []
        for path in db_paths:
            try:
                db_pil = Image.open(path).convert("RGB")
                db_cv = pil_to_cv(db_pil)
                
                db_positions = []
                for temp in templates:
                    if temp.size > 0:
                        pos = find_item_positions(db_cv, temp, threshold)
                        db_positions.extend(pos)
                
                # 計算位置相似度（匹配點數量接近就高分）
                score = 1.0 / (1.0 + abs(len(query_positions) - len(db_positions)))
                results.append((path, score, len(db_positions)))
            except:
                continue
        
        results.sort(key=lambda x: x[1], reverse=True)
        
        st.subheader("最相似圖片")
        cols = st.columns(3)
        for i, (path, score, count) in enumerate(results[:6]):
            with cols[i % 3]:
                st.image(str(path), caption=f"分數: {score:.2f} | 匹配點: {count}")
