from pydantic import BaseModel, Field, HttpUrl


class LogAnalysisRequest(BaseModel):
    logs: str = Field(..., min_length=5, max_length=30000)
    repo_context: str = Field(default="Not provided", max_length=10000)


class LogAnalysisResponse(BaseModel):
    status: str
    analysis: str
    fix_suggestion: str


class MonitorAppRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    url: HttpUrl


class CollectLogRequest(BaseModel):
    logs: str = Field(..., min_length=5, max_length=30000)
    app_id: int | None = None
    repo_context: str = Field(default="Not provided", max_length=10000)

class MultiAgentRequest(BaseModel):
    task: str = Field(
        default="Analyze the provided DevOps information.",
        max_length=2000
    )

    logs: str | None = Field(
        default=None,
        max_length=30000
    )

    repo_context: str = Field(
        default="Not provided",
        max_length=10000
    )

    github_owner: str | None = None
    github_repo: str | None = None

    app_id: int | None = Field(
        default=None,
        ge=1
    )