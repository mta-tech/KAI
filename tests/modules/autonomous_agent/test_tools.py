import pytest
import json
from app.modules.autonomous_agent.tools import (
    create_pandas_analysis_tool,
    create_python_execute_tool,
)


def test_pandas_analysis_summary():
    """Test pandas summary analysis."""
    analyze = create_pandas_analysis_tool()
    data = json.dumps([
        {"a": 1, "b": 4},
        {"a": 2, "b": 5},
        {"a": 3, "b": 6},
    ])
    result = analyze(data, "summary")
    assert "mean" in result
    assert "count" in result


def test_python_execute_safe():
    """Test safe Python execution."""
    execute = create_python_execute_tool()
    result = execute("print(sum([1, 2, 3]))")
    assert "6" in result


def test_python_execute_restricted():
    """Test that dangerous operations are blocked."""
    execute = create_python_execute_tool()
    result = execute("import os; os.system('ls')")
    assert "error" in result.lower()
