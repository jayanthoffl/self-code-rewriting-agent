import os
import shutil
import logging
import threading
import time
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import docker
from git import Repo
from agent import fix_code

# --- Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AutoDev")

app = FastAPI(title="Auto-Dev Brain")

# --- UNLOCK THE GATES (CORS) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GLOBAL STATE ---
SYSTEM_STATE = {
    "status": "IDLE",       # IDLE, DEPLOYING, RUNNING, CRASHED, FIXING, SUCCESS, STOPPED
    "logs": [],             # Live log buffer
    "repo_path": ""
}
ACTIVE_CONTAINER_NAME = None

# --- CONFIG ---
WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "/app/temp_repos")
ADMIN_GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") 

# --- DOCKER INIT ---
try:
    docker_client = docker.from_env()
    logger.info("✅ Docker Client connected.")
except Exception as e:
    logger.error(f"❌ Docker Error: {e}")

class Request(BaseModel):
    repo_url: str
    github_token: str | None = None 

# --- HELPER FUNCTIONS ---
def add_log(message):
    """Saves logs to memory so React can see them."""
    timestamp = time.strftime("%H:%M:%S")
    entry = f"[{timestamp}] {message}"
    print(entry)
    SYSTEM_STATE["logs"].append(entry)
    if len(SYSTEM_STATE["logs"]) > 100:
        SYSTEM_STATE["logs"].pop(0)

def push_changes(repo_path, token):
    if not token:
        add_log("⚠️ No Token. Skipping Push.")
        return
    try:
        add_log("📤 Pushing fix to GitHub...")
        repo = Repo(repo_path)
        repo.config_writer().set_value("user", "name", "AutoDev Bot").release()
        repo.config_writer().set_value("user", "email", "bot@autodev.ai").release()
        repo.git.add(all=True)
        if not repo.is_dirty():
            return
        repo.index.commit("🩹 Auto-fix: AI Agent repaired the crash")
        origin = repo.remote(name='origin')
        clean_url = origin.url.split("@")[-1].replace("https://", "")
        origin.set_url(f"https://{token}@{clean_url}")
        origin.push()
        add_log("🚀 SUCCESS: Fix pushed to GitHub!")
        SYSTEM_STATE["status"] = "SUCCESS"
    except Exception as e:
        add_log(f"❌ Git Push Failed: {e}")

# --- CORE LOGIC ---
def monitor_container(container, repo_path, token):
    add_log(f"👀 Monitoring {container.name}...")
    SYSTEM_STATE["status"] = "RUNNING"
    try:
        for line in container.logs(stream=True, follow=True):
            log_line = line.decode('utf-8').strip()
            add_log(f"[App] {log_line}")
            
            if "Traceback" in log_line or "Exception" in log_line:
                add_log("🚨 CRASH DETECTED! Awakening AI...")
                SYSTEM_STATE["status"] = "CRASHED"
                
                full_logs = container.logs(tail=20).decode('utf-8')
                SYSTEM_STATE["status"] = "FIXING"
                add_log("🧠 AI is diagnosing...")
                
                fix_code(repo_path, full_logs)
                push_changes(repo_path, token)
                
                add_log("🩹 Patch applied.")
                break
    except Exception as e:
        add_log(f"Monitor stopped: {e}")

def run_setup(repo_url: str, request_token: str = None):
    SYSTEM_STATE["logs"] = [] # Clear logs
    SYSTEM_STATE["status"] = "DEPLOYING"
    
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    local_path = os.path.join(WORKSPACE_DIR, repo_name)
    
    active_token = request_token if request_token else ADMIN_GITHUB_TOKEN
    
    if os.path.exists(local_path):
        shutil.rmtree(local_path)
    
    add_log(f"⬇️ Cloning {repo_url}...")
    auth_url = repo_url
    if active_token and "github.com" in repo_url:
        clean_url = repo_url.replace("https://", "")
        auth_url = f"https://{active_token}@{clean_url}"

    try:
        Repo.clone_from(auth_url, local_path)
    except Exception as e:
        add_log(f"❌ Clone failed: {e}")
        return

    template_path = os.path.join(os.getcwd(), "templates", "Dockerfile.python")
    shutil.copy(template_path, os.path.join(local_path, "Dockerfile"))

    image_tag = f"autodev-{repo_name.lower()}"
    add_log(f"🔨 Building Environment...")
    try:
        docker_client.images.build(path=local_path, tag=image_tag, rm=True)
        
        # --- NEW: TRACK CONTAINER NAME ---
        container_name = f"run-{repo_name.lower()}"
        global ACTIVE_CONTAINER_NAME
        ACTIVE_CONTAINER_NAME = container_name
        # ---------------------------------

        try:
            old = docker_client.containers.get(container_name)
            old.stop()
            old.remove()
        except: pass
        
        add_log("🚀 Launching...")
        container = docker_client.containers.run(
            image_tag, name=container_name, detach=True, command="python main.py"
        )
        
        monitor_thread = threading.Thread(
            target=monitor_container, 
            args=(container, local_path, active_token)
        )
        monitor_thread.start()
        
    except Exception as e:
        add_log(f"❌ Error: {e}")

# --- API ENDPOINTS ---
@app.post("/deploy")
async def deploy(req: Request, tasks: BackgroundTasks):
    tasks.add_task(run_setup, req.repo_url, req.github_token)
    return {"status": "Started"}

@app.get("/status")
async def get_status():
    return SYSTEM_STATE

@app.post("/stop")
async def stop_process():
    """Kills the active container and stops the agent."""
    global ACTIVE_CONTAINER_NAME
    add_log("🛑 Manual Stop Signal Received.")
    
    if ACTIVE_CONTAINER_NAME:
        try:
            container = docker_client.containers.get(ACTIVE_CONTAINER_NAME)
            container.stop(timeout=1)
            container.remove()
            add_log(f"✅ Container {ACTIVE_CONTAINER_NAME} destroyed.")
        except Exception as e:
            add_log(f"⚠️ Could not stop container: {e}")
            
    SYSTEM_STATE["status"] = "STOPPED"
    return {"message": "Process Stopped"}