"""Tests for CoderService agent (Phase 2 Multi-Agent Orchestration)."""

import pytest
from unittest.mock import MagicMock

from app.core.exceptions import CodeGenerationError
from app.schemas.debugger import DebugDiagnosis
from app.schemas.plan import Plan, PlanStep
from app.services.coder import CoderService


def test_coder_execute_step_initial():
    """Test CoderService executes an initial step, creating new files."""
    mock_provider = MagicMock()
    mock_provider.generate_text.return_value = """
```index.html
<!DOCTYPE html>
<html>
<head><title>Timer</title></head>
<body><h1>00:00</h1></body>
</html>
```
"""
    coder = CoderService(provider=mock_provider)
    step = PlanStep(
        step_number=1,
        title="HTML Layout",
        description="Create basic markup",
        target_files=["index.html"],
    )
    files = coder.execute_step(step=step, prompt="Build a timer")

    assert "index.html" in files
    assert "<h1>00:00</h1>" in files["index.html"]


def test_coder_execute_step_with_prior_files():
    """Test CoderService merges step output onto existing codebase files."""
    mock_provider = MagicMock()
    mock_provider.generate_text.return_value = """
```style.css
body { background: #111; color: #fff; }
```
"""
    coder = CoderService(provider=mock_provider)
    prior_files = {"index.html": "<!DOCTYPE html><html><body><h1>Hello</h1></body></html>"}

    step = PlanStep(
        step_number=2,
        title="Styling",
        description="Add dark mode style",
        target_files=["style.css"],
    )
    updated_files = coder.execute_step(
        step=step,
        prior_files=prior_files,
        prompt="Build a dark mode timer",
    )

    assert "index.html" in updated_files
    assert "style.css" in updated_files
    assert "background: #111" in updated_files["style.css"]


def test_coder_execute_step_modifies_existing_file():
    """Test CoderService updates modified files while preserving unchanged ones."""
    mock_provider = MagicMock()
    mock_provider.generate_text.return_value = """
```index.html
<!DOCTYPE html><html><head><link rel="stylesheet" href="style.css"></head><body><h1>Updated</h1></body></html>
```
"""
    coder = CoderService(provider=mock_provider)
    prior_files = {
        "index.html": "<!DOCTYPE html><html><body><h1>Original</h1></body></html>",
        "style.css": "body { margin: 0; }",
    }

    step = PlanStep(
        step_number=2,
        title="Link Stylesheet",
        description="Link style.css in index.html head",
        target_files=["index.html"],
    )
    updated_files = coder.execute_step(
        step=step,
        prior_files=prior_files,
        prompt="Link stylesheet",
    )

    assert "Updated" in updated_files["index.html"]
    assert "style.css" in updated_files
    assert "margin: 0" in updated_files["style.css"]


def test_coder_apply_fix_success():
    """Test CoderService applies targeted debug fix from DebugDiagnosis."""
    mock_provider = MagicMock()
    mock_provider.generate_text.return_value = """
```script.js
// Fixed startTimer reference
function startTimer() { console.log('started'); }
```
"""
    coder = CoderService(provider=mock_provider)
    files = {
        "index.html": "<!DOCTYPE html><html><body><script src='script.js'></script></body></html>",
        "script.js": "// Buggy code\nstartTimer();",
    }

    diagnosis = DebugDiagnosis(
        error_summary="ReferenceError: startTimer is not defined",
        root_cause="Called startTimer before function definition",
        fix_instruction="Define function startTimer before invoking it",
        files_to_modify=["script.js"],
    )

    fixed_files = coder.apply_fix(files=files, diagnosis=diagnosis, prompt="Timer app")

    assert "Fixed startTimer reference" in fixed_files["script.js"]
    assert "index.html" in fixed_files


def test_coder_apply_fix_fails_if_index_html_removed():
    """Test CoderService raises error if debug fix accidentally discards index.html."""
    mock_provider = MagicMock()
    mock_provider.generate_text.return_value = """
```script.js
const fixed = true;
```
"""
    coder = CoderService(provider=mock_provider)
    # If starting files somehow lost index.html and fix did not provide it
    files = {"script.js": "const fixed = false;"}

    diagnosis = DebugDiagnosis(
        error_summary="Syntax error",
        root_cause="Bad variable",
        fix_instruction="Fix variable",
        files_to_modify=["script.js"],
    )

    with pytest.raises(CodeGenerationError) as excinfo:
        coder.apply_fix(files=files, diagnosis=diagnosis)
    assert "index.html" in excinfo.value.message


def test_coder_generate_files_backwards_compatible():
    """Test Phase 1 generate_files still works for single-pass generation."""
    mock_provider = MagicMock()
    mock_provider.generate_text.return_value = """
```index.html
<!DOCTYPE html><html><body><h1>App</h1></body></html>
```
```style.css
h1 { color: red; }
```
"""
    coder = CoderService(provider=mock_provider)
    files = coder.generate_files("Build a simple app")

    assert "index.html" in files
    assert "style.css" in files
