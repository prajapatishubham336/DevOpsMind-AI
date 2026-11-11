from __future__ import annotations

import json
import os
import asyncio
import pytest
from app.agents.fix_agent import fix_agent

def load_eval_dataset():
    dataset_path = os.path.join(os.path.dirname(__file__), "../evals/dataset.json")
    if not os.path.exists(dataset_path):
        return []
    with open(dataset_path, "r") as f:
        data = json.load(f)
    return data.get("test_cases", [])

@pytest.mark.parametrize("test_case", load_eval_dataset())
def test_fix_agent_evaluation(test_case):
    # Support both key variations ('error_log' or 'input_log') from dataset
    error_log = test_case.get("error_log") or test_case.get("input_log", "")
    expected_keyword = test_case.get("expected_keyword") or test_case.get("expected_fix_pattern", "")
    
    # Handle forbidden keywords or safety checks safely
    forbidden_keywords = test_case.get("forbidden_keyword")
    if not forbidden_keywords:
        forbidden_keywords = test_case.get("should_not_contain", [])
    if isinstance(forbidden_keywords, str):
        forbidden_keywords = [forbidden_keywords]

    # State passed to fix_agent
    state = {"logs": error_log, "fix_suggestion": ""}
    
    try:
        # Run async fix_agent using asyncio
        result_state = asyncio.run(fix_agent(state))
        fix_output = result_state.get("fix_suggestion", "").lower()
    except Exception as e:
        fix_output = str(e).lower()

    # Assertions for Self-Healing Quality & Safety
    if expected_keyword:
        assert expected_keyword.lower() in fix_output, f"Expected keyword '{expected_keyword}' missing in fix output!"
    
    for forbidden in forbidden_keywords:
        assert forbidden.lower() not in fix_output, f"Safety violation! Forbidden keyword '{forbidden}' found."

def test_api_health():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code in [200, 404]