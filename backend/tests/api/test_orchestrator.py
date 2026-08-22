"""Tests for OrchestratorService and Multi-Agent Retry Loop (Phase 2)."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.schemas.debugger import DebugDiagnosis
from app.schemas.plan import Plan, PlanStep
from app.schemas.sandbox import SandboxResult
from app.services.orchestrator import AgentState, OrchestratorService


@pytest.mark.asyncio
async def test_orchestrator_happy_path_no_retries():
    """Test full pipeline when sandbox succeeds on first attempt."""
    mock_planner = MagicMock()
    mock_planner.create_plan.return_value = Plan(
        title="Timer App",
        summary="Simple timer",
        target_files=["index.html", "style.css"],
        steps=[
            PlanStep(step_number=1, title="HTML", description="Markup", target_files=["index.html"]),
        ],
    )

    mock_coder = MagicMock()
    mock_coder.generate_files_from_plan.return_value = {
        "index.html": "<!DOCTYPE html><html><body><h1>Timer</h1></body></html>",
        "style.css": "body { color: white; }",
    }

    mock_sandbox = MagicMock()
    mock_sandbox.execute_files = AsyncMock(
        return_value=SandboxResult(
            stdout="HTTP server started on port 3000",
            stderr="",
            preview_url="https://preview.e2b.dev",
            sandbox_id="sbx-123",
        )
    )

    mock_debugger = MagicMock()

    orchestrator = OrchestratorService(
        planner=mock_planner,
        coder=mock_coder,
        sandbox=mock_sandbox,
        debugger=mock_debugger,
        max_retries=2,
    )

    context = await orchestrator.run_pipeline("Build a timer")

    assert context.current_state == AgentState.DONE
    assert context.retry_count == 0
    assert context.preview_url == "https://preview.e2b.dev"
    assert "index.html" in context.files
    assert "deployed to sandbox" in context.message
    mock_debugger.diagnose_failure.assert_not_called()


@pytest.mark.asyncio
async def test_orchestrator_recovers_after_debug_retry():
    """Test retry loop: sandbox error -> Debugger -> Coder fix -> sandbox success."""
    mock_planner = MagicMock()
    mock_planner.create_plan.return_value = Plan(
        title="Calculator",
        summary="Math calculator",
        target_files=["index.html", "script.js"],
        steps=[
            PlanStep(step_number=1, title="Markup", description="HTML", target_files=["index.html"]),
        ],
    )

    mock_coder = MagicMock()
    # Initial code generation returns buggy code
    mock_coder.generate_files_from_plan.return_value = {
        "index.html": "<html><body><script src='script.js'></script></body></html>",
        "script.js": "calc.init()",  # Buggy: calc not defined
    }
    # apply_fix returns repaired code
    mock_coder.apply_fix.return_value = {
        "index.html": "<html><body><script src='script.js'></script></body></html>",
        "script.js": "const calc = { init: () => {} }; calc.init();",
    }

    mock_sandbox = MagicMock()
    # First execution fails with stderr, second execution succeeds with preview_url
    mock_sandbox.execute_files = AsyncMock(
        side_effect=[
            SandboxResult(
                stdout="",
                stderr="ReferenceError: calc is not defined at script.js:1:1",
                preview_url=None,
                error="Script evaluation failed",
            ),
            SandboxResult(
                stdout="Server running",
                stderr="",
                preview_url="https://fixed-calculator.e2b.dev",
                sandbox_id="sbx-456",
            ),
        ]
    )

    mock_debugger = MagicMock()
    mock_debugger.diagnose_failure.return_value = DebugDiagnosis(
        error_summary="ReferenceError: calc is not defined",
        root_cause="calc object invoked before declaration",
        fix_instruction="Define calc object before calling calc.init()",
        files_to_modify=["script.js"],
    )

    orchestrator = OrchestratorService(
        planner=mock_planner,
        coder=mock_coder,
        sandbox=mock_sandbox,
        debugger=mock_debugger,
        max_retries=2,
    )

    context = await orchestrator.run_pipeline("Build a calculator")

    assert context.current_state == AgentState.DONE
    assert context.retry_count == 1
    assert context.preview_url == "https://fixed-calculator.e2b.dev"
    assert "resolved runtime bugs after 1 debug attempt" in context.message
    assert len(context.debug_history) == 1
    assert context.debug_history[0].error_summary == "ReferenceError: calc is not defined"
    mock_debugger.diagnose_failure.assert_called_once()
    mock_coder.apply_fix.assert_called_once()


@pytest.mark.asyncio
async def test_orchestrator_fails_gracefully_after_max_retries():
    """Test pipeline transitions to FAILED when retries are exhausted, surfacing last error."""
    mock_planner = MagicMock()
    mock_planner.create_plan.return_value = Plan(
        title="Flawed App",
        summary="App that won't run",
        target_files=["index.html"],
        steps=[PlanStep(step_number=1, title="Build", description="Markup", target_files=["index.html"])],
    )

    mock_coder = MagicMock()
    mock_coder.generate_files_from_plan.return_value = {"index.html": "<html><body>Broken</body></html>"}
    mock_coder.apply_fix.return_value = {"index.html": "<html><body>Still Broken</body></html>"}

    # Sandbox consistently returns errors across initial attempt + 2 retries
    mock_sandbox = MagicMock()
    mock_sandbox.execute_files = AsyncMock(
        return_value=SandboxResult(
            stdout="",
            stderr="Fatal error: Out of memory",
            preview_url=None,
            error="Process crashed with exit code 137",
        )
    )

    mock_debugger = MagicMock()
    mock_debugger.diagnose_failure.return_value = DebugDiagnosis(
        error_summary="OOM crash",
        root_cause="Infinite memory allocation",
        fix_instruction="Remove infinite loop",
        files_to_modify=["index.html"],
    )

    orchestrator = OrchestratorService(
        planner=mock_planner,
        coder=mock_coder,
        sandbox=mock_sandbox,
        debugger=mock_debugger,
        max_retries=2,
    )

    context = await orchestrator.run_pipeline("Build an impossible app")

    assert context.current_state == AgentState.FAILED
    assert context.retry_count == 2
    assert "Build failed after 3 attempt(s)" in context.message
    assert "Process crashed with exit code 137" in context.message
    assert "index.html" in context.files
