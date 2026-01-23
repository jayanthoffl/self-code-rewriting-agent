import streamlit as st
import requests
import time

# Configuration
API_URL = "http://localhost:8000"  # We talk to our own local Brain

st.set_page_config(page_title="Auto-Dev Agent", page_icon="🧬", layout="wide")

st.title("🧬 Auto-Dev: Self-Healing Infrastructure")
st.markdown("Enter a GitHub repository URL. If it crashes, the AI will fix it live.")

# Input Section
# Change this line:
repo_url = st.text_input("GitHub Repository URL", "https://github.com/jayanthoffl/broken-python-test")

if st.button("🚀 Deploy & Monitor"):
    with st.spinner("Initializing Deployment..."):
        try:
            # 1. Trigger the Deployment via FastAPI
            payload = {"repo_url": repo_url}
            response = requests.post(f"{API_URL}/deploy", json=payload)
            
            if response.status_code == 200:
                st.success(f"Deployment started! Repo: {repo_url}")
                
                # 2. Live Log Viewer
                st.subheader("📡 Live System Logs")
                log_placeholder = st.empty()
                logs = []
                
                # We will simulate a log stream here for the UI demo
                # (In a real production app, we would use WebSockets, 
                # but for this MVP, we will watch the backend logs)
                st.info("Check your Docker Terminal for the real-time AI logs!")
                
            else:
                st.error(f"Failed to deploy: {response.text}")
                
        except Exception as e:
            st.error(f"Connection Error: {e}")
            st.warning("Make sure your Docker Container is running!")

# Instructions
st.divider()
st.subheader("How it works")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### 1. Detect")
    st.write("Monitors container logs for stack traces.")
with col2:
    st.markdown("### 2. Analyze")
    st.write("Sends error context to Google Gemini.")
with col3:
    st.markdown("### 3. Heal")
    st.write("Hot-patches the python files on disk.")