from pathlib import Path
import os
import sys
import traceback
import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Allow nested event loops for async calls in FastAPI
import nest_asyncio
nest_asyncio.apply()

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Wayfarer AI",
    description="Autonomous Multi-Agent Travel Planner with LangGraph and MCP",
    version="1.0.0"
)

# Robust static files mounting (Never call mkdir in serverless environments!)
static_candidates = [
    BASE_DIR / "public" / "static",
    BASE_DIR / "static",
    BASE_DIR.parent / "public" / "static",
    BASE_DIR.parent / "static",
    Path("/var/task/public/static"),
    Path("/var/task/static"),
    Path.cwd() / "public" / "static",
    Path.cwd() / "static"
]
static_path = next((p for p in static_candidates if p.is_dir()), None)
if static_path:
    app.mount(
        "/static",
        StaticFiles(directory=str(static_path)),
        name="static"
    )

template_candidates = [
    BASE_DIR / "templates",
    BASE_DIR / "api" / "templates",
    BASE_DIR.parent / "templates",
    Path("/var/task/templates"),
    Path("/var/task/api/templates"),
    Path.cwd() / "templates"
]
templates_path = next((p for p in template_candidates if p.is_dir()), None)
templates = Jinja2Templates(directory=str(templates_path)) if templates_path else None


EMBEDDED_INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wayfarer AI — Autonomous Multi-Agent Travel Planner</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <div class="page-bg">
        <div class="gradient-circle circle-1"></div>
        <div class="gradient-circle circle-2"></div>
        <div class="gradient-circle circle-3"></div>
    </div>
    <main class="app-container">
        <section class="hero-section">
            <div class="badge">
                ✈️ Wayfarer AI — Autonomous Multi-Agent Travel Architect with LangGraph & MCP
            </div>
            <h1>Plan Your Perfect Trip with AI</h1>
            <p>
                Search flights, discover hotels, and generate a complete travel itinerary using a multi-agent LangGraph system.
            </p>
        </section>
        <section class="planner-card">
            <div class="card-header">
                <div>
                    <h2>Where do you want to go?</h2>
                    <p>Example: Plan a complete 7 days Japan trip from Bangladesh under 2 lakhs.</p>
                </div>
                <div class="status-pill">
                    <span class="status-dot"></span>
                    Online
                </div>
            </div>
            <div class="input-area">
                <textarea
                    id="userInput"
                    placeholder="Plan a complete 7 days Japan trip including flights, hotels and sightseeing under 2 lakhs..."
                ></textarea>
                <button id="sendBtn" onclick="sendMessage()">
                    <span id="btnText">Generate Plan</span>
                    <span id="btnLoader" class="loader hidden"></span>
                </button>
            </div>
            <div class="quick-prompts">
                <button onclick="setPrompt('Plan a complete 7 days Japan trip from Bangladesh including flights, hotels and sightseeing under 2 lakhs.')">
                    Japan Trip
                </button>
                <button onclick="setPrompt('Plan a 5 days Dubai trip from Dhaka with flights, hotels and sightseeing.')">
                    Dubai Trip
                </button>
                <button onclick="setPrompt('Plan a 7 days Thailand trip from Bangladesh with budget hotels and sightseeing.')">
                    Thailand Trip
                </button>
                <button onclick="setPrompt('Give me all country flight info.')">
                    Global Flights
                </button>
            </div>
            <div id="progressBox" class="progress-box hidden">
                <div class="progress-header">
                    <div class="agent-pulse"></div>
                    <span id="progressStepTitle" class="progress-step-title">Initializing travel agents...</span>
                </div>
                <div class="progress-bar-track">
                    <div id="progressBarFill" class="progress-bar-fill"></div>
                </div>
                <p id="progressStepDesc" class="progress-step-desc">Coordinating LangGraph multi-agent workflow...</p>
            </div>
        </section>
        <section id="resultSection" class="result-section hidden">
            <div class="result-header">
                <div>
                    <h2>Your AI Travel Plan</h2>
                    <p id="threadInfo">Thread ID: -</p>
                </div>
                <div class="result-actions">
                    <button class="copy-btn" onclick="copyResult()">Copy</button>
                    <button class="download-btn" onclick="downloadPDF()">Download PDF</button>
                </div>
            </div>
            <div id="pdfContent" class="pdf-content">
                <h1 class="pdf-title">AI Travel Plan</h1>
                <div id="resultBox" class="result-box"></div>
            </div>
        </section>
        <section id="errorBox" class="error-box hidden"></section>
    </main>
    <footer>
        Built with FastAPI, LangGraph, Groq, PostgreSQL, Tavily, AviationStack & OpenWeather • Wayfarer AI
    </footer>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    <script src="/static/script.js"></script>
</body>
</html>"""


class TravelRequest(BaseModel):
    message: str
    thread_id: str | None = None


@app.get("/", response_class=HTMLResponse)
@app.get("/api/index.py", response_class=HTMLResponse)
@app.get("/api", response_class=HTMLResponse)
async def home(request: Request):
    if templates:
        try:
            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context={}
            )
        except Exception:
            pass

    # Resilient fallback: search known paths or serve embedded HTML
    for cand in [
        templates_path / "index.html" if templates_path else None,
        BASE_DIR / "templates" / "index.html",
        BASE_DIR.parent / "templates" / "index.html",
        Path("/var/task/templates/index.html"),
        Path.cwd() / "templates" / "index.html"
    ]:
        if cand and cand.is_file():
            return HTMLResponse(content=cand.read_text(encoding="utf-8"))

    return HTMLResponse(content=EMBEDDED_INDEX_HTML)


@app.post("/api/travel")
@app.post("/api/index.py")
@app.post("/")
async def travel_planner(request_data: TravelRequest):
    try:
        user_message = request_data.message.strip()

        if not user_message:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Message cannot be empty."
                }
            )

        from backend import run_travel_agent

        result = run_travel_agent(
            user_input=user_message,
            thread_id=request_data.thread_id
        )

        return JSONResponse(
            content={
                "success": True,
                "thread_id": result["thread_id"],
                "answer": result["answer"],
                "flight_results": result["flight_results"],
                "hotel_results": result["hotel_results"],
                "itinerary": result["itinerary"],
                "llm_calls": result["llm_calls"],
            }
        )

    except Exception as e:
        print("ERROR IN travel_planner:", e)
        traceback.print_exc()

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


@app.get("/health")
@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "message": "Wayfarer AI Travel Planner API is running"
    }


@app.get("/favicon.ico")
async def favicon():
    return JSONResponse(content={})


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )