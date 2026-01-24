import os
import shutil
import logging
import threading
import time
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import docker
from git import Repo

# Import the Agent
from agent import fix_code

# --- Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AutoDev")

app = FastAPI(title="Auto-Dev Brain")

# Config
WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "/app/temp_repos")
# We still keep this as a "Admin Fallback" for your own use
ADMIN_GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") 

# Initialize Docker
try:
    docker_client = docker.from_env()
    logger.info("✅ Docker Client connected.")
except Exception as e:
    logger.error(f"❌ Docker Error: {e}")

# --- NEW DATA MODEL ---
class Request(BaseModel):
    repo_url: str
    github_token: str | None = None # <--- The Guest Key

# --- Helper: Push to GitHub ---
def push_changes(repo_path, token):
    """
    Commits and pushes using the SPECIFIC USER'S token.
    """
    if not token:
        logger.warning("⚠️ No GitHub Token provided for this session. Skipping push.")
        return

    try:
        logger.info("📤 Attempting to push fix to GitHub...")
        repo = Repo(repo_path)
        
        # Configure Git Identity (The Bot)
        repo.config_writer().set_value("user", "name", "AutoDev Bot").release()
        repo.config_writer().set_value("user", "email", "bot@autodev.ai").release()
        
        # 1. Add
        repo.git.add(all=True)
        
        # 2. Check
        if not repo.is_dirty():
            logger.warning("⚠️ No file changes detected.")
            return

        # 3. Commit
        repo.index.commit("🩹 Auto-fix: AI Agent repaired the crash")
        
        # 4. Push (Injecting the User's specific token)
        origin = repo.remote(name='origin')
        current_url = origin.url
        
        # Clean potential existing auth to avoid conflicts
        clean_url = current_url.split("@")[-1] if "@" in current_url else current_url
        if "https://" in clean_url:
            clean_url = clean_url.replace("https://", "")
            
        # Construct Authenticated URL: https://USER_TOKEN@github.com/user/repo
        auth_url = f"https://{token}@{clean_url}"
        origin.set_url(auth_url)
            
        origin.push()
        logger.info("🚀 SUCCESS: Fix pushed to GitHub!")
        
    except Exception as e:
        logger.error(f"❌ Git Push Failed: {e}")

# --- Core Logic ---

def monitor_container(container, repo_path, token):
    logger.info(f"👀 Monitoring {container.name} for crashes...")
    try:
        for line in container.logs(stream=True, follow=True):
            log_line = line.decode('utf-8').strip()
            print(f"[{container.name}] {log_line}")
            
            if "Traceback" in log_line or "Exception" in log_line:
                logger.error("🚨 CRASH DETECTED! Triggering AI Agent...")
                
                # 1. Capture Logs
                full_logs = container.logs(tail=20).decode('utf-8')
                
                # 2. Fix Code
                fix_code(repo_path, full_logs)
                
                # 3. Push to GitHub (Using the User's Token)
                push_changes(repo_path, token)
                
                logger.info("🩹 Fix applied. Stopping monitor.")
                break
    except Exception as e:
        logger.error(f"Monitor stopped: {e}")

def run_setup(repo_url: str, request_token: str = None):
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    local_path = os.path.join(WORKSPACE_DIR, repo_name)
    
    # --- PRIORITY AUTH SYSTEM ---
    # 1. User provided a token in the UI? Use that.
    # 2. No? Fallback to the Admin token in .env (for you).
    # 3. No? Use None (Public Read-Only).
    active_token = request_token if request_token else ADMIN_GITHUB_TOKEN
    
    # 1. Clean & Clone
    if os.path.exists(local_path):
        shutil.rmtree(local_path)
    
    logger.info(f"⬇️ Cloning {repo_url}...")
    
    # Construct Clone URL
    auth_url = repo_url
    if active_token and "github.com" in repo_url:
        clean_url = repo_url.replace("https://", "")
        auth_url = f"https://{active_token}@{clean_url}"

    try:
        Repo.clone_from(auth_url, local_path)
        logger.info(f"✅ Cloned to {local_path}")
    except Exception as e:
        logger.error(f"❌ Clone failed: {e}")
        return

    # 2. Inject Dockerfile
    template_path = os.path.join(os.getcwd(), "templates", "Dockerfile.python")
    target_dockerfile = os.path.join(local_path, "Dockerfile")
    if not os.path.exists(target_dockerfile):
        shutil.copy(template_path, target_dockerfile)

    # 3. Build Image
    image_tag = f"autodev-{repo_name.lower()}"
    logger.info(f"🔨 Building {image_tag}...")
    try:
        docker_client.images.build(path=local_path, tag=image_tag, rm=True)
    except Exception as e:
        logger.error(f"❌ Build Failed: {e}")
        return

    # 4. Cleanup old container
    container_name = f"run-{repo_name.lower()}"
    try:
        old = docker_client.containers.get(container_name)
        old.stop()
        old.remove()
    except:
        pass

    # 5. Detect Entry Point
    entry_file = "main.py"
    if not os.path.exists(os.path.join(local_path, "main.py")):
        for root, dirs, files in os.walk(local_path):
            if "main.py" in files:
                rel_path = os.path.relpath(os.path.join(root, "main.py"), local_path)
                entry_file = rel_path.replace("\\", "/")
                break
    
    # 6. Run & Monitor
    logger.info(f"🚀 Launching Container: {container_name}")
    try:
        container = docker_client.containers.run(
            image_tag,
            name=container_name,
            detach=True,
            command=f"python {entry_file}" 
        )
        logger.info(f"✅ Container {container_name} is running!")

        monitor_thread = threading.Thread(
            target=monitor_container, 
            args=(container, local_path, active_token) # Pass the token down!
        )
        monitor_thread.start()
        
    except Exception as e:
        logger.error(f"❌ Run Failed: {e}")

@app.post("/deploy")
async def deploy(req: Request, tasks: BackgroundTasks):
    # Pass the user's specific token to the background task
    tasks.add_task(run_setup, req.repo_url, req.github_token)
    return {"status": "Deploying", "repo": req.repo_url}

@app.get("/")
async def root():
    return {"message": "Auto-Dev Brain is running!"}