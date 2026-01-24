import streamlit as st
import requests
import json
import time

# --- Configuration ---
API_URL = "http://localhost:8000"

st.set_page_config(page_title="AutoDev Agent", page_icon="🤖", layout="wide")

# --- Sidebar: Authentication ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/robot-2.png", width=80)
    st.title("AutoDev Agent")
    st.markdown("---")
    
    st.header("🔑 Authentication")
    st.info("Required for Private Repos & Auto-Pushing fixes.")
    
    # The "Password Field" for the Token
    user_token = st.text_input("GitHub PAT (Token)", type="password", help="Generate a token with 'repo' scope in GitHub Developer Settings.")
    
    if not user_token:
        st.warning("Running in Read-Only Mode (Public Repos).")
    else:
        st.success("Authenticated & Ready to Push! 🚀")

# --- Main Layout ---
st.title("🤖 Autonomous Code Healer")
st.markdown("Give me a broken GitHub repo. I will deploy it, watch it crash, fix the code, and push the solution.")

# Input Section
col1, col2 = st.columns([3, 1])
with col1:
    repo_url = st.text_input("GitHub Repository URL", placeholder="https://github.com/username/broken-repo")
with col2:
    st.write("") # Spacer
    st.write("") 
    deploy_btn = st.button("🚀 Deploy & Heal", type="primary", use_container_width=True)

# Status & Logs
status_container = st.empty()
log_container = st.empty()

if deploy_btn and repo_url:
    try:
        with st.spinner("Initializing Agent..."):
            # Prepare Payload with the Token
            payload = {
                "repo_url": repo_url,
                "github_token": user_token if user_token else None
            }
            
            # Send to Backend
            response = requests.post(f"{API_URL}/deploy", json=payload)
            
            if response.status_code == 200:
                st.success(f"✅ Agent Deployed on: {repo_url}")
                st.toast("Monitoring for crashes...", icon="👀")
            else:
                st.error(f"Deployment Failed: {response.text}")
                
    except Exception as e:
        st.error(f"Connection Error: {e}")

# --- Log Viewer (Simple Polling) ---
st.markdown("### 📡 Live Agent Logs")
logs_placeholder = st.code("Waiting for deployment...", language="bash")

# NOTE: In a real app, use WebSockets. Here we just show a static message 
# because Streamlit can't easily tail Docker logs from the frontend directly 
# without complex threading. Use the VS Code terminal to see the real action!