"""
Coder agent service (Phase 2 Multi-Agent Orchestration).

Role in Pipeline:
The Coder agent receives structured build steps from the Planner agent along with
any prior file state. It generates new files and modifies existing files to iteratively
construct the application.

During error recovery in the retry loop, the Coder agent also consumes structured
diagnoses from the Debugger agent to apply targeted bug fixes to the codebase.
"""

import re
from typing import Dict, Optional

from app.core.exceptions import CodeGenerationError
from app.schemas.debugger import DebugDiagnosis
from app.schemas.plan import Plan, PlanStep
from app.services.providers.base import LLMProvider


CODER_SYSTEM_PROMPT = """You are an expert web developer and coder assistant.
Your job is to generate clean, complete, working web application code based on build instructions.

Rules for output:
1. Generate complete, working code for HTML, CSS, and JavaScript files as needed.
2. Format your response with clear markdown file blocks:
```filename.ext
file content here
```
3. Use modern, responsive CSS, semantic HTML5, and vanilla JavaScript.
4. When prior files are provided, maintain consistency with existing code and integrate your changes cleanly.
5. Never output placeholders or truncated code (like "...rest of code unchanged..."). Always provide the full file contents.
"""

STEP_EXECUTION_PROMPT_TEMPLATE = """You are executing Step {step_number} of an application build plan.

Original App Request:
{prompt}

Plan Summary:
{plan_summary}

Current Step:
- Step {step_number}: {step_title}
- Instructions: {step_description}
- Target Files: {target_files}

Current Codebase Files:
{prior_files_formatted}

Please implement the requirements for this step. Output all new or modified files in ```filename.ext code blocks.
"""

DEBUG_FIX_PROMPT_TEMPLATE = """You are fixing a bug or execution error in an existing web application.

Original App Request:
{prompt}

Error Summary:
{error_summary}

Root Cause Diagnosis:
{root_cause}

Fix Instructions:
{fix_instruction}

Files Requiring Modification:
{files_to_modify}

Current Codebase Files:
{current_files_formatted}

Please apply the necessary fixes. Output all modified files in full using ```filename.ext code blocks.
"""


