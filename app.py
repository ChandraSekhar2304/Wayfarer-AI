from pathlib import Path
import traceback
import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from backend import run_travel_agent

# This is to allow nested event loops for async calls in FastAPI
import nest_asyncio
nest_asyncio.apply()


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Wayfarer AI",
    description="Autonomous Multi-Agent Travel Planner with LangGraph and MCP",
    version="1.0.0"
)


# Robust path resolution for serverless environments (Vercel Lambda)
static_candidates = [
    BASE_DIR / "static",
    Path("/var/task/static"),
    Path.cwd() / "static",
    BASE_DIR.parent / "static"
]
static_path = next((p for p in static_candidates if p.is_dir()), None)
if not static_path:
    static_path = BASE_DIR / "static"
    static_path.mkdir(parents=True, exist_ok=True)

app.mount(
    "/static",
    StaticFiles(directory=str(static_path)),
    name="static"
)

template_candidates = [
    BASE_DIR / "templates",
    Path("/var/task/templates"),
    Path.cwd() / "templates",
    BASE_DIR.parent / "templates"
]
templates_path = next((p for p in template_candidates if p.is_dir()), BASE_DIR / "templates")

templates = Jinja2Templates(
    directory=str(templates_path)
)



class TravelRequest(BaseModel):
    message: str
    thread_id: str | None = None



@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    try:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={}
        )
    except Exception:
        # Resilient fallback: read index.html directly if Jinja2 has directory resolution issues in Lambda
        for cand in [templates_path / "index.html", BASE_DIR / "templates" / "index.html", Path("/var/task/templates/index.html")]:
            if cand.is_file():
                return HTMLResponse(content=cand.read_text(encoding="utf-8"))
        raise


@app.post("/api/travel")
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
        print("ERROR:", e)
        traceback.print_exc()

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )



@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": "AI Travel Planner API is running"
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