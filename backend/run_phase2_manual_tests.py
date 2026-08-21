"""
Phase 2 Multi-Agent Orchestration Validation Script.

Executes the 5 standard test prompts through the full Multi-Agent FSM pipeline
(Planner -> Coder -> Sandbox -> Debugger loop) and records comparative metrics against Phase 1.
"""

import asyncio
import json
import os
import sys
import time
import urllib.request

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.core.config import get_settings
from app.services.providers import get_llm_provider
from app.services.planner import PlannerService
from app.services.coder import CoderService
from app.services.sandbox import SandboxService
from app.services.debugger import DebuggerService
from app.services.orchestrator import OrchestratorService, AgentState


TEST_PROMPTS = [
    {
        "id": "prompt_1_counter_stopwatch",
        "category": "Single-Page Utility / State",
        "prompt": "Build a clean, modern stopwatch and countdown timer app with lap times, sound alerts (using Web Audio API), start/pause/reset buttons, and a dark mode toggle.",
    },
    {
        "id": "prompt_2_kanban_todo",
        "category": "CRUD / Interactive State / LocalStorage",
        "prompt": "Build a Kanban board with 3 columns (To Do, In Progress, Done), task cards with priority badges (Low, Med, High), drag-and-drop support, ability to add/edit/delete tasks, and persist state in localStorage.",
    },
    {
        "id": "prompt_3_expense_tracker_chart",
        "category": "Data / Visualization / Canvas",
        "prompt": "Build a personal expense tracker app with a summary card (total income, expenses, net balance), add transaction form with categories, transaction history list with filtering and delete, and an interactive HTML5 Canvas pie/bar chart showing category breakdowns.",
    },
    {
        "id": "prompt_4_snake_game",
        "category": "Canvas Game / Real-time Loop / Input Handling",
        "prompt": "Build a retro Snake arcade game using HTML5 Canvas with smooth controls (arrow keys and on-screen directional buttons for mobile), score tracking, high score saved in localStorage, speed levels, pause/resume, and game over screen with restart.",
    },
    {
        "id": "prompt_5_markdown_editor",
        "category": "Multi-component / Rich Text / File Export",
        "prompt": "Build a split-screen Markdown live editor and previewer with syntax highlighting, word and character counters, table generation toolbar buttons, and the ability to export the document as a .md file or download as HTML.",
    },
]


async def run_phase2_tests():
    settings = get_settings()
    print(f"================================================================")
    print(f"Starting Phase 2 Multi-Agent Manual Test Suite")
    print(f"Active Provider: {settings.LLM_PROVIDER}")
    print(f"================================================================")

    provider = get_llm_provider(settings)
    planner = PlannerService(provider=provider)
    coder = CoderService(provider=provider)
    sandbox = SandboxService(settings=settings)
    debugger = DebuggerService(provider=provider)

    orchestrator = OrchestratorService(
        planner=planner,
        coder=coder,
        sandbox=sandbox,
        debugger=debugger,
        max_retries=2,
    )

    results = []

    for idx, item in enumerate(TEST_PROMPTS, 1):
        print(f"\n----------------------------------------------------------------")
        print(f"Running Test {idx}/5: {item['id']}")
        print(f"Category: {item['category']}")
        print(f"Prompt: {item['prompt']}")
        print(f"----------------------------------------------------------------")

        start_time = time.time()
        test_result = {
            "test_num": idx,
            "id": item["id"],
            "category": item["category"],
            "prompt": item["prompt"],
            "final_state": None,
            "total_time_sec": 0,
            "plan_title": None,
            "plan_step_count": 0,
            "plan_target_files": [],
            "files_generated": [],
            "file_sizes": {},
            "has_index_html": False,
            "has_css": False,
            "has_js": False,
            "retries_used": 0,
            "debug_diagnoses_count": 0,
            "debug_summaries": [],
            "sandbox_success": False,
            "preview_url": None,
            "sandbox_id": None,
            "message": "",
            "errors": [],
            "file_contents_summary": {},
        }

        try:
            context = await orchestrator.run_pipeline(item["prompt"])
            test_result["final_state"] = context.current_state.value
            test_result["total_time_sec"] = context.duration_sec
            test_result["files_generated"] = list(context.files.keys())
            test_result["has_index_html"] = "index.html" in context.files
            test_result["has_css"] = any(f.endswith(".css") for f in context.files) or ("<style>" in context.files.get("index.html", ""))
            test_result["has_js"] = any(f.endswith(".js") for f in context.files) or ("<script>" in context.files.get("index.html", ""))
            test_result["retries_used"] = context.retry_count
            test_result["preview_url"] = context.preview_url
            test_result["sandbox_id"] = context.sandbox_id
            test_result["sandbox_success"] = context.current_state == AgentState.DONE and (context.preview_url is not None or not context.error_message)
            test_result["message"] = context.message

            if context.plan:
                test_result["plan_title"] = context.plan.title
                test_result["plan_step_count"] = len(context.plan.steps)
                test_result["plan_target_files"] = context.plan.target_files

            test_result["debug_diagnoses_count"] = len(context.debug_history)
            test_result["debug_summaries"] = [d.error_summary for d in context.debug_history]

            for fname, content in context.files.items():
                test_result["file_sizes"][fname] = len(content)
                test_result["file_contents_summary"][fname] = {
                    "lines": len(content.splitlines()),
                    "chars": len(content),
                    "first_50_chars": content[:50].replace("\n", " "),
                }

            safe_title = context.plan.title.encode("ascii", "replace").decode("ascii") if context.plan else ""
            safe_message = context.message.encode("ascii", "replace").decode("ascii")

            print(f" Result: State={context.current_state.value}, Retries={context.retry_count}, Time={context.duration_sec}s")
            print(f" Files ({len(context.files)}): {list(context.files.keys())}")
            if context.plan:
                print(f" Plan: '{safe_title}' with {len(context.plan.steps)} steps")
            if context.preview_url:
                print(f" Preview URL: {context.preview_url}")
            print(f" Message: {safe_message}")

        except Exception as e:
            test_result["errors"].append(str(e))
            test_result["total_time_sec"] = round(time.time() - start_time, 2)
            safe_err = str(e).encode("ascii", "replace").decode("ascii")
            print(f" Test notice: {safe_err}")

        results.append(test_result)
        # Brief pause between test runs to respect rate limits
        if idx < len(TEST_PROMPTS):
            print(f" Pausing 5s before next test...")
            await asyncio.sleep(5)

    # Save full results json to docs/
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "phase2_manual_test_results.json"))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n================================================================")
    print(f"All 5 Phase 2 tests completed! Results saved to docs/phase2_manual_test_results.json")
    print(f"================================================================")


if __name__ == "__main__":
    asyncio.run(run_phase2_tests())
