# Summary of Fixes & Current Status for HomeDashboard

This document summarizes the major troubleshooting steps and fixes applied to the HomeDashboard project.

## Summary of Fixes

### 1. Initial Goal: Display Plex Posters & Season Info
- **Problem:** The dashboard showed icons instead of posters for Plex items, and season titles were incorrect.
- **Fix:**
    - The backend was updated to construct full image URLs for Plex items, including a fallback for season posters (`backend/app/services/plex.py`).
    - The frontend was updated to display these images and to correctly show the show's title for seasons (`frontend/src/components/PlexCard.js`). **(FIXED)**

### 2. Major Problem: `git` History Conflicts & Deployment Failures
- **Problem:** We were unable to push changes to GitHub due to "divergent histories" and other `git` errors.
- **Cause:** The local working copy and the server's copy had separate, conflicting `git` histories that were different from your GitHub repository.
- **Resolution:**
    - We established the GitHub repository as the single 'source of truth'.
    - We applied all our fixes directly on your server and pushed them to GitHub.
    - We then reset your local machine's project by deleting the old folder and re-cloning the clean version from GitHub to establish a standard workflow. **(FIXED)**

### 3. Major Problem: Frontend Not Displaying ("NetworkError")
- **Problem:** The dashboard showed a "Failed to connect to API" error, caused by the frontend trying to contact `http://localhost:8000`.
- **Cause:**
    1.  The `REACT_APP_API_URL` environment variable was not being correctly set when building the frontend Docker image.
    2.  The `frontend/nginx.conf` file was missing the necessary configuration to proxy API requests to the backend.
- **Resolution:**
    - We updated `frontend/nginx.conf` to correctly forward requests from `/api` to the backend service.
    - We permanently fixed the build process by hardcoding `REACT_APP_API_URL=/api` into the `docker-compose.yml` file. **(FIXED)**

### 4. Problem: Unhealthy Backend Services
- **Problem:** The Unifi and Proxmox cards were showing errors.
- **Cause:**
    1.  The `.env` file had an incorrect IP address for `PROXMOX_HOST`.
    2.  The `backend/app/services/unifi.py` file was using outdated API paths for the Unifi controller version.
- **Resolution:**
    - We corrected the IP address for `PROXMOX_HOST` in your `.env` file. **(FIXED)**
    - We updated `unifi.py` with the correct API paths for Unifi authentication. **(FIXED)**

### 5. New Feature: Unifi Card Customization
- **Feature:** Replaced "Devices Offline" with "WAN Latency" and "Total Devices" with "Wireless Clients" (was "Devices Online" -> "Wireless Clients" and "Total Devices" -> "24h Data Usage").
- **Resolution:**
    - `backend/app/models/schemas.py` updated with new fields.
    - `backend/app/services/unifi.py` updated to calculate wireless clients, 24h data usage, and WAN latency.
    - `frontend/src/components/UnifiCard.js` updated to display new metrics. **(FIXED)**

### 6. Problem: Google Calendar (Previously: "Only one calendar event showing")
- **Problem:** Only one calendar event was being displayed, even though there were many on the calendar.
- **Fix:**
    - Corrected syntax for timezone conversion in `backend/app/services/calendar.py` to ensure `.astimezone(timezone.utc)` is called on a `datetime` object and not a string. **(FIXED)**

### 7. New Feature: 1080p Viewport-Fit Layout
- **Goal:** Restructure dashboard to fit all cards on a 1920x1080 screen without vertical scrolling.
- **Changes:**
    - Dashboard now uses CSS flexbox with `height: 100vh` and `overflow: hidden` for viewport fit.
    - Grid uses `auto-fit` with `minmax(300px, 1fr)` for flexible 3-5 column layout depending on enabled services.
    - Calendar always positioned in bottom row spanning full width.
    - Cards scroll internally when content overflows instead of page scrolling.
    - Added `--spacing-unit: 20px` CSS variable for consistent spacing throughout.
    - Responsive breakpoints for portrait/smaller screens allow vertical scrolling. **(IMPLEMENTED)**

### 8. New Feature: Header Widgets (Weather, News, DateTime)
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
- **Goal:** Remove "Updated X ago" footer from all service cards.
- **Changes:**
    - Removed timestamp footer and `formatRelativeTime` import from `StatusCard.js`.
    - Removed `lastUpdated` prop from `UnifiCard.js`, `ProxmoxCard.js`, `DockerCard.js`, `PlexCard.js`. **(IMPLEMENTED)**

### 10. Enhancement: Increase Plex Item Count
- **Goal:** Show more Plex items in the card.
- **Change:** Increased from 5 to 10 items displayed in `PlexCard.js`. **(IMPLEMENTED)**

---

## Current Status (As of Jan 19, 2026)

### Working Features
- **Network (Unifi):** Displaying wireless clients, WAN latency, total clients, 24h data usage, and device list.
- **Proxmox:** Displaying node info, CPU/memory usage, and container/VM list.
- **Plex:** Displaying 10 recently added items with posters and metadata.
- **Calendar:** Displaying upcoming events in horizontal card layout.
- **Weather:** Displaying today's and tomorrow's temperature in header (requires coordinates in `.env`).
- **News:** Displaying rotating headlines in header (requires NewsAPI key in `.env`).
- **DateTime:** Displaying current date/time in header.
- **Layout:** All cards fit on 1080p screen without vertical scrolling.

### Remaining Issues

1.  **Docker Service:** Still reports an error: `Failed to connect to Docker: Error while fetching server API version: Not supported URL scheme http+docker`.
