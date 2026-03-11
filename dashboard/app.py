import streamlit as st
import os
import requests

st.set_page_config(page_title="Pokemon Cafe MBA", page_icon="?", layout="wide")

API = os.getenv("MBA_API_URL", "http://localhost:8000")

st.title("? Pokemon Cafe — Market Basket Analysis")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Pipeline Status")
    try:
        r = requests.get(f"{API}/health", timeout=2)
        st.success(f"API Online · v{r.json()['version']}")
    except:
        st.error("API Offline — start uvicorn first")

with col2:
    st.subheader("Upload Transaction CSV")
    uploaded = st.file_uploader("Drop CSV here", type=["csv"])
    if uploaded:
        st.info(f"File ready: {uploaded.name}")

with col3:
    st.subheader("Quick Actions")
    if st.button("Refresh"):
        st.rerun()
    if st.button("View Drift Report"):
        try:
            st.json(requests.get(f"{API}/drift-report").json())
        except:
            st.error("Could not fetch drift report")
