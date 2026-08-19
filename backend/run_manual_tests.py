"""
Script to run 5 varied prompts through the Kint generation and sandbox pipeline.
Records detailed findings, generated file structure, syntax validation, sandbox results, and edge cases.
"""

import asyncio
import json
import time
import urllib.request
import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.core.config import get_settings
from app.services.providers import get_llm_provider
from app.services.coder import CoderService
from app.services.sandbox import SandboxService


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


async def run_test():
    settings = get_settings()
    print(f"Loaded Settings: LLM_PROVIDER={settings.LLM_PROVIDER}")
    provider = get_llm_provider(settings)
    coder = CoderService(provider=provider)
    sandbox = SandboxService(settings=settings)

    results = []

    for idx, item in enumerate(TEST_PROMPTS, 1):
        print(f"\n========================================================")
        print(f"Running Test {idx}/5: {item['id']}")
        print(f"Category: {item['category']}")
        print(f"Prompt: {item['prompt']}")
        print(f"========================================================")

        start_time = time.time()
        test_result = {
            "test_num": idx,
            "id": item["id"],
            "category": item["category"],
            "prompt": item["prompt"],
            "generation_time_sec": 0,
            "sandbox_time_sec": 0,
            "total_time_sec": 0,
            "files_generated": [],
            "file_sizes": {},
            "has_index_html": False,
            "has_css": False,
            "has_js": False,
            "sandbox_success": False,
            "preview_url": None,
            "sandbox_id": None,
            "stdout": "",
            "stderr": "",
            "http_status": None,
            "preview_accessible": False,
            "errors": [],
            "observations": [],
            "file_contents_summary": {}
        }

        # Step 1: Code Generation
        try:
            gen_start = time.time()
            files = coder.generate_files(item["prompt"])
            test_result["generation_time_sec"] = round(time.time() - gen_start, 2)
            test_result["files_generated"] = list(files.keys())
            test_result["has_index_html"] = "index.html" in files
            test_result["has_css"] = any(f.endswith(".css") for f in files) or ("<style>" in files.get("index.html", ""))
            test_result["has_js"] = any(f.endswith(".js") for f in files) or ("<script>" in files.get("index.html", ""))

            for fname, content in files.items():
                test_result["file_sizes"][fname] = len(content)
                test_result["file_contents_summary"][fname] = {
                    "lines": len(content.splitlines()),
                    "chars": len(content),
                    "first_50_chars": content[:50].replace("\n", " ")
                }

            print(f" Generated {len(files)} files in {test_result['generation_time_sec']}s: {list(files.keys())}")
            for fname in files:
                print(f"   - {fname} ({len(files[fname])} bytes, {len(files[fname].splitlines())} lines)")

        except Exception as e:
            test_result["errors"].append(f"Generation error: {str(e)}")
            print(f" Generation failed: {e}")
            results.append(test_result)
            continue

        # Step 2: Sandbox Execution
        try:
            sb_start = time.time()
            sb_res = await sandbox.execute_files(files)
            test_result["sandbox_time_sec"] = round(time.time() - sb_start, 2)
            test_result["sandbox_success"] = sb_res.error is None
            test_result["preview_url"] = sb_res.preview_url
            test_result["sandbox_id"] = sb_res.sandbox_id
            test_result["stdout"] = sb_res.stdout
            test_result["stderr"] = sb_res.stderr

            print(f" Sandbox deployed in {test_result['sandbox_time_sec']}s")
            print(f"   Preview URL: {sb_res.preview_url}")
            print(f"   Sandbox ID: {sb_res.sandbox_id}")

            # Step 3: Check Preview URL Accessibility
            if sb_res.preview_url:
                try:
                    req = urllib.request.Request(
                        sb_res.preview_url,
                        headers={"User-Agent": "Mozilla/5.0"}
                    )
                    with urllib.request.urlopen(req, timeout=10) as response:
                        test_result["http_status"] = response.getcode()
                        html_preview = response.read().decode("utf-8", errors="ignore")
                        test_result["preview_accessible"] = response.getcode() == 200
                        print(f" Preview HTTP Status: {response.getcode()} (length: {len(html_preview)} bytes)")
                except Exception as url_err:
                    test_result["observations"].append(f"Preview URL fetch notice: {str(url_err)}")
                    print(f" Preview URL fetch notice: {url_err}")

        except Exception as e:
            test_result["errors"].append(f"Sandbox error: {str(e)}")
            print(f" Sandbox failed: {e}")

        test_result["total_time_sec"] = round(time.time() - start_time, 2)
        results.append(test_result)

    # Save full results json
    with open("docs/manual_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n\nAll 5 tests completed. Saved to docs/manual_test_results.json")

if __name__ == "__main__":
    asyncio.run(run_test())
