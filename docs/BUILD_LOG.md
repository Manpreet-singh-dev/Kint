# Build Log

Running log of implementation decisions and rationale.

## 2026-08-17: Phase 1 Start — FastAPI Backend Scaffold

**What:** Created minimal FastAPI backend with `/generate` endpoint.

**Implementation:**
- `backend/app/main.py`: FastAPI app with CORS middleware, health check endpoint, and `/generate` POST endpoint
- Request model accepts a `prompt` string
- Response model returns a `message` and `files` dict
- Stub implementation returns hardcoded HTML/CSS files — no LLM call yet
- Added docstrings to explain each component's role in the future pipeline (Planner/Coder/Sandbox/Debugger)

**Tradeoffs:**
- Used Pydantic models for request/response validation — explicit contracts make it easier to evolve the API
- CORS configured to allow localhost:3000 (Next.js dev server) — will need to be configurable via env var for production
- Returned dict of files rather than array — makes it easier to reference files by name in later phases

**Testing:**
- Manual curl tests verified both health check and `/generate` endpoints work
- Server starts successfully with `uvicorn app.main:app`

**Next:** Wire this endpoint to a Next.js frontend (Task 2).

## 2026-08-18: Phase 1 — Next.js Frontend Scaffold

**What:** Created chat interface with message list and input field.

**Implementation:**
- `frontend/app/page.tsx`: Client-side chat component with React state management
  - Message list showing user/assistant messages with timestamps
  - Empty state with helpful prompt examples
  - Text input with Enter to send, Shift+Enter for new line
  - Loading indicator with animated dots
  - Responsive design with Tailwind CSS
- `frontend/app/layout.tsx`: Updated metadata to use "Kint" as app name
- Keyboard shortcuts: Enter to send, Shift+Enter for new line

**Tradeoffs:**
- Used client-side state (`useState`) for message management — simple for Phase 1, will need persistence layer later
- Stub timeout response simulates async behavior — makes testing the UI easier before backend integration
- Fixed 70% max width for message bubbles — balances readability with space efficiency
- Used Tailwind utility classes directly — faster to prototype than separate CSS modules

**UI/UX decisions:**
- Chat-style interface (bubbles, not table) — more intuitive for conversational app generation
- User messages right-aligned, assistant left-aligned — follows common chat conventions
- Disabled send button when input is empty — prevents accidental empty submissions
- Timestamp on each message — helps track conversation flow during development
- Empty state with example prompt — reduces friction for first-time users

**Testing:**
- Verified server starts and page renders correctly at localhost:3000
- Confirmed "Kint" branding appears in both title and header
- UI renders with proper styling in both empty and message states

**Next:** Wire frontend to backend `/generate` endpoint (Task 3).

## 2026-08-18: Phase 1 — Frontend-Backend Integration

**What:** Connected Next.js frontend to FastAPI backend `/generate` endpoint.

**Implementation:**
- `frontend/app/page.tsx`: Replaced setTimeout stub with actual fetch call
  - POST request to `http://localhost:8000/generate` with prompt
  - Parses JSON response containing `message` and `files` dict
  - Formats files as code blocks in the assistant message
  - Error handling with user-friendly messages
  - Fixed keyboard event handling for Enter key (uses `form.requestSubmit()`)

**Tradeoffs:**
- Hardcoded backend URL (localhost:8000) — sufficient for local development, will need env variable for production
- Displays files inline as markdown code blocks — simple for Phase 1, will be replaced by preview pane in later tasks
- No retry logic on failed requests — user sees error message and can try again manually
- CORS already configured in backend (Task 1), so no additional frontend changes needed

**Error handling:**
- Network errors caught and displayed to user
- Message includes hint to check if backend is running
- Non-200 responses treated as errors

**Testing:**
Manual testing should verify:
- User submits prompt → loading indicator appears
- Backend processes request → assistant message with stub files appears
- Files formatted with filename and code block
- Error case: backend offline → error message displayed

**Next:** Integrate E2B sandbox service (Task 4).

## 2026-08-18: Phase 1 — E2B Sandbox Integration

**What:** Integrated E2B Code Interpreter for executing generated files in isolated sandboxes.

