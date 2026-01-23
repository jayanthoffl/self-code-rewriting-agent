import os
import shutil
import logging
import threading
import time
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import docker
from git import Repo

# Import the AI Agent logic
# (Ensure agent.py and tools.py exist in the same folder)
from agent import fix_code

# --- Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AutoDev")

app = FastAPI(title="Auto-Dev Brain")

# Config
WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "/app/temp_repos")

# Initialize Docker Client
try:
    docker_client = docker.from_env()
    logger.info("✅ Docker Client connected.")
except Exception as e:
    logger.error(f"❌ Docker Error: {e}")

# --- Data Models ---
class Request(BaseModel):
    repo_url: str

# --- Core Logic ---

def monitor_container(container, repo_path):
    """
    Background thread that watches logs for 'Traceback'.
    """
    logger.info(f"👀 Monitoring {container.name} for crashes...")
    
    try:
        # Stream logs line by line
        for line in container.logs(stream=True, follow=True):
            log_line = line.decode('utf-8').strip()
            print(f"[{container.name}] {log_line}") # Print to console
            
            # KEYWORD DETECTION
            if "Traceback" in log_line or "Exception" in log_line:
                logger.error("🚨 CRASH DETECTED! Triggering AI Agent...")
                
                # Capture the full recent logs (context)
                full_logs = container.logs(tail=20).decode('utf-8')
                
                # 1. Trigger the Agent
                fix_code(repo_path, full_logs)
                
                # 2. Rebuild & Restart (Self-Healing)
                logger.info("🩹 Fix applied by Agent. Stopping monitor.")
                break
    except Exception as e:
        logger.error(f"Monitor stopped: {e}")

def run_setup(repo_url: str):
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    local_path = os.path.join(WORKSPACE_DIR, repo_name)
    
    # 1. Clean & Clone
    if os.path.exists(local_path):
        shutil.rmtree(local_path)
    
    logger.info(f"⬇️ Cloning {repo_url}...")
    try:
        Repo.clone_from(repo_url, local_path)
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

    # 5. DETECT ENTRY POINT (Crucial Fix)
    entry_file = "main.py" # Default
    if not os.path.exists(os.path.join(local_path, "main.py")):
        # Simple search for main.py if not in root
        for root, dirs, files in os.walk(local_path):
            if "main.py" in files:
                rel_path = os.path.relpath(os.path.join(root, "main.py"), local_path)
                entry_file = rel_path.replace("\\", "/")
                break
    
    logger.info(f"🎯 Detected Entry Point: {entry_file}")

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

        # 7. Start Monitoring (THE MISSING LINK)
        monitor_thread = threading.Thread(
            target=monitor_container, 
            args=(container, local_path)
        )
        monitor_thread.start()
        
    except Exception as e:
        logger.error(f"❌ Run Failed: {e}")

# --- Endpoints ---
@app.post("/deploy")
async def deploy(req: Request, tasks: BackgroundTasks):
    tasks.add_task(run_setup, req.repo_url)
    return {"status": "Deploying", "repo": req.repo_url}

@app.get("/")
async def root():
    return {"message": "Auto-Dev Brain is running!"}

# --- Test Endpoint (for quick checks) ---
@app.get("/test")
async def test_crash():
    print("App Started...")
    time.sleep(1)
    print("Working...")
    time.sleep(1)
    # Removed: raise Exception("Oops! The code crashed!")
