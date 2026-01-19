# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HomeLab Dashboard is a full-stack monitoring dashboard for homelab services (Unifi, Proxmox, Plex, Docker, Google Calendar). The stack is:
- **Backend**: Python 3.11 with FastAPI
- **Frontend**: React 18 with create-react-app
- **Deployment**: Docker Compose with Nginx reverse proxy

## Common Commands

### Docker (Production)
```bash
docker-compose up -d --build     # Build and run all services
docker-compose logs -f backend   # View backend logs
docker-compose logs -f frontend  # View frontend logs
docker-compose down              # Stop all services
```

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend Development
```bash
cd frontend
npm install
npm start          # Dev server on port 3000
npm run build      # Production build
npm test           # Run tests (none currently implemented)
```

### Quick Health Check
```bash
curl http://localhost/api/health           # Through Nginx
curl http://localhost:8000/api/health      # Direct to backend
```

## Architecture

### Data Flow
```
Frontend (React) → Nginx (/api proxy) → Backend (FastAPI) → External Services
                                              ↓
                                       APScheduler (30s polls)
                                              ↓
                                       TTLCache (25s TTL)
```

### Backend Structure (`backend/app/`)
- `main.py` - FastAPI app, lifespan events, scheduler setup
- `config.py` - Pydantic settings loaded from `.env`
- `models/schemas.py` - All Pydantic models and `StatusLevel` enum
- `routers/dashboard.py` - API endpoints (`/api/dashboard`, `/api/{service}`, `/api/refresh`)
- `services/` - One module per external service (unifi.py, proxmox.py, plex.py, docker_service.py, calendar.py, cache.py)

### Frontend Structure (`frontend/src/`)
- `components/Dashboard.js` - Main orchestrator component
- `components/StatusCard.js` - Reusable card wrapper with status indicator
- `components/*Card.js` - Service-specific cards (UnifiCard, PlexCard, etc.)
- `hooks/useDashboard.js` - Data fetching hook with auto-refresh and formatting utilities
- `styles/index.css` - Dark theme with CSS custom properties

### Key Patterns
1. **Service singletons** - Services imported from `app/services/__init__.py`
2. **TTL caching** - `CacheService` wraps cachetools, cleared via `POST /api/refresh`
3. **Status enum** - All responses use `StatusLevel` (HEALTHY/WARNING/ERROR/UNKNOWN) for consistent status indicators
4. **Async throughout** - Backend uses async/await with aiohttp for external API calls

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/dashboard` | Aggregated status of all services |
| `GET /api/unifi` | Network status |
| `GET /api/proxmox` | VM/container status |
| `GET /api/plex` | Recently added media |
| `GET /api/docker` | Container status |
| `GET /api/calendar` | Upcoming events |
| `POST /api/refresh` | Force cache refresh |
| `GET /api/health` | Health check |

## Adding a New Service

1. Create `backend/app/services/newservice.py` with async fetch logic
2. Add Pydantic models to `backend/app/models/schemas.py`
3. Export singleton in `backend/app/services/__init__.py`
4. Add route in `backend/app/routers/dashboard.py`
5. Include in `poll_services()` in `backend/app/main.py`
6. Create `frontend/src/components/NewServiceCard.js`
7. Import and render in `Dashboard.js`

## Configuration

All config via environment variables (see `.env.example`). Key settings:
- `POLL_INTERVAL` - Background poll frequency (default: 30s)
- `CACHE_TTL` - Cache expiration (default: 25s)
- Service credentials: `UNIFI_*`, `PROXMOX_*`, `PLEX_*`, `DOCKER_HOST`, `GOOGLE_*`

## Styling

Dark theme uses CSS custom properties in `:root`:
- Status colors: `--status-healthy` (green), `--status-warning` (amber), `--status-error` (red)
- Background: `--bg-primary` (#0f0f1a), `--bg-secondary` (#1a1a2e)
- Accent: `--accent-blue` (#4a90d9)