**Implementation:**
- `backend/app/sandbox.py`: New module for sandbox execution
  - `execute_files()` function takes dict of {filename: content}
  - Returns SandboxResult with stdout, stderr, preview_url
  - Handles different file types (HTML → HTTP server, Python → execute, others → list)
  - Error handling for missing API keys and execution failures
- `backend/app/main.py`: Added environment variable loading and test endpoint
  - `load_dotenv()` loads .env on startup
  - `/sandbox/test` endpoint for testing E2B integration
  - Returns execution results and preview URL for a test HTML page
- `backend/pyproject.toml`: Added e2b-code-interpreter and python-dotenv dependencies
- `backend/.gitignore`: Created to exclude .env, venv, and cache files
- `backend/.env`: Template created (user needs to add their E2B_API_KEY)

**Tradeoffs:**
- Using e2b-code-interpreter (managed service) rather than self-hosted Docker — simpler setup, follows PRD requirement
- Synchronous sandbox execution — will block during file execution, but acceptable for Phase 1 single-user testing
- HTTP server on port 8000 for HTML files — simple default, can be customized later
- Error returned as part of SandboxResult rather than raising exceptions — easier to handle in API responses

**API Design:**
- SandboxResult dataclass: clean separation of success/error states
- Async function signature: ready for future async E2B operations
- Separate test endpoint: can verify sandbox works without full generation flow

**Setup required:**
1. User needs to get E2B API key from https://e2b.dev/docs/getting-started/api-key
2. Add to `backend/.env` as `E2B_API_KEY=your_key_here`
3. Test with `curl http://localhost:8000/sandbox/test`

**Next:** Add live preview pane in frontend (Task 5).

## 2026-08-18: Phase 1 — Live Preview Pane

**What:** Added two-panel layout with live preview of generated apps.

**Implementation:**
- `frontend/app/page.tsx`: Complete UI restructure
  - Two-panel layout: left chat panel (420px) + right preview panel (flexible)
  - Dark-mode-first design with zinc color palette
  - Preview state management with `previewUrl` state
  - Preview controls: refresh button, URL bar, open in new tab
  - Empty state for preview panel when no app is generated
  - Iframe sandbox for secure preview rendering
- `backend/app/main.py`: Added `preview_url` to GenerateResponse model
  - Optional field (None by default for stub responses)
  - Ready for sandbox integration in next task

**UI/UX Design:**
- Left panel: 420px fixed width for chat interface
  - Header with app name and description
  - Message list with scrolling
  - Chat input at bottom
- Right panel: Flexible width for preview
  - Browser-style chrome (refresh, URL bar, open in new tab)
  - Iframe with sandbox attributes for security
  - Empty state with helpful message when no preview

**Visual Updates:**
- Switched from light theme to dark theme (bg-zinc-950/900)
- User messages: light background (zinc-100), assistant: dark (zinc-800)
- Consistent spacing and rounded corners (rounded-xl, rounded-2xl)
- Icon-based controls for preview actions

**Security:**
- Iframe sandbox attributes: allow-scripts, allow-same-origin, allow-forms
- Prevents malicious code from accessing parent window

**Preview URL handling:**
- Frontend checks for `preview_url` in API response
- Updates preview state when URL is present
- Refresh button adds timestamp to force reload
- Open in new tab for full-screen testing

**Testing:**
To test the preview:
1. Backend needs to return `preview_url` in response
2. Next task will connect /generate → sandbox → preview_url
3. For now, layout and controls are ready

**Next:** Replace stub /generate response with Claude API call (Task 6).

## 2026-08-18: Phase 1 — Claude Code Generation

**What:** Replaced stub `/generate` endpoint with actual Claude API integration for code generation.

