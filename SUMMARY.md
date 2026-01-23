# Summary of Fixes & Current Status for HomeDashboard

> This document is a historical incident log. Entries reflect the state at the time of each update, not necessarily the current codebase.

## How to Add New Entries
- **Date:** Use a clear date in `YYYY-MM-DD` format.
- **Branch:** Note the GitHub branch name (e.g., `main`, `feature/setup-wizard`).
- **Summary:** Briefly describe the change made.
- **What Worked:** List successful outcomes or verifications.
- **What Failed:** List failures, regressions, or remaining issues.

This document summarizes the major troubleshooting steps and fixes applied to the HomeDashboard project.

## Summary of Fixes

### 1. Initial Goal: Display Plex Posters & Season Info
**Date:** 2026-01-18
**Branch:** main
**Summary:** Initial Goal: Display Plex Posters & Season Info
**What Worked:** See details below.
**What Failed:** None noted.

- **Problem:** The dashboard showed icons instead of posters for Plex items, and season titles were incorrect.
- **Fix:**
    - The backend was updated to construct full image URLs for Plex items, including a fallback for season posters (`backend/app/services/plex.py`).
    - The frontend was updated to display these images and to correctly show the show's title for seasons (`frontend/src/components/PlexCard.js`). **(FIXED)**

### 2. Major Problem: `git` History Conflicts & Deployment Failures
**Date:** 2026-01-19
**Branch:** main
**Summary:** Major Problem: `git` History Conflicts & Deployment Failures
**What Worked:** See details below.
**What Failed:** None noted.

- **Problem:** We were unable to push changes to GitHub due to "divergent histories" and other `git` errors.
- **Cause:** The local working copy and the server's copy had separate, conflicting `git` histories that were different from your GitHub repository.
- **Resolution:**
    - We established the GitHub repository as the single 'source of truth'.
    - We applied all our fixes directly on your server and pushed them to GitHub.
    - We then reset your local machine's project by deleting the old folder and re-cloning the clean version from GitHub to establish a standard workflow. **(FIXED)**

### 3. Major Problem: Frontend Not Displaying ("NetworkError")
**Date:** 2026-01-19
**Branch:** main
**Summary:** Major Problem: Frontend Not Displaying ("NetworkError")
**What Worked:** See details below.
**What Failed:** None noted.

- **Problem:** The dashboard showed a "Failed to connect to API" error, caused by the frontend trying to contact `http://localhost:8000`.
- **Cause:**
    1.  The `REACT_APP_API_URL` environment variable was not being correctly set when building the frontend Docker image.
    2.  The `frontend/nginx.conf` file was missing the necessary configuration to proxy API requests to the backend.
- **Resolution:**
    - We updated `frontend/nginx.conf` to correctly forward requests from `/api` to the backend service.
    - We permanently fixed the build process by hardcoding `REACT_APP_API_URL=/api` into the `docker-compose.yml` file. **(FIXED)**

### 4. Problem: Unhealthy Backend Services
**Date:** 2026-01-19
**Branch:** main
**Summary:** Problem: Unhealthy Backend Services
**What Worked:** See details below.
**What Failed:** None noted.

- **Problem:** The Unifi and Proxmox cards were showing errors.
- **Cause:**
    1.  The `.env` file had an incorrect IP address for `PROXMOX_HOST`.
    2.  The `backend/app/services/unifi.py` file was using outdated API paths for the Unifi controller version.
- **Resolution:**
    - We corrected the IP address for `PROXMOX_HOST` in your `.env` file. **(FIXED)**
    - We updated `unifi.py` with the correct API paths for Unifi authentication. **(FIXED)**

### 5. New Feature: Unifi Card Customization
**Date:** 2026-01-19
**Branch:** main
**Summary:** New Feature: Unifi Card Customization
**What Worked:** See details below.
**What Failed:** None noted.

- **Feature:** Replaced "Devices Offline" with "WAN Latency" and "Total Devices" with "Wireless Clients" (was "Devices Online" -> "Wireless Clients" and "Total Devices" -> "24h Data Usage").
- **Resolution:**
    - `backend/app/models/schemas.py` updated with new fields.
    - `backend/app/services/unifi.py` updated to calculate wireless clients, 24h data usage, and WAN latency.
    - `frontend/src/components/UnifiCard.js` updated to display new metrics. **(FIXED)**

