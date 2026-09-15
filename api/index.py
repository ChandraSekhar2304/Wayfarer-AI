import os
import sys
import traceback
from pathlib import Path

# Ensure all possible root directories are in sys.path for serverless execution
CURRENT_DIR = Path(__file__).resolve().parent
PARENT_DIR = CURRENT_DIR.parent

for path_candidate in [
    str(CURRENT_DIR),
    str(PARENT_DIR),
    "/var/task",
    "/var/task/api",
    os.getcwd()
]:
    if path_candidate and path_candidate not in sys.path:
        sys.path.insert(0, path_candidate)

try:
    from app import app
except Exception as e:
    err_tb = traceback.format_exc()
    print("FATAL ERROR IMPORTING APP IN api/index.py:", err_tb)

    from fastapi import FastAPI, Request
    from fastapi.responses import HTMLResponse, JSONResponse

    app = FastAPI(title="Wayfarer AI (Diagnostic Fallback)")

    @app.get("/{full_path:path}")
    async def diagnostic_get(request: Request, full_path: str = ""):
        task_files = []
        try:
            task_files = os.listdir("/var/task")
        except Exception as dir_err:
            task_files = [str(dir_err)]

        return HTMLResponse(
            content=f"""
            <html>
            <head><title>Startup Diagnostic</title></head>
            <body style="font-family: monospace; padding: 20px; background: #0f172a; color: #f87171;">
                <h2>Startup Error in api/index.py</h2>
                <pre>{err_tb}</pre>
                <hr style="border-color: #334155;"/>
                <h3 style="color: #94a3b8;">Environment Diagnostics:</h3>
                <p><strong>CWD:</strong> {os.getcwd()}</p>
                <p><strong>sys.path:</strong> {sys.path}</p>
                <p><strong>/var/task contents:</strong> {task_files}</p>
            </body>
            </html>
            """,
            status_code=500
        )

    @app.post("/{full_path:path}")
    async def diagnostic_post(request: Request, full_path: str = ""):
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Serverless startup failed",
                "details": str(e)
            }
        )