**Implementation:**
- `backend/app/coder.py`: New Coder agent module
  - `generate_files_from_prompt()`: Takes user prompt, returns dict of files
  - Uses Claude Sonnet 4 with structured system prompt
  - Parses code blocks from response (```filename.ext format)
  - Validates that index.html exists as entry point
  - Custom error handling with CodeGenerationError
- `backend/app/main.py`: Updated /generate endpoint
  - Replaced stub with real Coder agent call
  - Returns generated files to frontend
  - HTTPException handling for user/system errors
  - preview_url remains None (Task 7 will connect sandbox)
- `backend/pyproject.toml`: Added anthropic>=0.40.0 dependency
- `backend/.env.example`: Updated to require ANTHROPIC_API_KEY

**System Prompt Design:**
- Instructs Claude to generate complete web applications
- Requires specific code block format with filenames
- Emphasizes HTML/CSS/JavaScript with index.html entry point
- Focuses on working code first, then aesthetics
- Uses semantic HTML, responsive CSS, vanilla JS

**Response Parsing:**
- Regex pattern matches ```filename.ext blocks
- Extracts filename and content
- Filters out language markers (```html, ```css without filenames)
- Builds dict of {filename: content}

**Error Handling:**
- CodeGenerationError for user-facing issues (missing API key, bad format)
- HTTP 400 for user errors, 500 for system errors
- Validates index.html presence before returning
- Descriptive error messages for debugging

**Model Selection:**
- Using claude-sonnet-4-20250514
- max_tokens: 4096 (sufficient for small apps, can increase later)
- Single message exchange (no conversation history in Phase 1)

**Setup Required:**
1. Get Anthropic API key from https://console.anthropic.com/
2. Add to `backend/.env` as `ANTHROPIC_API_KEY=your_key_here`
3. Restart backend server
4. Test with: `curl -X POST http://localhost:8000/generate -H "Content-Type: application/json" -d '{"prompt": "Build a simple counter app"}'`

**Testing Notes:**
- Frontend will now receive actual generated files instead of stub
- Files display in chat as code blocks
- Preview panel still shows empty state (Task 7 will connect sandbox → preview)

**Next:** Connect generation → sandbox → preview for full end-to-end flow (Task 7).

---

### Backend Architecture Refactoring (Auth0 FastAPI Best Practices) - 2026-08-18

**What:** Restructured the FastAPI backend to adhere to standard enterprise architectural patterns following the [Auth0 FastAPI Best Practices](https://auth0.com/blog/fastapi-best-practices/) guide.

**Key Changes:**
- **Layered Folder Structure**:
  - `app/api/`: Modular route handlers (`routes/generate.py`, `routes/sandbox.py`, `routes/health.py`), dependency injection (`deps.py`), and aggregate router (`main.py`).
  - `app/core/`: Centralized Pydantic settings (`config.py`), domain exceptions & global exception handlers (`exceptions.py`).
  - `app/schemas/`: Typed Pydantic request/response schemas with OpenAPI `Field` examples and validation.
  - `app/services/`: Isolated business logic and agent implementations (`CoderService`, `SandboxService`).
  - `app/main.py`: Clean FastAPI application factory, CORS middleware, global exception handlers, and versioned + root router mounting.
  - `tests/`: Separated test suite with pytest fixtures, dependency overrides, and unit/integration tests (`test_health.py`, `test_generate.py`, `test_sandbox.py`).
- **Dependency Injection**: Route handlers inject services via `Depends(get_coder_service)`, `Depends(get_sandbox_service)`.
- **Domain Error Handling**: Decoupled domain exceptions mapped cleanly to HTTP responses via FastAPI global exception handlers.
- **Testing**: 100% passing pytest suite with mocked services and error assertions.

---

### Frontend Scalable Architecture Refactoring - 2026-08-19

**What:** Restructured the Next.js frontend according to the [Complete Guide to Scalable Next.js Architecture](https://dev.to/melvinprince/the-complete-guide-to-scalable-nextjs-architecture-39o0) by Melvin Prince.

**Key Changes:**
- **Modular Component Categorization**:
  - `components/ui/`: Atomic UI primitives (`Button`, `Textarea`, `Badge`, `Spinner`).
  - `components/common/`: Reusable widgets (`EmptyState`).
  - `components/layout/`: Structural layout containers (`Header`, `PreviewHeader`).
  - `components/pages/`: Feature composite components (`ChatPanel`, `MessageList`, `MessageItem`, `ChatInput`, `PreviewPanel`, `BuilderPage`).
- **Encapsulated Custom Hooks**:
  - `hooks/useAppGeneration.ts`: Handles chat messages, prompt generation, loading states, and live preview updates.
  - `hooks/useAutoScroll.ts`: Auto-scrolls message list on new messages.
  - `hooks/usePreview.ts`: Controls iframe preview URL and refreshing.
- **Decoupled API & Client Layer**:
  - `api/apiClient.ts`: Type-safe HTTP client with custom `ApiError` handling.
  - `api/generateService.ts`: Dedicated service functions for backend communication (`generateApp`, `checkBackendHealth`).
- **Central Configuration & Types**:
  - `lib/config.ts`: Environment-aware API URL resolution (`NEXT_PUBLIC_API_URL` or `http://localhost:8000`).
  - `types/`: Strict TypeScript models (`Message`, `GeneratedFiles`, `GenerateRequest`, `GenerateResponse`, `HealthResponse`, `ApiErrorResponse`).
- **Clean App Entrypoint**:
  - `app/page.tsx`: Lightweight page orchestrator rendering `<BuilderPage />`.
- **Validation**:
  - `npm run build` and `npm run lint` passed with 0 errors.

---

### Connect Generation → Sandbox → Preview (Full Pipeline) - 2026-08-19

**What:** Wired the full Phase 1 core loop end-to-end: User Prompt → Claude (Coder Agent) → E2B Sandbox → Live Preview URL → Frontend iframe.

**Key Changes:**

- **Sandbox Service Rewrite** (`app/services/sandbox.py`):
  - Switched from `e2b_code_interpreter.Sandbox` (Jupyter-style, `run_code`) to core `e2b.Sandbox` (shell-based, `commands.run` + `get_host`). The code interpreter SDK doesn't support `get_host()` for public preview URLs — the core SDK does.
  - Uses `sandbox.files.write()` to deploy generated files, `sandbox.commands.run("python3 -m http.server 3000", background=True)` to start a static server, and `sandbox.get_host(3000)` to get the public URL.
  - Sandbox is intentionally **not killed** after capturing the URL — the preview iframe needs it alive. E2B auto-terminates after its default timeout (~5 min).
  - Returns `sandbox_id` for future keep-alive/kill endpoints.
  - Raises `SandboxExecutionError` (caught by global exception handler) instead of silently returning error strings.

- **Generate Route** (`app/api/routes/generate.py`):
  - Made the handler `async def` to `await` sandbox execution.
  - Added `SandboxService` as a second DI dependency via `Depends(get_sandbox_service)`.
  - Pipeline: `coder_service.generate_files(prompt)` → `sandbox_service.execute_files(files)` → return `preview_url`.
  - Sandbox errors are non-fatal: generated files are still returned with error info in the `message` field.

- **Schema Update** (`app/schemas/sandbox.py`):
  - Added `sandbox_id: Optional[str]` to `SandboxResult`.

- **Frontend**: No changes required — already handles `preview_url` correctly.

**Tradeoffs:**
- Sandbox kept alive after URL capture means E2B credits are consumed for the full timeout window, even if the user navigates away. Acceptable for Phase 1; Phase 2 can add explicit cleanup.
- Port 3000 chosen (configurable via `SandboxService.SERVE_PORT`) — avoids conflict with common port 8000 used by backend dev server.
- `time.sleep(1)` after starting the HTTP server gives it time to bind to the port before capturing the URL. Not ideal, but simple and reliable for Phase 1.

**Testing:**
- 11/11 pytest tests passing.
- New tests: `test_generate_full_pipeline_success` (verifies full pipeline returns `preview_url`), `test_generate_sandbox_error_still_returns_files` (sandbox fails but files still returned).
- Existing tests updated to verify sandbox is NOT called when code generation fails.

**Next:** Manual test with 5 varied prompts to note what breaks (Task 8).

---

### Multi-LLM Provider Support (Claude + Gemini) - 2026-08-19

**What:** Added the ability to switch between Claude and Gemini as the code generation LLM via the `LLM_PROVIDER` environment variable. Uses the Strategy pattern with a shared `LLMProvider` protocol.

**Key Changes:**

- **Provider Abstraction** (`app/services/providers/`):
  - `base.py`: `LLMProvider` Protocol defining the `generate_text(system_prompt, user_prompt) -> str` contract.
  - `claude.py`: `ClaudeProvider` wrapping the Anthropic SDK (extracted from the old `CoderService`).
  - `gemini.py`: `GeminiProvider` wrapping the `google-genai` SDK (`generate_content` with `system_instruction` config).
  - `__init__.py`: Factory function `get_llm_provider(settings)` with lazy imports (only loads the SDK you're using).

- **Config** (`app/core/config.py`):
  - Added `LLM_PROVIDER` (default: `"claude"`) with a Pydantic validator that rejects unsupported values at startup.
  - Added `GEMINI_API_KEY`, `GEMINI_MODEL` (default: `"gemini-2.5-pro"`), `GEMINI_MAX_TOKENS` (default: `8192`).

- **CoderService** (`app/services/coder.py`):
  - Refactored to accept an `LLMProvider` instead of using Anthropic directly.
  - System prompt extracted as a module-level constant (shared across providers).
  - `generate_files()` calls `provider.generate_text()` — fully provider-agnostic.

- **Dependency Injection** (`app/api/deps.py`):
  - New DI chain: `Settings → get_llm_provider() → CoderService`.
  - The provider is resolved from `settings.LLM_PROVIDER` and injected.

- **Dependencies** (`pyproject.toml`): Added `google-genai>=1.0.0`.

**How to switch providers:**
```bash
# In .env:
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
```

**Tradeoffs:**
- Lazy provider imports avoid loading both SDKs at startup — only the selected SDK is imported.
- Gemini `max_output_tokens` set to 8192 (vs Claude's 4096) since Gemini models handle longer outputs well.
- Both providers share the same system prompt and file parsing logic — output format consistency depends on the model following the `\`\`\`filename.ext` convention (both Claude and Gemini handle this well).

**Testing:**
- 11/11 pytest tests passing.
- Tests mock at the `CoderService` level (above the provider abstraction) so they're provider-agnostic.

---

### Phase 1 Manual Testing — 5 Varied Prompts & Breakage Analysis - 2026-08-19

**What:** Executed end-to-end manual testing with 5 diverse prompts across the complete pipeline (Prompt → LLM Code Generation → E2B Cloud Sandbox Execution → Public Preview URL → HTTP Validation). Evaluated output quality, runtime reliability, file parsing, and failure modes to inform Phase 1.5 and Phase 2.

**Prompts Tested:**

1. **Stopwatch & Countdown Timer** (`prompt_1_counter_stopwatch` - Single-Page Utility & State):
   - *Prompt:* "Build a clean, modern stopwatch and countdown timer app with lap times, sound alerts (using Web Audio API), start/pause/reset buttons, and a dark mode toggle."
   - *Result:* Generated `index.html` (175 lines, 9.3 KB) and `style.css` (542 lines, 10.9 KB).
   - *Timing:* Generation: 35.95s | Sandbox: 5.16s | Total: 41.82s. Preview returned HTTP 200.
   - *Behavior:* Rendered clean UI with dark theme, stopwatch/timer tabs, lap table. Web Audio synthesized beeps directly.

2. **Kanban Todo Board** (`prompt_2_kanban_todo` - CRUD / State / LocalStorage):
   - *Prompt:* "Build a Kanban board with 3 columns (To Do, In Progress, Done), task cards with priority badges (Low, Med, High), drag-and-drop support, ability to add/edit/delete tasks, and persist state in localStorage."
   - *Result:* Generated `index.html` (138 lines, 5.9 KB) and `style.css` (532 lines, 10.5 KB).
   - *Timing:* Generation: 37.67s | Sandbox: 2.95s | Total: 41.14s. Preview returned HTTP 200.
   - *Behavior:* HTML5 Drag and Drop events (`dragstart`, `dragover`, `drop`) implemented. LocalStorage persistence for cards.

3. **Expense Tracker & Visual Chart** (`prompt_3_expense_tracker_chart` - Data / Canvas Visualization):
   - *Prompt:* "Build a personal expense tracker app with a summary card (total income, expenses, net balance), add transaction form with categories, transaction history list with filtering and delete, and an interactive HTML5 Canvas pie/bar chart showing category breakdowns."
   - *Result:* Generated `index.html` (179 lines, 8.6 KB) and `style.css` (585 lines, 10.1 KB).
   - *Timing:* Generation: 37.81s | Sandbox: 3.13s | Total: 41.38s. Preview returned HTTP 200.
   - *Behavior:* Built-in HTML5 Canvas 2D rendering for doughnut/pie breakdown without heavy third-party bundle requirements.

4. **Retro Snake Arcade Game** (`prompt_4_snake_game` - Game Loop & Real-Time Controls):
   - *Prompt:* "Build a retro Snake arcade game using HTML5 Canvas with smooth controls (arrow keys and on-screen directional buttons for mobile), score tracking, high score saved in localStorage, speed levels, pause/resume, and game over screen with restart."
   - *Result:* Generated `index.html` (115 lines, 5.0 KB) and `style.css` (375 lines, 7.7 KB).
   - *Timing:* Generation: 36.56s | Sandbox: 2.33s | Total: 39.41s. Preview returned HTTP 200.
   - *Behavior:* Game tick loop with `requestAnimationFrame` / `setInterval`, directional keylisteners, and touch d-pad for mobile.

5. **Markdown Live Editor & Exporter** (`prompt_5_markdown_editor` - Multi-Component / Rich Text):
   - *Prompt:* "Build a split-screen Markdown live editor and previewer with syntax highlighting, word and character counters, table generation toolbar buttons, and the ability to export the document as a .md file or download as HTML."
   - *Result:* Generated `index.html` (139 lines, 7.4 KB) and `style.css` (483 lines, 9.4 KB).
   - *Timing:* Generation: 37.80s | Sandbox: 2.23s | Total: 40.66s. Preview returned HTTP 200 initially.
   - *Behavior:* Used CDN links for `marked.min.js`, `highlight.min.js`, `purify.min.js`.

---

### Key Findings & What Breaks (Critical Takeaways for Phase 1.5 and Phase 2)

1. **Missing / Referenced File 404s (Single-Agent Limitation)**:
   - *Problem:* In Prompt 5 (Markdown Editor), `index.html` referenced `<script src="script.js"></script>`, but the model generated only `index.html` and `style.css`, completely omitting the `script.js` code block. This resulted in a silent 404 for `script.js` and non-functional interactivity.
   - *Architectural Need:* Phase 2 **Planner** (to enforce explicit file manifest before coding) and **Debugger** (to catch 404s/unresolved references and loop back to the Coder).

2. **E2B Sandbox Lifespan & 502 Bad Gateway Expiry**:
   - *Problem:* Sandboxes auto-terminate after ~2-5 minutes of inactivity or session disconnect. When inspecting earlier preview URLs after 3 minutes, they returned `502 Bad Gateway`.
   - *Architectural Need:* Need explicit sandbox keep-alive / heartbeat management or on-demand re-spawn for inactive preview sessions.

3. **Inline vs External File Generation Strategy**:
   - *Problem:* In prompts 1-4, the model embedded JavaScript into inline `<script>` tags inside `index.html`, whereas `style.css` was split. This was more robust than referencing an external `script.js` that might fail to generate, but makes modular editing harder.
   - *Architectural Need:* System prompt should either enforce single-file bundles (`index.html` with inline styles/scripts for simple apps) or strict multi-file manifests where every referenced `<script src="...">` or `<link href="...">` must be present in the output dictionary.

4. **Pipeline Latency**:
   - *Metrics:* LLM generation takes ~36-38s per app; E2B sandbox boot takes ~2-5s. Total roundtrip is ~40s.
   - *Architectural Need:* Phase 1.5 UI shell requires clear, animated progress indicators (Planner → Coder → Sandbox → Debugger) to provide real-time feedback during the 40s wait.

**Next:** Phase 1.5 — UI shell (Dark mode two-panel layout, chat thread, agent status trail, and browser-chrome preview).

---

### Phase 1.5 — Two-Panel Layout Shell (Dark Mode First) - 2026-08-19

**What:** Built the foundational two-panel layout shell according to the agreed wireframe (340px fixed left panel for chat and multi-agent orchestration trail, flexible right panel for live preview with browser chrome).

**Key Implementation Details:**
- **TwoPanelShell Layout Container** (`components/layout/TwoPanelShell.tsx`):
  - Strict 340px width (`w-[340px] shrink-0`) left sidebar with `bg-zinc-900/95`, subtle `border-r border-zinc-800/80`, and depth shadowing.
  - Flexible right preview panel (`flex-1 min-w-0 bg-zinc-950`) providing responsive scaling for the live iframe container.
- **Brand Header** (`components/layout/Header.tsx`):
  - Compact header optimized for the 340px sidebar width with vibrant gradient icon, version pill (`v0.1`), and clear typography.
- **Browser Chrome Preview Bar** (`components/layout/PreviewHeader.tsx`):
  - Classic browser window indicators (rose/amber/emerald dots), refresh button, SSL secured URL bar pill, open-in-new-tab action, and responsive viewport mode toggles (Desktop, Tablet, Mobile).
- **Page Orchestrator** (`components/pages/BuilderPage.tsx`):
  - Composes `ChatPanel` and `PreviewPanel` directly into `TwoPanelShell`.

**Validation:**
- `npm run lint` passed with 0 errors.
- `npm run build` compiled all static routes successfully.

**Next:** Build the chat thread UI (user/agent message bubbles, input box) inside the left panel.

---

### Phase 1.5 — Chat Thread UI (User/Agent Bubbles & Input Box) - 2026-08-19

**What:** Built the rich dark-mode chat thread UI optimized for the 340px sidebar, featuring user/assistant message bubbles with code blocks, one-click code copy, auto-scrolling message list, starter suggestion cards, and an auto-resizing input box.

**Key Implementation Details:**
- **Message Bubbles** (`components/pages/MessageItem.tsx`):
  - User messages styled with indigo accent (`bg-indigo-600/20 text-indigo-50 border border-indigo-500/30 rounded-2xl rounded-tr-xs`) and timestamp.
  - Assistant messages styled with dark container (`bg-zinc-950/90 text-zinc-200 border border-zinc-800/90 rounded-2xl rounded-tl-xs`), gradient sparkle avatar, code block detection, filename header, and one-click copy button.
- **Message List & Starter Chips** (`components/pages/MessageList.tsx`):
  - Smooth auto-scrolling with `useAutoScroll`.
  - Empty state with 4 starter suggestion cards (Stopwatch & Timer, Kanban Board, Expense Tracker, Retro Snake Game). Clicking any chip populates the input field.
  - Animated assistant loading indicator with pulsing dots.
- **Chat Input Box** (`components/pages/ChatInput.tsx`):
  - Auto-resizing textarea pinned to the bottom of the sidebar.
  - Submit button with gradient glow when input is non-empty, inline spinner during generation.
  - Keyboard shortcuts (`Enter` to submit, `Shift+Enter` for multi-line).

**Validation:**
- `npm run lint` passed with 0 errors and 0 warnings.
- `npm run build` compiled all routes cleanly.

**Next:** Build the agent status trail component (Planner/Coder/Sandbox/Debugger rows with idle/active/done/error states).

---

### Phase 1.5 — Multi-Agent Status Trail Component - 2026-08-20

**What:** Built the multi-agent status trail component (`AgentStatusTrail`) visualizing the 4 core agents (Planner → Coder → Sandbox → Debugger) directly within the 340px left sidebar.

**Key Implementation Details:**
- **Typed Agent State Contract** (`types/agent.ts`):
  - `AgentType`: `"planner" | "coder" | "sandbox" | "debugger"`
  - `AgentState`: `"idle" | "active" | "done" | "error"`
  - `AgentStepStatus`: contains label, description, state, durationSec, error, and details list.
  - `AgentTrailState`: map of all 4 agent steps.
- **AgentStatusTrail Component** (`components/common/AgentStatusTrail.tsx`):
  - Collapsible container header with summary badge (Idle, Running, Ready, Attention) and progress counter (`X/4 Completed`).
  - Vertical connecting pipeline line linking the 4 steps with subtle gradient styling.
  - Distinct state icons and micro-animations:
    - `idle`: Muted bullet dot with dark border.
    - `active`: Glowing pulse ring with animated spinner and highlighted indigo background.
    - `done`: Crisp emerald checkmark with elapsed seconds badge (e.g. `3.2s`).
    - `error`: Rose warning icon with error message text.
- **Embedded in Sidebar** (`components/pages/ChatPanel.tsx`):
  - Placed above the message list with compact padding suited for the 340px width.

**Validation:**
- `npm run lint` passed with 0 errors and 0 warnings.
- `npm run build` compiled all routes cleanly.

**Next:** Build the preview panel chrome (URL bar, refresh, open-in-new-tab) with a placeholder empty state.
