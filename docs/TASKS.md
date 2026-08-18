# Tasks

Work top to bottom within the active phase. Check off as completed. Keep each task to something reviewable in under an hour — split further if it's bigger than that.

## Phase 1 — Core loop (Week 1)

- [x] Scaffold FastAPI backend with a single `/generate` endpoint that accepts a text prompt and returns a stub response
- [x] Scaffold Next.js frontend with a chat input and a message list
- [x] Wire frontend to backend `/generate` endpoint end to end (no LLM call yet — hardcode a fixed response)
- [x] Integrate managed sandbox service (E2B): a function that takes a dict of `{filename: content}` and returns `{stdout, stderr, preview_url}`
- [x] Add a live preview pane in the frontend that renders the sandbox's preview URL
- [x] Replace the stub `/generate` response with a single-agent Claude call: prompt in, generated files out
- [ ] Connect generation → sandbox → preview: full path from user prompt to a running app, no retry logic yet
- [ ] Manual test: run 5 varied prompts, note what breaks

## Phase 1.5 — UI shell (before Week 2)
 
Reference: Replit Agent, Lovable, and v0 — left panel for chat + agent status, right panel for live preview, dark-mode-first. Rough wireframe agreed: 340px left panel (chat thread, agent status trail with Planner/Coder/Sandbox/Debugger states, message input) + flexible right panel (browser-chrome-style preview with URL bar, refresh, open-in-new-tab).
 
- [ ] Build the two-panel layout shell (left chat panel, right preview panel) in dark mode, no live data yet
- [ ] Build the chat thread UI (user/agent message bubbles, input box) inside the left panel
- [ ] Build the agent status trail component (Planner/Coder/Sandbox/Debugger rows with idle/active/done/error states) — this is the highest-value UI piece, worth extra polish since it visualizes the multi-agent architecture directly
- [ ] Build the preview panel chrome (URL bar, refresh, open-in-new-tab) with a placeholder empty state
- [ ] Wire the agent status trail to real state from the Phase 1 generation call (idle → active → done, no error state yet since there's no retry loop until Phase 2)
- [ ] Responsive/basic empty and loading states for both panels

## Phase 2 — Multi-agent orchestration (Week 2)

- [ ] Design the agent state machine (states: planning, coding, executing, debugging, done, failed) — write this out before coding it
- [ ] Implement Planner agent: takes user prompt, outputs an ordered list of build steps
- [ ] Implement Coder agent: takes a build step (+ prior file state), outputs file changes
- [ ] Implement Debugger agent: takes sandbox stderr/stdout, outputs a diagnosis and a fix instruction for the Coder
- [ ] Wire the retry loop: sandbox failure → Debugger → Coder → sandbox again, capped at 2-3 attempts
- [ ] Add a clear "failed after N attempts" state surfaced to the user, showing the last error
- [ ] Manual test: same 5 prompts from Phase 1, compare success rate before/after the debug loop

## Phase 3 — RAG and prompt caching (Week 3)

- [ ] Stand up Postgres + pgvector
- [ ] Curate a small set of framework docs/patterns (FastAPI + Next.js) and embed them
- [ ] Retrieve top-k relevant chunks before each Coder agent call, inject into its context
- [ ] Embed the files of a freshly generated app after each successful build
- [ ] Add a "chat about this app" endpoint that answers questions grounded in those embeddings
- [ ] Enable prompt caching on the static system prompt and retrieved doc context in Claude API calls
- [ ] Benchmark: measure latency and token cost with vs. without caching, on a fixed set of repeated conversations; record results in `docs/BUILD_LOG.md`

## Phase 4 — GraphRAG (Week 4)

- [ ] Stand up Neo4j (local or hosted free tier)
- [ ] Write a parser that walks a generated project's files and extracts import/function-call relationships
- [ ] Load the extracted relationships into Neo4j as a graph
- [ ] Write Cypher queries for common traversal needs (e.g. "what does this function call", "what imports this file")
- [ ] Use graph traversal to supplement Coder/Debugger context when editing or fixing a specific file
- [ ] Qualitative comparison: for 3-5 "explain/fix this part of the app" queries, compare answers using plain vector RAG vs. GraphRAG context; record in `docs/BUILD_LOG.md`
- [ ] UI polish pass: loading states, error messages, basic styling
- [ ] Write `README.md` explaining the architecture, referencing the PRD and build log

## Stretch — LoRA fine-tuning (time-permitting, separate track)

- [ ] Pick a narrow task (commit-message generation or user-intent classification) and assemble a small labeled dataset
- [ ] Fine-tune a small open model (e.g. Llama 3.2 1B/3B or Qwen 2.5 0.5B) via HuggingFace PEFT/LoRA in a notebook
- [ ] Evaluate before/after on a held-out set
- [ ] If clean, wrap as a small standalone microservice; otherwise keep as a documented notebook artifact
- [ ] Write up the process and results in `docs/BUILD_LOG.md`