### 6. Problem: Google Calendar (Previously: "Only one calendar event showing")
**Date:** 2026-01-19
**Branch:** main
**Summary:** Problem: Google Calendar (Previously: "Only one calendar event showing")
**What Worked:** See details below.
**What Failed:** None noted.

- **Problem:** Only one calendar event was being displayed, even though there were many on the calendar.
- **Fix:**
    - Corrected syntax for timezone conversion in `backend/app/services/calendar.py` to ensure `.astimezone(timezone.utc)` is called on a `datetime` object and not a string. **(FIXED)**

### 7. New Feature: 1080p Viewport-Fit Layout
**Date:** 2026-01-19
**Branch:** main
**Summary:** New Feature: 1080p Viewport-Fit Layout
**What Worked:** See details below.
**What Failed:** None noted.

- **Goal:** Restructure dashboard to fit all cards on a 1920x1080 screen without vertical scrolling.
- **Changes:**
    - Dashboard now uses CSS flexbox with `height: 100vh` and `overflow: hidden` for viewport fit.
    - Grid uses `auto-fit` with `minmax(300px, 1fr)` for flexible 3-5 column layout depending on enabled services.
    - Calendar always positioned in bottom row spanning full width.
    - Cards scroll internally when content overflows instead of page scrolling.
    - Added `--spacing-unit: 20px` CSS variable for consistent spacing throughout.
    - Responsive breakpoints for portrait/smaller screens allow vertical scrolling. **(IMPLEMENTED)**

### 8. New Feature: Header Widgets (Weather, News, DateTime)
**Date:** 2026-01-19
**Branch:** main
**Summary:** New Feature: Header Widgets (Weather, News, DateTime)
**What Worked:** See details below.
**What Failed:** None noted.

- **Goal:** Add weather forecast, news headlines, and current time to the header area.
- **Changes:**
    - **WeatherWidget:** Displays today's and tomorrow's temperature using Open-Meteo API (no API key required).
    - **NewsWidget:** Rotates through top headlines every 10 seconds using NewsAPI.org (free API key required).
    - **DateTimeWidget:** Shows current date/time, updates every minute.
    - **RefreshIndicator:** Moved from header to fixed bottom-right corner of viewport.
- **Backend:**
    - Added `backend/app/services/weather.py` - Open-Meteo API integration.
    - Added `backend/app/services/news.py` - NewsAPI.org integration.
    - Added `WeatherStatus`, `WeatherForecast`, `NewsStatus`, `NewsHeadline` models to schemas.
    - Added `/api/weather` and `/api/news` endpoints.
- **Configuration (`.env`):**
    ```
    WEATHER_LATITUDE=38.3045
    WEATHER_LONGITUDE=-85.2498
    WEATHER_ENABLED=true
    NEWS_API_KEY=your_api_key_here
    NEWS_COUNTRY=us
    NEWS_ENABLED=true
    ```
- **Files Modified:**
    - `frontend/src/styles/index.css` - Complete layout overhaul
    - `frontend/src/components/Dashboard.js` - New header with widgets
    - `docker-compose.yml` - Pass weather/news env vars to container
    - `.env.example` - Document new configuration options
    - `backend/app/config.py` - Added weather/news settings **(IMPLEMENTED)**

### 9. UI Cleanup: Remove Card Timestamps
**Date:** 2026-01-19
**Branch:** main
**Summary:** UI Cleanup: Remove Card Timestamps
**What Worked:** See details below.
**What Failed:** None noted.

- **Goal:** Remove "Updated X ago" footer from all service cards.
- **Changes:**
    - Removed timestamp footer and `formatRelativeTime` import from `StatusCard.js`.
    - Removed `lastUpdated` prop from `UnifiCard.js`, `ProxmoxCard.js`, `DockerCard.js`, `PlexCard.js`. **(IMPLEMENTED)**

### 10. Enhancement: Increase Plex Item Count
**Date:** 2026-01-19
**Branch:** main
**Summary:** Enhancement: Increase Plex Item Count
**What Worked:** See details below.
**What Failed:** None noted.

- **Goal:** Show more Plex items in the card.
- **Change:** Increased from 5 to 10 items displayed in `PlexCard.js`. **(IMPLEMENTED)**

