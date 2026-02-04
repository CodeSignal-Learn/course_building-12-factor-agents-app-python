# Repository Guidelines

## Project Structure & Module Organization
- `backend/`: FastAPI service and core agent logic.
  - `core/`: agent loop, prompts, tools, and state model.
  - `server/`: API endpoints and SQLite persistence.
  - `tests/`: local agent test runner.
- `frontend/`: React + Vite UI.
  - `src/`: components, API client, and app state.
- `start.sh`: convenience script to run backend + frontend.
- Logs: `backend.log`, `frontend.log` (created by `start.sh`).

## Build, Test, and Development Commands
- `./start.sh`: starts backend on `:8000` and serves built frontend on `:3000`.
- `cd backend && pip install -r requirements.txt`: install backend deps.
- `cd backend && python -m uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload`: run backend in dev.
- `cd backend && python -m tests.test_agent`: run local agent flow (no server).
- `cd frontend && npm install`: install frontend deps.
- `cd frontend && npm run dev`: Vite dev server on `:3000`.
- `cd frontend && npm run build`: production build into `frontend/dist`.
- `cd frontend && npm run preview`: preview production build.

## Coding Style & Naming Conventions
- Python: follow PEP 8 with 4-space indentation.
- Frontend: current code uses 2-space indentation and no semicolons; follow existing style.
- File names are `snake_case.py` in backend and `PascalCase.jsx` for React components.
- No formatter or linter is configured; keep changes small and consistent with surrounding code.

## Testing Guidelines
- Tests live in `backend/tests/` and run as a module (not pytest).
- Naming: use `test_*.py` for test files.
- Run with `python -m tests.test_agent` from `backend/`.

## Commit & Pull Request Guidelines
- Recent commits use short, imperative summaries (e.g., "Update documentation") without conventional prefixes.
- Keep commits focused and descriptive; prefer one logical change per commit.
- PRs: include a brief summary, testing notes (commands + results), and UI screenshots when frontend behavior changes.

## Configuration & Secrets
- Set `OPENAI_API_KEY` in your environment before running the backend.
- SQLite state is stored at `backend/data/agent_states.db` (auto-created). Delete it to reset state.
