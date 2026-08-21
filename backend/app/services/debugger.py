"""
Debugger agent service (Phase 2 Multi-Agent Orchestration).

Role in Pipeline:
The Debugger agent is the diagnostic engine in the multi-agent retry loop.
When code execution in the E2B sandbox fails (due to JavaScript runtime errors,
CSS syntax errors, missing DOM elements, or HTTP server bind issues), the Debugger
analyzes the failure logs, inspects the current codebase files, and produces a
structured root-cause diagnosis and actionable fix instructions for the Coder agent.
"""

import json
import re
from typing import Dict, Optional

from app.core.exceptions import CodeGenerationError
from app.schemas.debugger import DebugDiagnosis
from app.services.providers.base import LLMProvider


DEBUGGER_SYSTEM_PROMPT = """You are an expert software debugger and technical diagnostician.
Your job is to analyze code execution failures, tracebacks, and sandbox error logs, and produce a clear, actionable diagnosis and fix instruction for the Coder agent.

Given the application files, error output, and original requirements, generate a JSON object matching this schema:
{
  "error_summary": "Concise 1-sentence summary of the error (e.g. 'Uncaught TypeError: Cannot read properties of null (reading addEventListener)')",
  "root_cause": "Clear technical explanation of why the failure occurred in the code",
  "fix_instruction": "Specific, step-by-step instructions for the Coder agent detailing exactly what changes to make to fix the issue",
  "files_to_modify": ["script.js", "index.html"]
}

Rules:
1. Focus on the root cause of the error.
2. Provide concrete, actionable fix instructions (e.g. 'Add DOMContentLoaded wrapper', 'Check element existence before querySelector', 'Fix syntax error in CSS').
3. Specify exactly which files in files_to_modify need to be modified.
4. Return ONLY valid JSON wrapped in ```json code blocks.
"""

DEBUG_PROMPT_TEMPLATE = """Please diagnose the following application failure and provide fix instructions.

Original App Request:
{prompt}

Sandbox / Execution Errors (stderr / logs):
{stderr}

Standard Output (stdout):
{stdout}

Current Codebase Files:
{files_formatted}

Analyze the error logs and code, then output your diagnosis and fix instructions in the specified JSON format.
"""


class DebuggerService:
    """Service responsible for analyzing runtime failures and diagnosing code fixes."""

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def diagnose_failure(
        self,
        files: Dict[str, str],
        stderr: str,
        stdout: Optional[str] = None,
        error_message: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> DebugDiagnosis:
        """
        Analyze sandbox error logs and code files to formulate a fix diagnosis.

        Args:
            files: Dictionary mapping filenames to current content.
            stderr: Standard error output or crash traceback from sandbox.
            stdout: Standard output logs (optional).
            error_message: High-level error description (optional).
            prompt: Original user prompt (optional).

        Returns:
            DebugDiagnosis with summary, root cause, fix instruction, and files to modify.

        Raises:
            CodeGenerationError: If diagnosis generation fails.
        """
        combined_error = stderr.strip() if stderr else (error_message or "Execution failed without specific stderr.")
        stdout_str = stdout.strip() if stdout else "(No stdout captured)"
        prompt_str = prompt or "Web application execution"

        user_prompt = DEBUG_PROMPT_TEMPLATE.format(
            prompt=prompt_str,
            stderr=combined_error,
            stdout=stdout_str,
            files_formatted=self._format_files_for_prompt(files),
        )

        try:
            response_text = self.provider.generate_text(
                system_prompt=DEBUGGER_SYSTEM_PROMPT,
                user_prompt=user_prompt,
            )

            diagnosis = self._parse_diagnosis_from_response(
                response_text=response_text,
                files=files,
                raw_error=combined_error,
            )
            return diagnosis

        except Exception as e:
            if isinstance(e, CodeGenerationError):
                raise
            raise CodeGenerationError(f"Debugger agent failed to diagnose issue: {str(e)}")

    def _parse_diagnosis_from_response(
        self,
        response_text: str,
        files: Dict[str, str],
        raw_error: str,
    ) -> DebugDiagnosis:
        """
        Parse and validate JSON diagnosis from model output with fallback handling.
        """
        if not response_text or not response_text.strip():
            return self._build_fallback_diagnosis(files, raw_error)

        cleaned = response_text.strip()

        # Extract JSON from markdown ```json ... ``` blocks if present
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
        if json_match:
            cleaned = json_match.group(1).strip()
        else:
            # Fallback: search for outermost JSON object {...}
            brace_match = re.search(r"\{[\s\S]*\}", cleaned)
            if brace_match:
                cleaned = brace_match.group(0).strip()

        try:
            data = json.loads(cleaned)
            diagnosis = DebugDiagnosis.model_validate(data)

            # Ensure files_to_modify has valid files
            if not diagnosis.files_to_modify:
                diagnosis.files_to_modify = list(files.keys())

            return diagnosis

        except Exception:
            # If JSON parsing fails, construct a reliable fallback diagnosis
            return self._build_fallback_diagnosis(files, raw_error)

    def _build_fallback_diagnosis(self, files: Dict[str, str], raw_error: str) -> DebugDiagnosis:
        """Generate a heuristic diagnosis when model output is malformed."""
        first_line = raw_error.split("\n")[0][:120].strip() or "Runtime error during execution"
        target_files = []

        # Heuristic detection of target files from error string
        for fname in files:
            if fname in raw_error:
                target_files.append(fname)

        if not target_files:
            if "script.js" in files:
                target_files.append("script.js")
            if "index.html" in files:
                target_files.append("index.html")

        return DebugDiagnosis(
            error_summary=f"Execution Error: {first_line}",
            root_cause=f"Runtime error detected in sandbox: {raw_error[:300]}",
            fix_instruction="Review code syntax, ensure all DOM elements are loaded before access, verify function definitions, and check script references.",
            files_to_modify=target_files or list(files.keys()),
        )

    def _format_files_for_prompt(self, files: Dict[str, str]) -> str:
        """Format codebase files for LLM prompt context."""
        if not files:
            return "(No files found in codebase)"

        blocks = []
        for filename, content in files.items():
            blocks.append(f"```{filename}\n{content}\n```")
        return "\n\n".join(blocks)