### 11. New Feature: "A Daily Byte" Card
**Date:** 2026-01-20
**Branch:** main
**Summary:** New Feature: "A Daily Byte" Card
**What Worked:** See details below.
**What Failed:** None noted.

- **Goal:** Add a new card displaying daily inspirational/fun content - Quote of the Day, Trivia, and Joke.
- **Changes:**
    - **DailyByteCard Component:** New frontend-only card that fetches data from free public APIs.
    - **APIs Used:**
        - Quote: ZenQuotes API (`https://zenquotes.io/api/today`) - free, no auth required
        - Joke: JokeAPI (`https://v2.jokeapi.dev/joke/Programming,Miscellaneous,Pun?safe-mode`) - free, safe mode
        - Trivia: Numbers API (`http://numbersapi.com/random/trivia`) - free, random number facts
    - **24-Hour LocalStorage Caching:** Data is cached in browser localStorage for 24 hours to minimize API calls.
    - **Fallback Data:** If APIs fail, displays preset fallback content.
    - **Grid Layout Update:** Medium breakpoint (1200-1599px) changed from 3 to 4 columns.
- **Files Created:**
    - `frontend/src/components/DailyByteCard.js` - New component with API fetching and caching logic
- **Files Modified:**
    - `frontend/src/components/Dashboard.js` - Import and render DailyByteCard after PlexCard
    - `frontend/src/styles/index.css` - Added styles for daily byte sections and updated grid layout **(IMPLEMENTED)**

### 12. Bugfix: Unifi Data Usage and Daily Byte Icon
**Date:** 2026-01-20
**Branch:** main
**Summary:** Bugfix: Unifi Data Usage and Daily Byte Icon
**What Worked:** See details below.
**What Failed:** None noted.

- **Goal:** Fix a validation error in the Unifi service and improve the Daily Byte card's icon.
- **Changes:**
    - **Unifi Pydantic Validation Error:** The `data_usage_24h` field in the `UnifiStatus` model was changed from `int` to `float` to handle decimal values from the Unifi API.
    - **Daily Byte Card Icon:** The icon for the `DailyByteCard` was changed from ✨ to 🧠 to better reflect the card's content.
- **Files Modified:**
    - `backend/app/models/schemas.py` - Updated `data_usage_24h` field.
    - `frontend/src/components/DailyByteCard.js` - Changed card icon. **(IMPLEMENTED)**

### 13. Enhancement: Daily Byte Expanded 5-Item Display with 60s Rotation
**Date:** 2026-01-20
**Branch:** feature/daily-byte-enhancement
**Summary:** Enhancement: Daily Byte Expanded 5-Item Display with 60s Rotation
**What Worked:** See details below.
**What Failed:** None noted.

- **Branch:** `feature/daily-byte-enhancement`
- **Goal:** Expand the Daily Byte card from 3 to 5 content types with automatic rotation.
- **Problem:** Original implementation had stale content due to single fetch on mount + 24-hour cache.
- **Solution:**
    - **5 Content Types:** Quote, Trivia, Joke, This Day in History, Word of the Day
    - **5 Items Per Type:** Fetches 5 items of each type from APIs
    - **60-Second Rotation:** Each section automatically advances to next item every 60 seconds
    - **Full Variety Cycle:** 5 minutes before content repeats
- **APIs Used:**
    - **Quotes:** ZenQuotes API (`https://zenquotes.io/api/quotes`) - free, no auth
    - **Trivia:** Useless Facts API (`https://uselessfacts.jsph.pl/api/v2/facts/random`) - free
    - **Jokes:** JokeAPI bulk (`https://v2.jokeapi.dev/joke/Programming,Miscellaneous,Pun?safe-mode&amount=5`) - free
    - **History:** Wikimedia Feed (`https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/all/{month}/{day}`) - free
    - **Words:** Random Word API + Dictionary API - free
- **Fallback Data:** Comprehensive fallbacks for all 5 content types if APIs fail.
- **Files Modified:**
    - `frontend/src/components/DailyByteCard.js` - Complete rewrite with new APIs, rotation logic, 5-item layout
    - `frontend/src/styles/index.css` - Added styles for history and word sections, adjusted spacing **(IMPLEMENTED)**

### 14. Enhancement: Plex Card with Library Counts and Active Streams
**Date:** 2026-01-20
**Branch:** feature/daily-byte-enhancement
**Summary:** Enhancement: Plex Card with Library Counts and Active Streams
**What Worked:** See details below.
**What Failed:** None noted.

