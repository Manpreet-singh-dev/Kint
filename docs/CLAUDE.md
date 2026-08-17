# Project: AI App Builder

Read this file at the start of every session. Full requirements live in `docs/PRD.md` — refer to it for detail, don't restate it here.

## What this is

A platform where a user describes an app in natural language and a team of agents (Planner → Coder → Sandbox → Debugger) generates, runs, and iterates on it until it works, with a live preview. Secondary goal: the codebase should clearly demonstrate multi-agent orchestration, RAG, GraphRAG, and prompt caching — favor clarity and explainability over cleverness.

## Stack (fixed — do not introduce alternatives without asking)

- **Backend:** Python, FastAPI
- **Frontend:** Next.js / React
- **Sandbox execution:** managed sandbox service (E2B) — no self-hosted Docker isolation
- **Vector store:** Postgres + pgvector
- **Code graph store:** Neo4j (Cypher queries for GraphRAG traversal)
- **LLM:** Claude API, with prompt caching enabled on static system/context content

## Architecture (one paragraph)

User prompt → **Planner agent** breaks it into build steps → **Coder agent** generates/edits files, grounded by RAG retrieval over a curated docs store → files run in the **sandbox**, which returns stdout/stderr → **Debugger agent** reads failures and either hands a fix back to the Coder (max 2-3 retries) or passes through to the **live preview**. Separately, users can ask questions about their generated app; those are answered via retrieval over the app's own embedded files, using Neo4j graph traversal for structural context (e.g. "what calls this function") and pgvector for semantic similarity.

## Conventions

- Small, single-purpose commits. One task from `docs/TASKS.md` per commit where possible.
- Every new module gets a short docstring explaining its role in the pipeline (Planner / Coder / Sandbox / Debugger / RAG / GraphRAG) — this doubles as interview prep material.
- Prefer explicit, readable control flow over clever abstractions, especially in the agent orchestration and retrieval code — this project is being used to learn these concepts, not just ship them.
- No new frameworks/libraries beyond what's listed above without flagging it first.
- Environment variables and API keys go in `.env` (never committed); add new ones to `.env.example` when introduced.

## Working agreement for this repo

- Work one task from `docs/TASKS.md` at a time. Don't jump ahead to later phases.
- For orchestration logic (Planner/Coder/Debugger loop), RAG retrieval strategy, and GraphRAG traversal: propose an approach and explain the tradeoff before implementing — these are the parts the developer wants to understand deeply, not just receive.
- For boilerplate (routes, UI scaffolding, config): implement directly, keep it simple.
- If a task is ambiguous or bigger than it looks, say so rather than guessing broadly.

## Where things live

- `docs/PRD.md` — full requirements and rationale
- `docs/TASKS.md` — current task breakdown, work top to bottom within the active phase
- `docs/BUILD_LOG.md` — running log of decisions and why they were made (append to this as you go)
