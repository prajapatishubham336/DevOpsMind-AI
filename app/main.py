from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from app.schemas import MultiAgentRequest
from app.graph import run_multi_agent
from fastapi.middleware.cors import CORSMiddleware
from app.config import APP_NAME
from app.schemas import (
    LogAnalysisRequest,
    LogAnalysisResponse,
    MonitorAppRequest,
    CollectLogRequest
)

from app.graph import run_analysis
from app.integrations.github import (
    get_repository,
    get_repository_files
)
from app.monitoring.health import check_website
from app.storage.database import (
    init_db,
    add_app,
    get_apps,
    get_app,
    save_log,
    save_health_check,
    get_recent_checks
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=APP_NAME,
    description="AI-powered Autonomous DevOps Engineer",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    return {
        "message": "Welcome to DevOpsMind AI",
        "status": "Running",
        "version": "2.0.0"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "application": APP_NAME
    }


# STEP 1: AI LOG ANALYSIS

@app.post("/analyze", response_model=LogAnalysisResponse)
async def analyze_logs(request: LogAnalysisRequest):
    try:
        result = await run_analysis(
            request.logs,
            request.repo_context
        )

        return LogAnalysisResponse(
            status="success",
            analysis=result["analysis"],
            fix_suggestion=result["fix_suggestion"]
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"AI analysis failed: {str(error)}"
        )


# STEP 2: GITHUB INTEGRATION

@app.get("/github/repo/{owner}/{repo}")
async def github_repository(owner: str, repo: str):
    try:
        return await get_repository(owner, repo)

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=502, detail=str(error))


@app.get("/github/files/{owner}/{repo}")
async def github_files(owner: str, repo: str):
    try:
        return await get_repository_files(owner, repo)

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=502, detail=str(error))


# STEP 2: APPLICATION REGISTRATION

@app.post("/monitor/apps")
async def register_application(request: MonitorAppRequest):
    try:
        app_id = add_app(
            request.name,
            str(request.url)
        )

        return {
            "status": "success",
            "message": "Application registered.",
            "app_id": app_id
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        if "UNIQUE constraint failed" in str(error):
            raise HTTPException(
                status_code=409,
                detail="This application URL is already registered."
            )

        raise HTTPException(status_code=500, detail=str(error))


@app.get("/monitor/apps")
async def list_applications():
    return {
        "applications": get_apps()
    }


# STEP 2: WEBSITE HEALTH CHECK

@app.post("/monitor/check/{app_id}")
async def monitor_application(app_id: int):
    application = get_app(app_id)

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found."
        )

    try:
        result = await check_website(application["url"])

        save_health_check(
            app_id,
            result["status_code"],
            result["response_time_ms"],
            result["status"]
        )

        return {
            "application": application["name"],
            **result
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.get("/monitor/history/{app_id}")
async def monitoring_history(app_id: int):
    if not get_app(app_id):
        raise HTTPException(
            status_code=404,
            detail="Application not found."
        )

    return {
        "application_id": app_id,
        "history": get_recent_checks(app_id)
    }


# STEP 2: LOG COLLECTION + AI ANALYSIS

@app.post("/monitor/logs")
async def collect_application_logs(request: CollectLogRequest):
    try:
        if request.app_id is not None:
            if not get_app(request.app_id):
                raise HTTPException(
                    status_code=404,
                    detail="Application not found."
                )

            save_log(request.app_id, request.logs)

        result = await run_analysis(
            request.logs,
            request.repo_context
        )

        return {
            "status": "success",
            "message": "Logs collected and analyzed.",
            "analysis": result["analysis"],
            "fix_suggestion": result["fix_suggestion"]
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Log collection failed: {str(error)}"
        )

# STEP 3: MULTI-AGENT DEVOPS WORKFLOW

@app.post("/agents/run")
async def run_agents(request: MultiAgentRequest):
    try:
        result = await run_multi_agent(request)

        return {
            "status": "success",
            "manager_plan": result["manager_plan"],
            "active_agents": result["active_agents"],
            "log_analysis": result["log_analysis"],
            "github_analysis": result["github_analysis"],
            "github_data": result["github_data"],
            "monitoring_analysis": result["monitoring_analysis"],
            "fix_suggestion": result["fix_suggestion"]
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Multi-agent execution failed: {str(error)}"
        )