- **Branch:** `feature/daily-byte-enhancement`
- **Goal:** Enhance the Plex card to show total movie/show counts and active streaming sessions.
- **Changes:**
    - **Metrics Update:** Replaced "Libraries" and "Recent Items" with "Movies" and "TV Shows" total counts.
    - **Now Playing Section:** Shows active streams with user name, content title, and play/pause state.
    - **Efficient API Calls:** Uses Plex pagination parameters to get counts without fetching all metadata.
- **Backend:**
    - Added `PlexSession` model with user, title, show_title, type, progress, state fields.
    - Updated `PlexStatus` with `movie_count`, `show_count`, `active_sessions` fields.
    - Fetches library counts from `/library/sections/{key}/all` with pagination params.
    - Fetches active sessions from `/status/sessions` endpoint.
- **Frontend:**
    - Updated metrics grid to show Movies and TV Shows counts.
    - Added "Now Playing" section with streaming session details.
    - Shows play/pause icons based on session state.
- **Files Modified:**
    - `backend/app/models/schemas.py` - Added PlexSession model, updated PlexStatus
    - `backend/app/services/plex.py` - Added movie/show count and active sessions fetching
    - `frontend/src/components/PlexCard.js` - Updated metrics and added Now Playing section
    - `frontend/src/styles/index.css` - Added styles for plex-now-playing and plex-session **(IMPLEMENTED)**

### 15. New Feature: Web-Based Setup Wizard
**Date:** 2026-01-21
**Branch:** feature/setup-wizard
**Summary:** New Feature: Web-Based Setup Wizard
**What Worked:** See details below.
**What Failed:** None noted.

- **Branch:** `feature/setup-wizard`
- **Goal:** Allow users to configure service credentials through a UI instead of manually editing `.env` files.
- **Changes:**
  - **Single Page Accordion UI:** All services configurable in one page with collapsible sections.
  - **Test Connection:** Each service has a "Test Connection" button to verify credentials before saving.
  - **Masked Passwords:** Sensitive fields show `********` when already configured; real values used for testing.
  - **Atomic .env Writes:** Configuration saved with backups (`.env.backup.{timestamp}`) before each write.
  - **First-Run Detection:** Dashboard shows setup wizard on first run, with Settings button to return later.
- **Backend:**
  - Added `backend/app/utils/env_manager.py` - Safe .env read/write with backup support.
  - Added `backend/app/services/test_connections.py` - Connection test functions for all 7 services.
  - Added `backend/app/routers/config.py` - Config API endpoints.
  - Added config models to `backend/app/models/schemas.py` (ConfigStatus, ConfigUpdate, ConfigResponse, TestConnectionRequest, TestConnectionResult).
- **Frontend:**
  - Added `frontend/src/styles/setup.css` - Dark theme styles for setup wizard.
  - Added `frontend/src/hooks/useSetup.js` - State management hook.
  - Added `frontend/src/components/setup/` directory with 10 components:
    - `SetupWizard.js` - Main container
    - `AccordionSection.js` - Collapsible section
    - `TestConnectionButton.js` - Reusable test button
    - `UnifiSetup.js`, `ProxmoxSetup.js`, `PlexSetup.js`, `DockerSetup.js`, `CalendarSetup.js`, `WeatherSetup.js`, `NewsSetup.js` - Service forms
  - Modified `frontend/src/App.js` - Routing between setup wizard and dashboard.
  - Modified `frontend/src/components/Dashboard.js` - Added Settings button in header.
- **API Endpoints:**
  - `GET /api/config` - Get current config (passwords masked)
  - `POST /api/config` - Save configuration to .env
  - `GET /api/config/status` - Check which services are configured
  - `POST /api/config/test/{service}` - Test connection with provided credentials
- **Known Issues Fixed:**
  - **Masked Password Testing:** Initial implementation sent masked `********` values to test endpoints, causing UniFi/Proxmox tests to fail even when services worked. Fixed by falling back to real credentials from settings when masked value is detected.
  - **Docker "Configured" Status:** Docker showed as "Configured" even with no settings because it auto-detects local socket. Fixed to only show configured when `DOCKER_HOST` is explicitly set.
