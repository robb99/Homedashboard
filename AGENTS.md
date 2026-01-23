# Repository Guidelines

## Project Structure & Module Organization
- `backend/` houses the FastAPI service. Core code lives in `backend/app/` with `routers/`, `services/`, and `models/` submodules.
- `frontend/` is a React (create-react-app) UI. Components live in `frontend/src/components/`, hooks in `frontend/src/hooks/`, and styles in `frontend/src/styles/`.
- `config/` stores runtime config and credentials (e.g., Google Calendar JSON); `.env` is expected at the repo root.
- `nginx/` and root `docker-compose.yml` provide reverse proxy and container orchestration.

## Build, Test, and Development Commands
- `docker-compose up -d --build`: build and run the full stack with Nginx reverse proxy.
- `docker-compose logs -f backend` / `docker-compose logs -f frontend`: tail service logs.
- `cd backend && uvicorn app.main:app --reload --port 8000`: run the API locally with auto-reload.
- `cd frontend && npm start`: start the React dev server on port 3000.
- `cd frontend && npm run build`: production build of the UI.

## Coding Style & Naming Conventions
- Python uses 4-space indentation; follow existing async patterns in `backend/app/services/` and `backend/app/routers/`.
- JavaScript uses 2-space indentation; components are `PascalCase` (e.g., `StatusCard.js`) and hooks are `useX`.
- Linting for the frontend is via `react-scripts` (ESLint config `react-app`). No formatter is enforced in the repo.

## Testing Guidelines
- There are no dedicated automated test suites at this time. `npm test` runs the CRA test runner if tests are added.
- Use health checks for quick verification: `curl http://localhost/api/health` (via Nginx) or `curl http://localhost:8000/api/health` (direct).

## Commit & Pull Request Guidelines
- Recent history uses short, conventional-style subjects like `feat: add ...`. Keep messages imperative and scoped.
- Pull requests should include a concise summary, linked issues (if applicable), and UI screenshots for visual changes.
- Note any new environment variables or config file requirements in the PR description.

## Configuration & Security Notes
- Store secrets only in `.env` and `config/` (e.g., `config/google_credentials.json`). Do not commit credentials.
- When adding a new service, mirror the existing backend service pattern and ensure it is wired into `poll_services()`.

## Agent-Specific Instructions
- See `CLAUDE.md` for architecture, command references, and key patterns when modifying the stack.