class CoderService:
    """Service responsible for generating and modifying code files."""

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def execute_step(
        self,
        step: PlanStep,
        plan: Optional[Plan] = None,
        prior_files: Optional[Dict[str, str]] = None,
        prompt: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Execute a single build step from the Planner, updating the codebase state.

        Args:
            step: The specific PlanStep to execute.
            plan: The complete Plan context.
            prior_files: Dictionary of existing files generated in prior steps.
            prompt: The original user prompt.

        Returns:
            Updated dictionary of all files in the codebase.

        Raises:
            CodeGenerationError: If code generation or parsing fails.
        """
        current_files = dict(prior_files or {})
        prompt_str = prompt or (plan.summary if plan else step.title)
        plan_summary = plan.summary if plan else "Multi-step web application build."

        user_prompt = STEP_EXECUTION_PROMPT_TEMPLATE.format(
            step_number=step.step_number,
            step_title=step.title,
            step_description=step.description,
            target_files=", ".join(step.target_files) if step.target_files else "as needed",
            prompt=prompt_str,
            plan_summary=plan_summary,
            prior_files_formatted=self._format_files_for_prompt(current_files),
        )

        try:
            response_text = self.provider.generate_text(
                system_prompt=CODER_SYSTEM_PROMPT,
                user_prompt=user_prompt,
            )

            new_or_modified_files = self._parse_files_from_response(
                response=response_text,
                expected_target_files=step.target_files,
            )

            if not new_or_modified_files and not current_files:
                raise CodeGenerationError(
                    f"No code files generated for step {step.step_number} ('{step.title}')."
                )

            # Merge new/modified files onto current files
            current_files.update(new_or_modified_files)

            return current_files

        except Exception as e:
            if isinstance(e, CodeGenerationError):
                raise
            raise CodeGenerationError(
                f"Coder failed on step {step.step_number} ('{step.title}'): {str(e)}"
            )

    def apply_fix(
        self,
        files: Dict[str, str],
        diagnosis: DebugDiagnosis,
        prompt: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Apply bug fixes to current files based on a Debugger diagnosis.

        Args:
            files: Current codebase files.
            diagnosis: DebugDiagnosis containing error summary, root cause, and fix instructions.
            prompt: Original user prompt.

        Returns:
            Updated dictionary of files with fixes applied.

        Raises:
            CodeGenerationError: If fix application fails.
        """
        updated_files = dict(files)
        prompt_str = prompt or "Web application repair."

        user_prompt = DEBUG_FIX_PROMPT_TEMPLATE.format(
            prompt=prompt_str,
            error_summary=diagnosis.error_summary,
            root_cause=diagnosis.root_cause,
            fix_instruction=diagnosis.fix_instruction,
            files_to_modify=", ".join(diagnosis.files_to_modify) if diagnosis.files_to_modify else "All relevant files",
            current_files_formatted=self._format_files_for_prompt(updated_files),
        )

        try:
            response_text = self.provider.generate_text(
                system_prompt=CODER_SYSTEM_PROMPT,
                user_prompt=user_prompt,
            )

            modified_files = self._parse_files_from_response(response_text)

            if not modified_files:
                raise CodeGenerationError(
                    "Coder did not produce modified code files for the debug fix."
                )

            # Merge fixed files onto existing codebase
            updated_files.update(modified_files)

            if "index.html" not in updated_files:
                raise CodeGenerationError(
                    "Fixed code must retain an index.html file as the application entry point."
                )

            return updated_files

        except Exception as e:
            if isinstance(e, CodeGenerationError):
                raise
            raise CodeGenerationError(f"Failed to apply debug fix: {str(e)}")

    def generate_files_from_plan(self, plan: Plan, prompt: str) -> Dict[str, str]:
        """
        Generate complete, cohesive application files grounded in the structured Plan.

        Args:
            plan: The structured Plan formulated by the Planner agent.
            prompt: The original user prompt.

        Returns:
            Dictionary mapping filenames to full source code.

        Raises:
            CodeGenerationError: If generation fails or index.html is missing.
        """
        steps_summary = "\n".join(
            f"Step {s.step_number}: {s.title} - {s.description} (Target: {', '.join(s.target_files)})"
            for s in plan.steps
        )
        plan_prompt = f"""Original User Request:
{prompt}

Application Plan:
Title: {plan.title}
Summary: {plan.summary}
Target Files: {', '.join(plan.target_files)}

Architecture & Implementation Steps:
{steps_summary}

Please generate the complete, production-ready code files implementing this plan. Output all files using ```filename.ext code blocks."""

        try:
            response_text = self.provider.generate_text(
                system_prompt=CODER_SYSTEM_PROMPT,
                user_prompt=plan_prompt,
            )

            files = self._parse_files_from_response(
                response=response_text,
                expected_target_files=plan.target_files,
            )

            if not files:
                raise CodeGenerationError(
                    "No code files generated from the architectural plan."
                )

            if "index.html" not in files:
                raise CodeGenerationError(
                    "Generated code must include an index.html file as the entry point."
                )

            return files

        except Exception as e:
            if isinstance(e, CodeGenerationError):
                raise
            raise CodeGenerationError(f"Failed to generate code from plan: {str(e)}")

    def generate_files(self, prompt: str) -> Dict[str, str]:
        """
        Generate complete code files from a user prompt (Phase 1 backwards compatibility).

        Args:
            prompt: User's description of the app to build.

        Returns:
            Dictionary mapping filenames to their content.

        Raises:
            CodeGenerationError: If generation fails or no index.html is present.
        """
        try:
            response_text = self.provider.generate_text(
                system_prompt=CODER_SYSTEM_PROMPT,
                user_prompt=prompt,
            )

            files = self._parse_files_from_response(response_text)

            if not files:
                raise CodeGenerationError(
                    "No files were generated. The model may not have followed the expected format."
                )

            if "index.html" not in files:
                raise CodeGenerationError(
                    "Generated code must include an index.html file as the entry point."
                )

            return files

        except Exception as e:
            if isinstance(e, CodeGenerationError):
                raise
            raise CodeGenerationError(f"Failed to generate code: {str(e)}")

    def _format_files_for_prompt(self, files: Dict[str, str]) -> str:
        """Format existing files for inclusion in LLM prompt context."""
        if not files:
            return "(No existing files yet - starting fresh codebase)"

        blocks = []
        for filename, content in files.items():
            blocks.append(f"```{filename}\n{content}\n```")
        return "\n\n".join(blocks)

    def _parse_files_from_response(
        self,
        response: str,
        expected_target_files: Optional[list[str]] = None,
    ) -> Dict[str, str]:
        """
        Parse code blocks from the LLM response into a files dictionary.

        Recognizes explicit filenames (```index.html) as well as language
        tags (```html, ```css, ```javascript) with smart mapping.
        """
        if not response:
            return {}

        files = {}
        pattern = r"```(\S+)?\n([\s\S]*?)```"
        matches = list(re.finditer(pattern, response))

        for match in matches:
            tag = (match.group(1) or "").strip().lower()
            content = match.group(2).strip()

            if not content:
                continue

            # Case 1: Tag is an explicit filename (e.g. index.html, style.css)
            if "." in tag:
                files[tag] = content
                continue

            # Case 2: Language tag mapping
            if tag in ("html", "htm") or "<!doctype html" in content.lower() or "<html" in content.lower():
                files["index.html"] = content
            elif tag in ("css", "style", "styles"):
                files["style.css"] = content
            elif tag in ("javascript", "js", "ts", "typescript"):
                files["script.js"] = content
            elif tag == "json":
                files["data.json"] = content
            elif expected_target_files and len(expected_target_files) == 1:
                # If only 1 target file was expected in this step, assign it
                files[expected_target_files[0]] = content
            elif "<!doctype" in content.lower():
                files["index.html"] = content

        return files
