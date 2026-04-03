import faiss
import numpy as np
import os
from sentence_transformers import SentenceTransformer

# المسار المحلي
MODEL_PATH = "./my_local_model"

def get_model():
    if os.path.exists(MODEL_PATH) and os.listdir(MODEL_PATH):
        print("🚀 تم تحميل الموديل من المجلد المحلي بنجاح!")
        return SentenceTransformer(MODEL_PATH)
    else:
        print("🌐 جاري تحميل الموديل من الإنترنت (لآخر مرة)...")
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        # السطر ده هو اللي هيحفظ الموديل عندك للأبد
        model.save(MODEL_PATH)
        print(f"✅ تم حفظ الموديل في {MODEL_PATH}")
        return model

model = get_model()

def create_hnsw_index(embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexHNSWFlat(dimension, 32)
    index.add(embeddings.astype('float32'))
    return index
