# ✈️ Wayfarer AI — Autonomous Multi-Agent Travel Planner with LangGraph & MCP

[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange.svg?logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Model Context Protocol](https://img.shields.io/badge/MCP-Standard-blue.svg)](https://modelcontextprotocol.io)
[![Groq](https://img.shields.io/badge/Groq-Ultra--Fast_LLM-f55036.svg)](https://groq.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Checkpointer-336791.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An open-source, production-ready AI travel planner that converts any natural-language travel request into an executive travel plan with live flight routes, hotel suggestions, real-time weather forecasts, and structured day-by-day itineraries. 

Built with **LangGraph**, **FastAPI**, **Groq LLMs**, **PostgreSQL state persistence**, and the **Model Context Protocol (MCP)**.

---

## 🌟 Why Wayfarer AI?

Planning an international or domestic vacation traditionally forces travelers to juggle dozens of browser tabs across Skyscanner, Booking.com, Weather apps, Reddit, and spreadsheets. 

**Wayfarer AI** automates this end-to-end using a coordinated team of autonomous agents:
1. **✈️ Flight Agent**: Analyzes origin/destination airports, airlines, route durations, and booking advice.
2. **🏨 Hotel Agent**: Researches top-rated hotels, neighborhood recommendations, and pricing using remote **Tavily MCP**.
3. **🌤 Weather Agent**: Inspects live conditions and 5-day forecasts via a **custom Weather FastMCP server**.
4. **📝 Itinerary Agent**: Crafts practical, day-by-day itineraries tailored to budget and pacing.
5. **✨ Final Synthesis Agent**: Assembles an executive report with structured tables, itemized budget, and packing advice.

---

## 🧠 System Architecture

```mermaid
graph TD
    User([👤 User Travel Request]) --> Frontend[🌐 Web Interface / API]
    Frontend --> FastAPI[⚡ FastAPI Backend]
    FastAPI --> LG[🧠 LangGraph Orchestrator]

    subgraph Autonomous Agents & MCP Tooling
        LG --> FlightAgent[✈️ Flight Agent]
        LG --> HotelAgent[🏨 Hotel Agent]
        LG --> WeatherAgent[🌤 Weather Agent]
        
        FlightAgent -.-> AviationMCP[AviationStack MCP]
        HotelAgent -.-> TavilyMCP[Remote Tavily HTTP MCP]
        WeatherAgent -.-> WeatherMCP[Local Weather FastMCP Server]
        
        FlightAgent --> ItineraryAgent[📝 Itinerary Agent]
        HotelAgent --> ItineraryAgent
        WeatherAgent --> ItineraryAgent
        
        ItineraryAgent --> FinalAgent[✨ Final Synthesis Agent]
    end

    FinalAgent --> DB[(💾 PostgreSQL Checkpointer)]
    FinalAgent --> Response([📄 Comprehensive Travel Plan])
```

---

## 🚀 Tech Stack

* **Orchestration**: LangGraph, LangChain
* **LLM Engine**: Groq (`openai/gpt-oss-120b` or `qwen/qwen3.8-27b`)
* **Tooling Protocol**: Model Context Protocol (MCP) via `langchain-mcp-adapters` and `mcp`
* **Backend**: FastAPI, Uvicorn, Jinja2
* **Persistence**: PostgreSQL (`PostgresSaver` with connection pooling)
* **Search & APIs**: Tavily Search MCP, OpenWeather API, AviationStack API

---

## 📁 Project Structure

```text
Wayfarer-AI/
├── app.py                       # FastAPI application entry point
├── backend.py                   # LangGraph workflow, agent nodes & graph state
├── mcp_client.py                # MultiServerMCPClient & tool invocation adapters
├── custom_weather_mcp_server.py # Standalone local FastMCP server for OpenWeather
├── requirements.txt             # Python dependencies
├── .env.example                 # Template for environment variables
├── .vercelignore                # Ignore rules for Vercel Serverless deployments
├── vercel.json                  # Vercel deployment configuration & route rewrites
├── Dockerfile                   # Production container definition
├── api/
│   └── index.py                 # ASGI entrypoint for Vercel
├── static/
│   ├── script.js                # Frontend client with animated agent progress
│   └── style.css                # Modern dark-mode glassmorphic design
├── templates/
│   └── index.html               # Responsive web UI
└── tools/                       # Flight and search utilities
```

---

## 🔒 Security & Environment Variables

> [!IMPORTANT]
> **Never commit your `.env` file or API keys to GitHub.** 
> The project includes `.env` and `.venv/` in `.gitignore` by default. Only commit the template `.env.example`.

Create a `.env` file in the project root:

```powershell
# Copy the template
Copy-Item .env.example .env   # Windows
# or
cp .env.example .env          # Linux/macOS
```

Fill in your configuration in `.env`:

```env
# Groq LLM API Key (https://console.groq.com/keys)
GROQ_API_KEY=your_groq_api_key_here

# Groq Model (Default: openai/gpt-oss-120b)
GROQ_MODEL=openai/gpt-oss-120b

# Tavily Search API Key for Hotel MCP Agent (https://tavily.com)
TAVILY_API_KEY=your_tavily_api_key_here

# AviationStack API Key for Flight MCP Agent (https://aviationstack.com)
AVIATIONSTACK_API_KEY=your_aviationstack_api_key_here

# OpenWeather API Key for Weather MCP Agent (https://openweathermap.org/api)
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Default Departure Airport IATA Code
DEFAULT_ORIGIN_IATA=DAC

# PostgreSQL Database URL for State Persistence
# Free cloud Postgres: Neon (https://neon.tech), Supabase, or Render
DATABASE_URL=postgresql://user:password@host.neon.tech/neondb?sslmode=require
```

---

## 💻 Local Installation & Setup

### 1. Prerequisites
- **Python 3.10+** installed
- Free API keys for **Groq**, **Tavily**, and **OpenWeather**
- A free **PostgreSQL** database (e.g. from [Neon.tech](https://neon.tech))

### 2. Setup Virtual Environment
```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```

Open your browser to:
👉 **`http://127.0.0.1:8000`**

---

## 🌐 Deploying to Vercel

The repository is pre-configured with `vercel.json` (60-second function timeout) and `api/index.py`.

### Method 1: Via GitHub & Vercel Dashboard (Recommended)

1. Push your repository to GitHub:
   ```bash
   git add .
   git commit -m "Deploy Wayfarer AI"
   git push origin main
   ```
2. Go to [Vercel Dashboard](https://vercel.com/new) and import your repository.
3. In **Settings** $\rightarrow$ **Environment Variables**, add:
   * `GROQ_API_KEY`
   * `GROQ_MODEL` = `openai/gpt-oss-120b`
   * `TAVILY_API_KEY`
   * `AVIATIONSTACK_API_KEY`
   * `OPENWEATHER_API_KEY`
   * `DEFAULT_ORIGIN_IATA` = `DAC`
   * `DATABASE_URL` = `postgresql://...`
4. Click **Deploy**.

### Method 2: Via Vercel CLI
```bash
npm install -g vercel
vercel login
vercel
vercel env add GROQ_API_KEY
vercel --prod
```

---

## 🐳 Docker Deployment (Render / Railway / Fly.io)

For deployments with unconstrained execution time and persistent MCP subprocesses:

```bash
# Build the container
docker build -t wayfarer-ai .

# Run container
docker run -p 8000:8000 --env-file .env wayfarer-ai
```

---

## 🛠 API Usage

Submit travel planning requests programmatically:

```bash
curl -X POST http://127.0.0.1:8000/api/travel \
  -H "Content-Type: application/json" \
  -d '{"message":"Plan a 3-day trip to Tokyo with a budget of $1200"}'
```

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
