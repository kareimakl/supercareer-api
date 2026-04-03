import streamlit as st
import sqlite3
import faiss
import os
from vector_engine import model, create_hnsw_index
from match import match

# إعدادات الصفحة
st.set_page_config(page_title="AI Matching Hub", page_icon="🎯", layout="wide")

# دالة لجلب البيانات
def get_data(table_name):
    conn = sqlite3.connect('matching.db')
    cursor = conn.cursor()
    if table_name == "users":
        cursor.execute('SELECT name, bio FROM users')
    else:
        cursor.execute('SELECT job_title, job_description FROM jobs')
    data = cursor.fetchall()
    conn.close()
    return data

# واجهة المستخدم
st.title("🎯 AI Smart Matching System")
st.markdown("---")

# القائمة الجانبية للاختيار
mode = st.sidebar.radio("ماذا تريد أن تفعل؟", ["البحث عن مستقلين (لأصحاب العمل)", "البحث عن وظائف (للمستقلين)"])

if mode == "البحث عن مستقلين (لأصحاب العمل)":
    st.header("🔎 ابحث عن أفضل شخص لمشروعك")
    query = st.text_input("صف الوظيفة المطلوبة (مثال: محتاج مبرمج بايثون لمشروع ذكاء اصطناعي)")
    data = get_data("users")
    btn_text = "بحث عن مرشحين"
else:
    st.header("💼 ابحث عن الوظيفة الأنسب لمهاراتك")
    query = st.text_area("أدخل مهاراتك أو نبذة عن خبراتك")
    data = get_data("jobs")
    btn_text = "بحث عن وظائف"

if st.button(btn_text) and query:
    with st.spinner('جاري التحليل الذكي للبيانات...'):
        # تحويل البيانات لـ Vectors
        contents = [item[1] for item in data]
        embeddings = model.encode(contents).astype('float32')
        index = create_hnsw_index(embeddings)
        
        # تحويل الطلب لـ Vector والبحث
        query_vec = model.encode([query]).astype('float32')
        distances, indices = index.search(query_vec, k=3)
        
        st.success("تم العثور على أفضل النتائج!")
        
        # عرض النتائج في شكل بطاقات (Cards)
        cols = st.columns(3)
        for i, idx in enumerate(indices[0]):
            if idx != -1:
                with cols[i]:
                    st.info(f"🏆 المركز {i+1}")
                    name_title = data[idx][0]
                    description = data[idx][1]
                    match_score = max(0, 100 - distances[0][i])
                    
                    st.subheader(name_title)
                    st.write(f"**نسبة التطابق:** {match_score:.1f}%")
                    st.write(f"**التفاصيل:** {description[:200]}...")
                    st.progress(int(match_score))