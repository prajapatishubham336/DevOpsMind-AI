# DevOpsMind-AI
A GenAI-powered multi-agent application troubleshooting platform that analyzes logs, investigates GitHub repositories, monitors application health, and generates root-cause analysis with actionable fix recommendations using FastAPI, LangGraph, and React.

# DevOpsMind AI — Multi-Agent Application Troubleshooting

> An AI-powered multi-agent system that analyzes application logs, investigates repository context, and generates root-cause analysis with actionable fix recommendations.

**Project:** DevOpsMind AI — Multi-Agent v2.0  
**Backend:** Python · FastAPI · LangChain · LangGraph  
**Frontend:** React · Vite · Axios  
**Evaluation:** Python · JSON Dataset  
**Containerization:** Docker · Docker Compose

**GitHub Repository:** [DevOpsMind AI](https://github.com/prajapatishubham336/DevOpsMind-AI)

---

## Overview

DevOpsMind AI is a GenAI-powered application troubleshooting platform built using a multi-agent architecture.

It analyzes application logs and optional GitHub repository context to identify potential issues, investigate possible root causes, and generate structured remediation recommendations.

The system uses LangGraph to coordinate multiple specialized AI agents. Each agent performs a specific task, and the Fix & Synthesis Agent combines the available findings into a final troubleshooting report.

The project also includes a React-based dashboard, GitHub integration, monitoring utilities, and an evaluation module.

## Dashboard Preview

<img width="1348" height="600" alt="image" src="https://github.com/user-attachments/assets/8d61fcdf-0612-4e47-9a01-9c5739ea6706" />

*DevOpsMind AI dashboard showing the AI agents pipeline, log submission interface, and fix synthesis panel.*

## Key Features

- **Multi-Agent Architecture:** Coordinates specialized agents using LangGraph.
- **Intelligent Log Analysis:** Analyzes application errors, logs, and tracebacks.
- **GitHub Code Intelligence:** Uses repository context to support root-cause investigation.
- **Application Monitoring:** Includes health-check and monitoring utilities.
- **Fix & Synthesis:** Combines agent findings into structured troubleshooting recommendations.
- **GenAI Evaluations:** Includes an evaluation dataset and evaluator.
- **Interactive Dashboard:** React-based interface for submitting logs and viewing results.
- **FastAPI Backend:** Provides API endpoints for executing the multi-agent workflow.

## AI Agents

| Agent | Responsibility |
|---|---|
| Manager Agent | Understands the task and decides which specialist agents should execute. |
| Log Analysis Agent | Analyzes application logs and identifies potential errors and root causes. |
| GitHub Intelligence Agent | Investigates relevant GitHub repository files and code context. |
| Monitoring Agent | Uses application monitoring and health-check information. |
| Fix & Synthesis Agent | Combines available findings and generates fix recommendations. |

## System Architecture

```text
                React Dashboard
                       |
                       v
                 FastAPI Backend
                       |
                       v
               LangGraph Workflow
                       |
                Manager Agent
                       |
          +------------+------------+
          |            |            |
          v            v            v
      Log Agent    GitHub Agent  Monitoring Agent
          |            |            |
          +------------+------------+
                       |
                       v
               Fix & Synthesis Agent
                       |
                       v
             Troubleshooting Report
```

## Technology Stack

| Category | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| Agent Framework | LangChain |
| Workflow Orchestration | LangGraph |
| Frontend | React |
| Build Tool | Vite |
| API Communication | Axios |
| Repository Integration | GitHub |
| Evaluation | Python, JSON |
| Containerization | Docker, Docker Compose |

## Project Structure

```text
DevOpsMind-AI/
│
├── app/
│   ├── agents/
│   │   ├── common.py
│   │   ├── fix_agent.py
│   │   ├── github_agent.py
│   │   ├── log_agent.py
│   │   ├── manager_agent.py
│   │   └── monitoring_agent.py
│   │
│   ├── evals/
│   │   ├── dataset.json
│   │   └── test_evaluator.py
│   │
│   ├── integrations/
│   │   └── github.py
│   │
│   ├── monitoring/
│   │   └── health.py
│   │
│   ├── storage/
│   │   └── database.py
│   │
│   ├── tests/
│   │   └── test_agents.py
│   │
│   ├── config.py
│   ├── graph.py
│   ├── llm.py
│   ├── main.py
│   └── schemas.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Python
- Node.js and npm
- Git
- LLM provider credentials supported by the project configuration

### 1. Clone the Repository

```bash
git clone https://github.com/prajapatishubham336/DevOpsMind-AI.git

cd DevOpsMind-AI
```

### 2. Backend Setup

Create a virtual environment:

**Windows PowerShell**

```powershell
python -m venv .venv

.\.venv\Scripts\Activate.ps1
```

**Install dependencies**

```bash
pip install -r requirements.txt
```

Configure your local environment variables according to `app/config.py` and `app/llm.py`.

Keep API keys and credentials inside your local `.env` file. Never upload secrets to GitHub.

**Start the backend**

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend URL:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### 3. Frontend Setup

Open another terminal:

```bash
cd frontend
```

Install frontend dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open the local URL displayed by Vite, commonly:

```text
http://localhost:5173
```

Make sure the API base URL in `frontend/src/services/api.js` points to your running backend.

## API Endpoints

### Health Check

```http
GET /health
```

### Execute Multi-Agent Workflow

```http
POST /agents/run
```

Example request:

```json
{
  "task": "Analyze this application error and identify the likely root cause.",
  "logs": "ERROR: Application returned HTTP 500. Database connection refused.",
  "repo_context": "Python FastAPI application using PostgreSQL.",
  "github_owner": "YOUR_GITHUB_USERNAME",
  "github_repo": "YOUR_REPOSITORY",
  "app_id": null
}
```

The API returns the workflow status and the analysis generated by the agents.

## GenAI Evaluations

The project includes an evaluation module:

```text
app/evals/
├── dataset.json
└── test_evaluator.py
```

This module provides a foundation for evaluating the project's AI workflow using a dataset and an evaluator.

Run the project tests from the root directory:

```bash
pytest
```

Run the evaluator test separately:

```bash
pytest app/evals/test_evaluator.py
```

## Docker Support

Docker configuration is included through:

- `Dockerfile`
- `docker-compose.yml`
- `frontend/Dockerfile`

Review the Docker configuration and required environment variables before starting the containers.

For a Compose-based setup:

```bash
docker compose up --build
```

## Safety & Limitations

- Analysis depends on the quality and completeness of the supplied logs and repository context.
- GitHub analysis depends on the repository information available to the integration.
- Monitoring analysis requires relevant application context.
- AI-generated recommendations should be reviewed before implementation.
- The current workflow provides troubleshooting analysis and recommended fixes. Automatic source-code modification and production deployment are not claimed as implemented features.

## Future Improvements

- Expand the evaluation dataset and introduce repeatable quality metrics.
- Improve agent observability and execution tracing.
- Add more comprehensive integration and regression tests.
- Introduce approval-based automated remediation.
- Improve monitoring history and dashboard visualizations.

## Contributing

Contributions and suggestions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Implement your changes.
4. Add or update tests.
5. Submit a pull request.


## Author

**Shubham Prajapati**

AI / ML Engineer | Generative AI | Machine Learning

GitHub: [@prajapatishubham336](https://github.com/prajapatishubham336)


## License

A license file was not present in the shared project structure. Add a `LICENSE` file before publishing the project as open source.

---

**DevOpsMind AI — Building intelligent multi-agent solutions for application troubleshooting.**
