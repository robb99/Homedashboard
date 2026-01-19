# Gemini Project Context: HomeLab Dashboard

## Project Overview

This is a full-stack monitoring dashboard for homelab services. It provides a web-based interface to view the status of various services including Unifi, Proxmox, Plex, Docker, and Google Calendar.

The architecture consists of:

*   **Backend:** A Python application built with the **FastAPI** framework. It serves a RESTful API to fetch data from the monitored services. It uses `apscheduler` to periodically poll services in the background.
*   **Frontend:** A **React** single-page application (SPA) that consumes the backend API and presents the data in a user-friendly dashboard. It is created using `create-react-app`.
*   **Containerization:** The entire application is containerized using **Docker** and orchestrated with **Docker Compose**. This simplifies setup and deployment.
*   **Reverse Proxy:** **Nginx** is used as a reverse proxy to route requests to the frontend and backend services, and is configured to be used in the `frontend` Docker image.

## Building and Running

The recommended way to build and run the project is using Docker Compose.

**Prerequisites:**

*   Docker
*   Docker Compose

**Steps:**

1.  **Clone the repository.**
2.  **Create a `.env` file** from the `.env.example` template:
    ```bash
    cp .env.example .env
    ```
3.  **Edit the `.env` file** with the necessary credentials and endpoints for your services (Unifi, Proxmox, Plex, etc.).
4.  **Run the application** using Docker Compose:
    ```bash
    docker-compose up -d --build
    ```
5.  Access the dashboard in your browser at `http://<your-server-ip>`.

**Development:**

For development, you can run the frontend and backend services separately.

*   **Backend:**
    ```bash
    cd backend
    pip install -r requirements.txt
    uvicorn app.main:app --reload --port 8000
    ```
*   **Frontend:**
    ```bash
    cd frontend
    npm install
    npm start
    ```

## Development Conventions

*   **Backend:**
    *   The backend follows the standard FastAPI project structure.
    *   Configuration is managed through environment variables using `pydantic-settings`.
    *   Services are separated into their own modules within the `app/services` directory.
    *   API routes are defined in the `app/routers` directory.
    *   Data models are defined using Pydantic in `app/models/schemas.py`.
*   **Frontend:**
    *   The frontend is a standard `create-react-app` project.
    *   Components are organized in the `src/components` directory.
    *   A custom hook `useDashboard.js` is used to fetch data from the backend.
*   **API:**
    *   The API is served under the `/api` path.
    *   The main data endpoint is `GET /api/dashboard`, which returns a consolidated status of all monitored services.
    *   The API includes a health check endpoint at `GET /api/health`.
*   **Styling:**
    *   Basic CSS is used for styling, located in `frontend/src/styles/index.css`.
*   **Testing:**
    *   `react-scripts test` is available in the frontend, but no tests are currently implemented.
    *   There are no explicit tests for the backend.
