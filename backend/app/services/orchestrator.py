"""
Multi-Agent Orchestrator Service (Phase 2 Multi-Agent Orchestration).

Role in Pipeline:
The Orchestrator coordinates the lifecycle of the application build loop, implementing
the finite state machine (FSM) specified in docs/STATE_MACHINE.md.

State Transitions:
1. PLANNING: Planner agent analyzes prompt and decomposes it into structured steps.
2. CODING: Coder agent executes the plan to construct complete application files.
3. EXECUTING: Sandbox service deploys files to E2B Cloud Sandbox and starts the HTTP server.
4. DEBUGGING: If runtime errors or crash logs occur, Debugger agent analyzes the failure
   and generates actionable fix instructions, passing them back to Coder (capped at MAX_RETRIES).
5. DONE: Successful terminal state with live preview URL.
6. FAILED: Terminal state reached after max retry exhaustion, surfacing last error.
"""

from dataclasses import dataclass, field
from enum import Enum
import time
from typing import Dict, List, Optional

from app.schemas.debugger import DebugDiagnosis
from app.schemas.plan import Plan
from app.schemas.sandbox import SandboxResult
from app.services.coder import CoderService
from app.services.debugger import DebuggerService
from app.services.planner import PlannerService
from app.services.sandbox import SandboxService


class AgentState(str, Enum):
    """Core states of the multi-agent state machine."""
    IDLE = "idle"
    PLANNING = "planning"
    CODING = "coding"
    EXECUTING = "executing"
    DEBUGGING = "debugging"
    DONE = "done"
    FAILED = "failed"


@dataclass
class AgentExecutionContext:
    """Shared state context passed through the orchestration lifecycle."""
    prompt: str
    current_state: AgentState = AgentState.IDLE
    plan: Optional[Plan] = None
    files: Dict[str, str] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 2
    stdout: str = ""
    stderr: str = ""
    preview_url: Optional[str] = None
    sandbox_id: Optional[str] = None
    debug_history: List[DebugDiagnosis] = field(default_factory=list)
    message: str = ""
    error_message: Optional[str] = None
    duration_sec: float = 0.0


class OrchestratorService:
    """Master orchestration service managing the Planner → Coder → Sandbox → Debugger loop."""

    def __init__(
        self,
        planner: PlannerService,
        coder: CoderService,
        sandbox: SandboxService,
        debugger: DebuggerService,
        max_retries: int = 2,
    ):
        self.planner = planner
        self.coder = coder
        self.sandbox = sandbox
        self.debugger = debugger
        self.max_retries = max_retries

    async def run_pipeline(self, prompt: str) -> AgentExecutionContext:
        """
        Execute the full multi-agent orchestration loop for a user prompt.

        Args:
            prompt: User's natural language application prompt.

        Returns:
            AgentExecutionContext containing generated files, preview URL, retry counts, and status.
        """
        start_time = time.time()
        context = AgentExecutionContext(
            prompt=prompt.strip(),
            max_retries=self.max_retries,
        )

        # -------------------------------------------------------------
        # STEP 1: PLANNING
        # -------------------------------------------------------------
        context.current_state = AgentState.PLANNING
        try:
            context.plan = self.planner.create_plan(context.prompt)
        except Exception as e:
            # Fallback to direct coding if planning fails
            context.error_message = f"Planning notice: {str(e)}"

        # -------------------------------------------------------------
        # STEP 2: INITIAL CODING
        # -------------------------------------------------------------
        context.current_state = AgentState.CODING
        if context.plan:
            context.files = self.coder.generate_files_from_plan(
                plan=context.plan,
                prompt=context.prompt,
            )
        else:
            # Direct generation fallback
            context.files = self.coder.generate_files(context.prompt)

        # Ensure index.html exists
        if "index.html" not in context.files:
            context.current_state = AgentState.FAILED
            context.error_message = "Generated code is missing an index.html entry point."
            context.message = f"Build failed: {context.error_message}"
            context.duration_sec = round(time.time() - start_time, 2)
            return context

        # -------------------------------------------------------------
        # STEP 3 & 4: EXECUTION & RETRY LOOP (Sandbox → Debugger → Coder)
        # -------------------------------------------------------------
        while True:
            context.current_state = AgentState.EXECUTING
            sandbox_result: SandboxResult = await self.sandbox.execute_files(context.files)

            context.stdout = sandbox_result.stdout or ""
            context.stderr = sandbox_result.stderr or ""
            context.preview_url = sandbox_result.preview_url
            context.sandbox_id = sandbox_result.sandbox_id

            # Determine if execution was successful or has a recoverable error
            has_runtime_error = bool(sandbox_result.stderr and "error" in sandbox_result.stderr.lower())
            has_sandbox_failure = bool(sandbox_result.error and "failed" in sandbox_result.error.lower())

            # Case A: Success (Preview live or static server active without runtime crashes)
            if sandbox_result.preview_url or (not has_runtime_error and not has_sandbox_failure):
                context.current_state = AgentState.DONE
                file_count = len(context.files)
                if context.retry_count > 0:
                    context.message = (
                        f"Generated {file_count} file(s) and resolved runtime bugs after "
                        f"{context.retry_count} debug attempt(s). Preview is live!"
                    )
                elif sandbox_result.preview_url:
                    context.message = f"Generated {file_count} file(s) and deployed to sandbox. Preview is live!"
                else:
                    context.message = f"Generated {file_count} file(s) successfully."
                break

            # Case B: Execution Failure -> Check Retry Limit
            if context.retry_count >= context.max_retries:
                # Reached maximum retries without resolution
                context.current_state = AgentState.FAILED
                context.error_message = sandbox_result.error or sandbox_result.stderr or "Execution failed after maximum retries."
                context.message = (
                    f"Build failed after {context.retry_count + 1} attempt(s). "
                    f"Last error: {context.error_message}"
                )
                break

            # Case C: Debugging and Auto-Repair Loop
            context.current_state = AgentState.DEBUGGING
            diagnosis = self.debugger.diagnose_failure(
                files=context.files,
                stderr=sandbox_result.stderr or sandbox_result.error or "Unknown sandbox execution error",
                stdout=sandbox_result.stdout,
                error_message=sandbox_result.error,
                prompt=context.prompt,
            )
            context.debug_history.append(diagnosis)

            # Re-invoke Coder with diagnosis
            context.current_state = AgentState.CODING
            try:
                context.files = self.coder.apply_fix(
                    files=context.files,
                    diagnosis=diagnosis,
                    prompt=context.prompt,
                )
            except Exception as fix_err:
                context.current_state = AgentState.FAILED
                context.error_message = f"Failed to apply fix: {str(fix_err)}"
                context.message = f"Build failed during debug attempt {context.retry_count + 1}: {str(fix_err)}"
                break

            context.retry_count += 1

        context.duration_sec = round(time.time() - start_time, 2)
        return context
