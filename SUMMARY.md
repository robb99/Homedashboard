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
    - We applied all our fixes directly on the server and pushed them to GitHub.
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

## Remaining Issues (As of Jan 19, 2026)

Despite the fixes above, the following issues are still present:

1.  **Plex Layout:** Plex items are visually taller than necessary, leading to wasted space and fewer items being visible without scrolling.
2.  **Google Calendar:** Only one calendar event is being displayed, even though there are many on the calendar.
3.  **Docker Service:** The Docker service still reports an error: `Failed to connect to Docker: Error while fetching server API version: Not supported URL scheme http+docker`.