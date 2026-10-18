import streamlit as st
import torch
import open_clip
from PIL import Image
import numpy as np
from pathlib import Path

st.set_page_config(page_title="相似圖片搜尋", layout="wide")
st.title("🖼️ 相似圖片搜尋")

# 載入模型
@st.cache_resource
def load_model():
    model, _, preprocess = open_clip.create_model_and_transforms(
        'ViT-L-14', pretrained='openai'
    )
    model.eval()
    return model, preprocess

model, preprocess = load_model()

# 讀取圖片
@st.cache_data
def load_database_images():
    image_folder = Path("images")
    image_folder.mkdir(exist_ok=True)
    paths = list(image_folder.glob("*.*"))
    paths = [p for p in paths if p.suffix.lower() in [".jpg", ".jpeg", ".png"]]
    return paths

db_paths = load_database_images()

if len(db_paths) == 0:
    st.warning("請喺 images/ 資料夾放入圖片，然後重新部署。")
    st.stop()

# 計算資料庫 embedding（會自動重新計算）
@st.cache_data
def compute_db_embeddings(_model, _preprocess, paths):
    embeddings = []
    for p in paths:
        try:
            img = Image.open(p).convert("RGB")
            img_tensor = _preprocess(img).unsqueeze(0)
            with torch.no_grad():
                emb = _model.encode_image(img_tensor)
                emb = emb / emb.norm(dim=-1, keepdim=True)
            embeddings.append(emb.cpu().numpy())
        except Exception as e:
            st.warning(f"跳過圖片 {p.name}: {e}")
    return np.vstack(embeddings) if embeddings else np.array([])

db_embeddings = compute_db_embeddings(model, preprocess, db_paths)

if len(db_embeddings) == 0:
    st.error("無法計算任何圖片嘅 embedding")
    st.stop()

# 用戶上傳
uploaded = st.file_uploader("上傳一張圖片搵相似圖", type=["jpg", "jpeg", "png"])

if uploaded:
    query_img = Image.open(uploaded).convert("RGB")
    st.image(query_img, caption="你上傳嘅圖片", width=300)

    query_tensor = preprocess(query_img).unsqueeze(0)
    with torch.no_grad():
        query_emb = model.encode_image(query_tensor)
        query_emb = query_emb / query_emb.norm(dim=-1, keepdim=True)
    query_emb = query_emb.cpu().numpy()

    # 確保維度正確
    if query_emb.shape[1] != db_embeddings.shape[1]:
        st.error(f"維度唔匹配：查詢 {query_emb.shape} vs 資料庫 {db_embeddings.shape}")
        st.stop()

    similarities = (db_embeddings @ query_emb.T).flatten()
    top_k = st.slider("顯示幾多張相似圖", 1, min(12, len(db_paths)), 6)
    top_indices = np.argsort(similarities)[::-1][:top_k]

    st.subheader("最相似嘅圖片")
    cols = st.columns(3)
    for i, idx in enumerate(top_indices):
        with cols[i % 3]:
            st.image(str(db_paths[idx]), caption=f"相似度: {similarities[idx]:.3f}")