- **Testing Results (Jan 21, 2026):**
  - Plex: Test connection works correctly
  - UniFi: Test connection now works (after fix for masked password)
  - Proxmox: Test connection now works (after fix for masked password)
  - Docker: Shows "Not configured" correctly when no explicit host set
  - Weather: Test connection works with valid coordinates
  - News: Test connection works with valid API key
  - Calendar: Test connection verifies credentials file exists **(IMPLEMENTED)**

### 16. Maintenance: Daily Byte Content Refresh and Trivia Source Update
**Date:** 2026-01-23
**Branch:** main
**Summary:** Reduce Daily Byte repetition and replace trivia API source.
**What Worked:** Trivia now uses Useless Facts API; cache duration reduced to 6 hours to refresh content more often.
**What Failed:** Numbers API failed intermittently in this environment; Dictionary API still returns 404 for some random words.

- **Changes:**
  - **Cache Duration:** Reduced Daily Byte cache from 24 hours to 6 hours for more frequent refresh.
  - **Trivia Source:** Switched from Numbers API to Useless Facts API.
  - **Notes:** Open Trivia DB was tested but not used.

### 17. Feature: Running Log Viewer with Backend Log API
**Date:** 2026-01-23
**Branch:** main
**Summary:** Add a settings-accessible running log viewer that aggregates frontend and backend errors.
**What Worked:** Log viewer shows client errors in real time and can fetch/clear backend logs via `/api/logs`.
**What Failed:** None noted.

- **Changes:**
  - **Frontend Logging:** Added client-side log buffer with storage, subscriptions, and global error capture.
  - **Log Viewer:** New settings-accessible page to view, refresh, and clear logs.
  - **Backend Logging:** Added in-memory log buffer and API endpoints.
  - **Endpoints:** `GET /api/logs`, `POST /api/logs/clear`
  - **Files Added:** `frontend/src/utils/logger.js`, `frontend/src/components/setup/LogViewer.js`, `backend/app/utils/log_buffer.py`, `backend/app/routers/logs.py`
  - **Files Modified:** `frontend/src/App.js`, `frontend/src/components/setup/SetupWizard.js`, `frontend/src/styles/setup.css`, `frontend/src/hooks/useDashboard.js`, `frontend/src/hooks/useSetup.js`, `frontend/src/components/DailyByteCard.js`, `backend/app/main.py`, `backend/app/models/schemas.py`

---

## Future Priority Improvements

| # | Feature | Description | Status |
|---|---------|-------------|--------|
| 1 | Web-based Setup Wizard | Configure via UI instead of .env | **Implemented** |
| 2 | Service Toggles | Enable/disable services from settings panel | **In Progress** (see below) |
| 3 | Theme Support | Light/dark mode, custom accent colors | Planned |
| 4 | Mobile Responsive | Better phone/tablet layout | Planned |
| 5 | Docker Hub Images | Pre-built images for easy deployment | Planned |

---

## Service Toggles Bug Fix (Jan 22, 2026)
**Date:** 2026-01-22
**Branch:** main
**Summary:** Diagnose and resolve service toggle behavior under Docker.
**What Worked:** Runtime config file approach (see details below).
**What Failed:** Initial env-var based approach in Docker (see details below).


### First Attempt - Changes Made

**Backend Services Modified:**
All services updated to call `get_settings()` fresh instead of caching at startup:
- `backend/app/services/unifi.py` - Removed `self.settings`, calls `get_settings()` in `get_status()`
- `backend/app/services/proxmox.py` - Same pattern
- `backend/app/services/plex.py` - Same pattern
- `backend/app/services/docker_service.py` - Same pattern
- `backend/app/services/calendar.py` - Same pattern
- `backend/app/services/news.py` - Same pattern
- `backend/app/services/weather.py` - Same pattern

**Frontend Modified:**
- `frontend/src/hooks/useDashboard.js` - Added `fetchConfig()` to get enabled flags
- `frontend/src/components/Dashboard.js` - Cards check `config?.{service}_enabled`

### Why It Still Doesn't Work

**Root Cause: Docker Environment Architecture**

The approach is fundamentally broken in Docker because:

1. **Environment Variables Are Set at Startup**
   - `docker-compose.yml` passes env vars using `${VAR:-default}` syntax
   - These are read from host's `.env` ONCE at container startup
   - After container starts, env vars are fixed until restart

