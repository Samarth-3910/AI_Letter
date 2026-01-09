import subprocess
import time
import os
import sys

def run_servers():
    ROOT_DIR = os.getcwd()
    PYTHON_EXEC = os.path.join(ROOT_DIR, "venv", "Scripts", "python.exe")
    
    # Paths
    BACKEND_MODULE = "Generative_AI_Core.Entry_Points.api:app"
    FRONTEND_DIR = os.path.join(ROOT_DIR, "User_Interface")

    print("--- Enterprise RAG Engine Launcher ---")
    
    # 1. Start Backend
    print("[1/2] Starting Generative AI Core (FastAPI)...")
    backend_env = os.environ.copy()
    backend_env["PYTHONPATH"] = ROOT_DIR # Vital so it can find 'Generative_AI_Core' package
    
    backend_process = subprocess.Popen(
        [PYTHON_EXEC, "-m", "uvicorn", BACKEND_MODULE, "--host", "127.0.0.1", "--port", "8000", "--reload"],
        cwd=ROOT_DIR, # Run from root so imports work
        env=backend_env,
        shell=True
    )

    # 2. Start Frontend
    print("[2/2] Starting User Interface (Next.js)...")
    frontend_process = subprocess.Popen(
        ["npm.cmd", "run", "dev"],
        cwd=FRONTEND_DIR,
        shell=True
    )

    print("\n>>> ENGINE ONLINE <<<")
    print("API: http://127.0.0.1:8000/docs")
    print("UI:  http://localhost:3000")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Stopping] Terminating services...")
        subprocess.call(['taskkill', '/F', '/T', '/PID', str(backend_process.pid)])
        subprocess.call(['taskkill', '/F', '/T', '/PID', str(frontend_process.pid)])

if __name__ == "__main__":
    run_servers()
