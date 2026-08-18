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