2. **env_manager.py Writes to Wrong Location**
   - Path: `Path(__file__).parent.parent.parent.parent / ".env"`
   - In Docker: `__file__` = `/app/app/utils/env_manager.py`
   - Result: writes to `/.env` (root filesystem) - WRONG!

3. **Settings Can't Pick Up Changes**
   - `pydantic-settings` reads environment variables first
   - Even if `.env` path was correct, env vars are already set
   - `get_settings.cache_clear()` only clears Python cache, not env vars

4. **Missing ENV Variables in docker-compose.yml**
   ```yaml
   # These are NOT passed to the container:
   - UNIFI_ENABLED=${UNIFI_ENABLED:-true}
   - PROXMOX_ENABLED=${PROXMOX_ENABLED:-true}
   - PLEX_ENABLED=${PLEX_ENABLED:-true}
   - DOCKER_ENABLED=${DOCKER_ENABLED:-true}
   - CALENDAR_ENABLED=${CALENDAR_ENABLED:-true}
   ```

### Revised Plan: Use Runtime Config File - IMPLEMENTED

Instead of modifying `.env` (which doesn't work in Docker), use a JSON config file in a mounted volume.

**Implementation Completed:**

| Step | File | Status |
|------|------|--------|
| 1 | `backend/app/utils/runtime_config.py` | DONE - Read/write `/app/config/runtime_config.json` |
| 2 | `backend/app/routers/config.py` | DONE - Reads/saves enabled flags from runtime config |
| 3 | `backend/app/services/unifi.py` | DONE - Uses `get_service_enabled("unifi")` |
| 4 | `backend/app/services/proxmox.py` | DONE - Uses `get_service_enabled("proxmox")` |
| 5 | `backend/app/services/plex.py` | DONE - Uses `get_service_enabled("plex")` |
| 6 | `backend/app/services/docker_service.py` | DONE - Uses `get_service_enabled("docker")` |
| 7 | `backend/app/services/calendar.py` | DONE - Uses `get_service_enabled("calendar")` |
| 8 | `backend/app/services/weather.py` | DONE - Uses `get_service_enabled("weather")` |
| 9 | `backend/app/services/news.py` | DONE - Uses `get_service_enabled("news")` |
| 10 | `docker-compose.yml` | DONE - Mount config as `:rw` |
| 11 | Cache cleared on save | DONE - Clears service cache when enabled flags change |

**Expected Behavior After Fix:**
1. User unchecks "Enable UniFi Monitoring" and clicks Save
2. Backend writes `{"unifi_enabled": false}` to `/app/config/runtime_config.json`
3. Cache is cleared immediately
4. Dashboard fetches config, sees `unifi_enabled: false`
5. UniFi card hidden immediately (no restart needed)
6. Settings persist on refresh and container restart (mounted volume)

**To Test:**
```bash
docker-compose down
docker-compose up -d --build
```

---

## Current Status (As of Jan 22, 2026)
**Date:** 2026-01-22
**Branch:** main
**Summary:** Snapshot of working features and remaining issues.
**What Worked:** See Working Features below.
**What Failed:** See Remaining Issues below.


### Working Features
- **Setup Wizard:** Web-based configuration UI with test connection buttons and automatic first-run detection.
- **Network (Unifi):** Displaying wireless clients, WAN latency, total clients, 24h data usage, and device list.
- **Proxmox:** Displaying node info, CPU/memory usage, and container/VM list.
- **Plex:** Displaying total movie/show counts, active streams with user info, and 10 recently added items with posters.
- **Calendar:** Displaying upcoming events in horizontal card layout.
- **Weather:** Displaying today's and tomorrow's temperature in header (configurable via setup wizard).
- **News:** Displaying rotating headlines in header (configurable via setup wizard).
- **DateTime:** Displaying current date/time in header.
- **A Daily Byte:** Displaying 5 content sections (Quote, Trivia, Joke, History, Word) with 60-second rotation and 24-hour caching (no configuration required).
- **Layout:** All cards fit on 1080p screen without vertical scrolling.
- **Settings Access:** Settings button in dashboard header to return to setup wizard.

### Remaining Issues

1.  **Docker Service:** Still reports an error: `Failed to connect to Docker: Error while fetching server API version: Not supported URL scheme http+docker`.
