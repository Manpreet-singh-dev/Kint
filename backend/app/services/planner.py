"""
Planner agent service (Phase 2 Multi-Agent Orchestration).

Role in Pipeline:
The Planner agent is the initial cognitive step in the multi-agent orchestration loop.
It receives a user's natural language prompt, analyzes requirements, determines architecture
and state management strategies, and breaks the build process down into an ordered sequence
of discrete steps with a target file manifest.

The structured plan is then consumed by the Coder agent to generate complete, cohesive applications.
"""

import json
import re
from typing import Optional

from app.core.exceptions import CodeGenerationError
from app.schemas.plan import Plan, PlanStep
from app.services.providers.base import LLMProvider


PLANNER_SYSTEM_PROMPT = """You are an expert software architect and technical planner.
Your job is to analyze user requests for web applications and produce a clear, structured implementation plan.

Given a user's prompt, generate a JSON object with the following schema:
{
  "title": "Short descriptive app title",
  "summary": "High-level summary of the architecture, key features, layout, and state management",
  "target_files": ["index.html", "style.css", "script.js"],
  "steps": [
    {
      "step_number": 1,
      "title": "HTML Structure & Layout",
      "description": "Define semantic HTML structure, main containers, UI elements, and link assets",
      "target_files": ["index.html"]
    },
    {
      "step_number": 2,
      "title": "Responsive Styling & Aesthetics",
      "description": "Implement modern styling, dark mode theme, CSS variables, and layout aesthetics",
      "target_files": ["style.css"]
    },
    {
      "step_number": 3,
      "title": "Interactivity & State Management",
      "description": "Implement vanilla JS event listeners, state persistence (e.g. localStorage), and core features",
      "target_files": ["script.js"]
    }
  ]
}

Rules:
1. Always include "index.html" in the target_files list.
2. Break the app into 3 to 6 logical, ordered build steps.
3. Keep steps focused and actionable.
4. Return ONLY valid JSON (no extra conversational commentary). Wrap the JSON in ```json code blocks.
"""


class PlannerService:
    """Service responsible for formulating structured application build plans."""

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def create_plan(
        self,
        prompt: str,
        current_files: Optional[dict[str, str]] = None,
    ) -> Plan:
        """
        Formulate an ordered implementation plan from a user prompt, taking into account
        any existing codebase files for incremental modification.

        Args:
            prompt: User's natural language description or modification request.
            current_files: Existing codebase files if modifying an existing app.

        Returns:
            Plan object containing summary, target files, and ordered build steps.

        Raises:
            CodeGenerationError: If LLM call fails or returns completely invalid output.
        """
        if not prompt or not prompt.strip():
            raise CodeGenerationError("Prompt cannot be empty for planning.")

        if current_files:
            file_manifest = ", ".join(current_files.keys())
            user_prompt = (
                f"The user wants to enhance and modify an existing web application with current files: [{file_manifest}].\n\n"
                f"Modification / Improvement Request: {prompt.strip()}\n\n"
                f"Create an incremental modification plan detailing what to add or update in the existing files without breaking current features."
            )
        else:
            user_prompt = f"Create an implementation plan for the following web application: {prompt.strip()}"

        try:
            response_text = self.provider.generate_text(
                system_prompt=PLANNER_SYSTEM_PROMPT,
                user_prompt=user_prompt,
            )

            plan = self._parse_plan_from_response(response_text, fallback_title=prompt.strip())
            return plan

        except Exception as e:
            if isinstance(e, CodeGenerationError):
                raise
            raise CodeGenerationError(f"Failed to generate implementation plan: {str(e)}")

    def _parse_plan_from_response(self, response_text: str, fallback_title: str) -> Plan:
        """
        Extract and validate JSON plan from model response.
        Supports raw JSON and markdown-wrapped JSON code blocks.
        """
        if not response_text or not response_text.strip():
            raise CodeGenerationError("Planner received an empty response from the model.")

        cleaned = response_text.strip()

        # Extract JSON from ```json ... ``` or ``` ... ``` code blocks if present
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
        if json_match:
            cleaned = json_match.group(1).strip()
        else:
            # Fallback: attempt to find the outer-most JSON object {...}
            brace_match = re.search(r"\{[\s\S]*\}", cleaned)
            if brace_match:
                cleaned = brace_match.group(0).strip()

        try:
            data = json.loads(cleaned)
            plan = Plan.model_validate(data)

            # Ensure index.html is always in target_files
            if "index.html" not in plan.target_files:
                plan.target_files.insert(0, "index.html")

            # Ensure target_files matches files mentioned across steps
            all_step_files = {f for step in plan.steps for f in step.target_files}
            for f in all_step_files:
                if f not in plan.target_files:
                    plan.target_files.append(f)

            return plan

        except Exception:
            # If JSON parsing fails, construct a robust fallback plan from the prompt
            return self._build_fallback_plan(fallback_title)

    def _build_fallback_plan(self, prompt: str) -> Plan:
        """Construct a structured default plan when model output is non-standard."""
        title = prompt.split(".")[0][:40].strip() or "Web Application"
        return Plan(
            title=title,
            summary=f"Build a complete web application based on the user prompt: {prompt}",
            target_files=["index.html", "style.css", "script.js"],
            steps=[
                PlanStep(
                    step_number=1,
                    title="Structure & HTML Foundation",
                    description="Create index.html with semantic markup, container hierarchy, and UI elements.",
                    target_files=["index.html"],
                ),
                PlanStep(
                    step_number=2,
                    title="CSS Styling & Layout",
                    description="Style components with modern responsive CSS, dark theme, and sleek visuals.",
                    target_files=["style.css"],
                ),
                PlanStep(
                    step_number=3,
                    title="JavaScript Interactivity & State",
                    description="Implement user interactions, logic, event handlers, and data persistence.",
                    target_files=["script.js"],
                ),
            ],
        )
