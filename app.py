import streamlit as st
import torch
import open_clip
from PIL import Image
import numpy as np
from pathlib import Path

st.set_page_config(page_title="相似圖片搜尋", layout="wide")
st.title("🖼️ 相似圖片搜尋（切格版）")

# 載入模型
@st.cache_resource
def load_model():
    model, _, preprocess = open_clip.create_model_and_transforms(
        'ViT-B-32', pretrained='openai'
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

# 將圖片切成網格並計算每格 embedding
def image_to_grid_embeddings(img, grid_size=4):
    """將圖片切成 grid_size x grid_size 格，返回每格 embedding"""
    w, h = img.size
    cell_w, cell_h = w // grid_size, h // grid_size
    embeddings = []
    
    for i in range(grid_size):
        for j in range(grid_size):
            left = j * cell_w
            top = i * cell_h
            right = left + cell_w
            bottom = top + cell_h
            cell = img.crop((left, top, right, bottom))
            
            cell_tensor = preprocess(cell).unsqueeze(0)
            with torch.no_grad():
                emb = model.encode_image(cell_tensor)
                emb = emb / emb.norm(dim=-1, keepdim=True)
            embeddings.append(emb.cpu().numpy())
    
    return np.vstack(embeddings)

# 計算資料庫所有圖片嘅網格 embedding
@st.cache_data
def compute_db_grid_embeddings(_model, _preprocess, paths, grid_size=4):
    all_embeddings = []
    for p in paths:
        try:
            img = Image.open(p).convert("RGB")
            grid_emb = image_to_grid_embeddings(img, grid_size)
            all_embeddings.append(grid_emb)
        except Exception as e:
            st.warning(f"跳過 {p.name}: {e}")
    return all_embeddings

grid_size = st.sidebar.slider("網格大小", 2, 6, 4, help="越大越準確但越慢")
db_grid_embeddings = compute_db_grid_embeddings(model, preprocess, db_paths, grid_size)

# 用戶上傳
uploaded = st.file_uploader("上傳一張圖片搵相似圖", type=["jpg", "jpeg", "png"])

if uploaded:
    query_img = Image.open(uploaded).convert("RGB")
    st.image(query_img, caption="你上傳嘅圖片", width=300)
    
    query_grid_emb = image_to_grid_embeddings(query_img, grid_size)
    
    # 計算每張資料庫圖片嘅相似度（所有格子平均）
    similarities = []
    for db_emb in db_grid_embeddings:
        # 每格計算相似度，再取平均
        cell_sims = np.sum(query_grid_emb * db_emb, axis=1)
        avg_sim = np.mean(cell_sims)
        similarities.append(avg_sim)
    
    similarities = np.array(similarities)
    top_k = st.slider("顯示幾多張相似圖", 1, min(12, len(db_paths)), 6)
    top_indices = np.argsort(similarities)[::-1][:top_k]
    
    st.subheader(f"最相似嘅圖片（{grid_size}x{grid_size} 切格）")
    cols = st.columns(3)
    for i, idx in enumerate(top_indices):
        with cols[i % 3]:
            st.image(str(db_paths[idx]), caption=f"相似度: {similarities[idx]:.3f}")
