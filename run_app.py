import subprocess
import time
import os

def run_servers():
    # Define paths
    ROOT_DIR = os.getcwd()
    BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
    FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
    
    # Check if venv exists in backend/venv or root/venv
    if os.path.exists(os.path.join(BACKEND_DIR, "venv")):
        PYTHON_EXEC = os.path.join(BACKEND_DIR, "venv", "Scripts", "python.exe")
    elif os.path.exists(os.path.join(ROOT_DIR, "venv")):
        PYTHON_EXEC = os.path.join(ROOT_DIR, "venv", "Scripts", "python.exe")
    else:
        print("Error: Could not find 'venv'. Please ensure virtual environment is set up.")
        return

    print("--- GhostWriter AI Launcher ---")
    print(f"[1/3] Found Python: {PYTHON_EXEC}")

    # Start Backend
    print("[2/3] Starting Backend (FastAPI)...")
    backend_process = subprocess.Popen(
        [PYTHON_EXEC, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
        cwd=BACKEND_DIR,
        shell=True
    )

    # Start Frontend
    print("[3/3] Starting Frontend (Next.js)...")
    # Using 'npm.cmd' for Windows compatibility
    frontend_process = subprocess.Popen(
        ["npm.cmd", "run", "dev"],
        cwd=FRONTEND_DIR,
        shell=True
    )

    print("\n>>> ALL SYSTEMS ARE GO! <<<")
    print("Backend: http://127.0.0.1:8000")
    print("Frontend: http://localhost:3000")
    print("--------------------------------")
    print("Press CTRL+C to stop both servers.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Stopping] Terminating servers...")
        # Windows requires forceful termination for shell=True processes
        subprocess.call(['taskkill', '/F', '/T', '/PID', str(backend_process.pid)])
        subprocess.call(['taskkill', '/F', '/T', '/PID', str(frontend_process.pid)])
        print("[Stopped] Goodbye!")

if __name__ == "__main__":
    run_servers()
