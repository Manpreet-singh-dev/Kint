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
