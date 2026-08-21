"""Tests for PlannerService agent (Phase 2 Multi-Agent Orchestration)."""

import pytest
from unittest.mock import MagicMock

from app.core.exceptions import CodeGenerationError
from app.schemas.plan import Plan, PlanStep
from app.services.planner import PlannerService


def test_planner_create_plan_success():
    """Test PlannerService creates structured Plan from clean JSON model output."""
    mock_provider = MagicMock()
    mock_provider.generate_text.return_value = """
    {
      "title": "Stopwatch & Timer",
      "summary": "Modern stopwatch with dark mode and laps",
      "target_files": ["index.html", "style.css", "script.js"],
      "steps": [
        {
          "step_number": 1,
          "title": "HTML Markup",
          "description": "Create base structure",
          "target_files": ["index.html"]
        },
        {
          "step_number": 2,
          "title": "Styles",
          "description": "Add dark mode CSS",
          "target_files": ["style.css"]
        },
        {
          "step_number": 3,
          "title": "Timer Logic",
          "description": "Add start, pause, lap handlers",
          "target_files": ["script.js"]
        }
      ]
    }
    """
    planner = PlannerService(provider=mock_provider)
    plan = planner.create_plan("Build a modern stopwatch app")

    assert isinstance(plan, Plan)
    assert plan.title == "Stopwatch & Timer"
    assert "index.html" in plan.target_files
    assert len(plan.steps) == 3
    assert plan.steps[0].title == "HTML Markup"
    assert plan.steps[0].step_number == 1


def test_planner_create_plan_markdown_wrapped_json():
    """Test PlannerService parses JSON inside markdown code blocks."""
    mock_provider = MagicMock()
    mock_provider.generate_text.return_value = """Here is your plan:
```json
{
  "title": "Kanban Board",
  "summary": "3-column Kanban with drag and drop",
  "target_files": ["index.html", "style.css", "script.js"],
  "steps": [
    {
      "step_number": 1,
      "title": "Markup",
      "description": "Columns and cards structure",
      "target_files": ["index.html"]
    }
  ]
}
```
Enjoy building!"""
    planner = PlannerService(provider=mock_provider)
    plan = planner.create_plan("Build a kanban board")

    assert plan.title == "Kanban Board"
    assert len(plan.steps) == 1
    assert "index.html" in plan.target_files


def test_planner_ensures_index_html_in_manifest():
    """Test PlannerService auto-inserts index.html if model omitted it."""
    mock_provider = MagicMock()
    mock_provider.generate_text.return_value = """
    {
      "title": "Snippet App",
      "summary": "Code snippet tool",
      "target_files": ["style.css", "script.js"],
      "steps": [
        {
          "step_number": 1,
          "title": "Style",
          "description": "Style file",
          "target_files": ["style.css"]
        }
      ]
    }
    """
    planner = PlannerService(provider=mock_provider)
    plan = planner.create_plan("Build a snippet tool")

    assert "index.html" in plan.target_files


def test_planner_fallback_on_unparseable_output():
    """Test PlannerService builds a reliable fallback plan when LLM output is malformed."""
    mock_provider = MagicMock()
    mock_provider.generate_text.return_value = "I cannot output JSON today. Here is some text."
    planner = PlannerService(provider=mock_provider)
    plan = planner.create_plan("Build a retro snake arcade game")

    assert isinstance(plan, Plan)
    assert "index.html" in plan.target_files
    assert len(plan.steps) == 3
    assert plan.steps[0].target_files == ["index.html"]


def test_planner_empty_prompt_raises_error():
    """Test PlannerService raises CodeGenerationError on empty prompt."""
    mock_provider = MagicMock()
    planner = PlannerService(provider=mock_provider)

    with pytest.raises(CodeGenerationError) as excinfo:
        planner.create_plan("   ")
    assert "Prompt cannot be empty" in excinfo.value.message


def test_planner_provider_failure_raises_error():
    """Test PlannerService handles upstream provider failures."""
    mock_provider = MagicMock()
    mock_provider.generate_text.side_effect = RuntimeError("API unreachable")
    planner = PlannerService(provider=mock_provider)

    with pytest.raises(CodeGenerationError) as excinfo:
        planner.create_plan("Build a calculator")
    assert "Failed to generate implementation plan" in excinfo.value.message
