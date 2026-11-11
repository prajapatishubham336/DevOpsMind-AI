import pytest
from app.graph import devops_graph

@pytest.mark.anyio
async def test_log_analysis_evaluation():
    sample_log = "ValueError: database connection failed on port 5432"
    
    # Asynchronous invoke use karein
    result = await devops_graph.ainvoke({"logs": sample_log})
    
    assert result is not None
    assert "analysis" in result
    print("Evaluation test passed successfully!")