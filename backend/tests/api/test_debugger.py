"""Tests for DebuggerService agent (Phase 2 Multi-Agent Orchestration)."""

import pytest
from unittest.mock import MagicMock

from app.core.exceptions import CodeGenerationError
from app.schemas.debugger import DebugDiagnosis
from app.services.coder import CoderService
from app.services.debugger import DebuggerService


def test_debugger_diagnose_failure_success():
    """Test DebuggerService produces structured DebugDiagnosis from clean JSON output."""
    mock_provider = MagicMock()
    mock_provider.generate_text.return_value = """
    {
      "error_summary": "TypeError: btn is null",
      "root_cause": "Script accessed DOM element #start-btn before it was rendered",
      "fix_instruction": "Wrap event listener attachment in document.addEventListener('DOMContentLoaded', ...)",
      "files_to_modify": ["script.js"]
    }
    """
    debugger = DebuggerService(provider=mock_provider)
    files = {
        "index.html": "<!DOCTYPE html><html><body><button id='start-btn'>Start</button></body></html>",
        "script.js": "document.querySelector('#start-btn').addEventListener('click', () => {});",
    }
    diagnosis = debugger.diagnose_failure(
        files=files,
        stderr="Uncaught TypeError: Cannot read properties of null (reading 'addEventListener') at script.js:1:37",
        prompt="Build a stopwatch",
    )

    assert isinstance(diagnosis, DebugDiagnosis)
    assert diagnosis.error_summary == "TypeError: btn is null"
    assert "DOMContentLoaded" in diagnosis.fix_instruction
    assert diagnosis.files_to_modify == ["script.js"]


def test_debugger_diagnose_failure_markdown_wrapped_json():
    """Test DebuggerService parses JSON wrapped in markdown code blocks."""
    mock_provider = MagicMock()
    mock_provider.generate_text.return_value = """Here is the diagnosis:
```json
{
  "error_summary": "SyntaxError: Unexpected token '<'",
  "root_cause": "HTML tags leaked into CSS file",
  "fix_instruction": "Remove HTML tags from style.css",
  "files_to_modify": ["style.css"]
}
```
"""
    debugger = DebuggerService(provider=mock_provider)
    files = {"style.css": "<style>body { color: red; }</style>"}
    diagnosis = debugger.diagnose_failure(
        files=files,
        stderr="CSS parsing error in style.css",
    )

    assert diagnosis.error_summary == "SyntaxError: Unexpected token '<'"
    assert diagnosis.files_to_modify == ["style.css"]


def test_debugger_fallback_on_unparseable_output():
    """Test DebuggerService builds a reliable fallback diagnosis when model output is non-standard."""
    mock_provider = MagicMock()
    mock_provider.generate_text.return_value = "Sorry, cannot generate JSON right now."
    debugger = DebuggerService(provider=mock_provider)
    files = {
        "index.html": "<html><body><h1>Test</h1></body></html>",
        "script.js": "alert('test');",
    }
    diagnosis = debugger.diagnose_failure(
        files=files,
        stderr="ReferenceError: alert is not defined in script.js",
    )

    assert isinstance(diagnosis, DebugDiagnosis)
    assert "script.js" in diagnosis.files_to_modify
    assert "Review code syntax" in diagnosis.fix_instruction


def test_debugger_provider_failure_raises_error():
    """Test DebuggerService raises CodeGenerationError if LLM provider fails."""
    mock_provider = MagicMock()
    mock_provider.generate_text.side_effect = RuntimeError("Provider timeout")
    debugger = DebuggerService(provider=mock_provider)

    with pytest.raises(CodeGenerationError) as excinfo:
        debugger.diagnose_failure(
            files={"index.html": "<html></html>"},
            stderr="Critical crash",
        )
    assert "Debugger agent failed" in excinfo.value.message


def test_debugger_and_coder_integration_pipeline():
    """Test end-to-end debugger diagnosis feeding into Coder apply_fix."""
    mock_debugger_provider = MagicMock()
    mock_debugger_provider.generate_text.return_value = """
```json
{
  "error_summary": "Missing semicolon",
  "root_cause": "Syntax error on line 2",
  "fix_instruction": "Add semicolon on line 2 of script.js",
  "files_to_modify": ["script.js"]
}
```
"""
    debugger = DebuggerService(provider=mock_debugger_provider)

    files = {
        "index.html": "<html><body><script src='script.js'></script></body></html>",
        "script.js": "const a = 1\nconst b = 2",
    }
    diagnosis = debugger.diagnose_failure(
        files=files,
        stderr="SyntaxError on script.js",
    )

    mock_coder_provider = MagicMock()
    mock_coder_provider.generate_text.return_value = """
```script.js
const a = 1;
const b = 2;
```
"""
    coder = CoderService(provider=mock_coder_provider)
    fixed_files = coder.apply_fix(files=files, diagnosis=diagnosis)

    assert "const a = 1;" in fixed_files["script.js"]
    assert "index.html" in fixed_files
