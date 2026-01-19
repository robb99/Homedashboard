# HomeLab Dashboard

A monitoring dashboard for homelab services including Unifi, Proxmox, Plex, Docker, and Google Calendar.

## Features

- **Network Monitoring** - Unifi controller status, devices, and client count
- **Virtualization** - Proxmox LXC containers and VM status with resource usage
- **Media** - Latest items added to Plex
- **Containers** - Docker container monitoring
- **Calendar** - Google Calendar integration showing next 7 days
- **Auto-refresh** - Dashboard updates every 30 seconds
- **Dark Theme** - Optimized for always-on kiosk displays

## Quick Start

### Using Docker Compose (Recommended)

1. Clone or copy this repository to your server
2. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` with your service credentials
4. Start the application:
   ```bash
   docker-compose up -d
   ```
5. Access the dashboard at `http://your-server-ip`

### Manual Installation

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables (see Configuration section)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm start  # Development
npm run build  # Production build
```

## Configuration

Create a `.env` file based on `.env.example`:

### Unifi Controller

```env
UNIFI_HOST=https://192.168.1.1:8443
UNIFI_USERNAME=admin
UNIFI_PASSWORD=your_password
UNIFI_SITE=default
UNIFI_VERIFY_SSL=false
```

### Proxmox

Create an API token in Proxmox:
1. Go to Datacenter > Permissions > API Tokens
2. Add a new token for your user
3. Note the token ID and value

```env
PROXMOX_HOST=https://192.168.1.10:8006
PROXMOX_USER=root@pam
PROXMOX_TOKEN_NAME=dashboard
PROXMOX_TOKEN_VALUE=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
PROXMOX_NODE=pve
PROXMOX_VERIFY_SSL=false
```

### Plex

Get your Plex token:
1. Sign in to Plex Web App
2. Open any media item
3. Click "Get Info" > "View XML"
4. Look for `X-Plex-Token` in the URL

```env
PLEX_URL=http://192.168.1.20:32400
PLEX_TOKEN=your_plex_token
```

### Docker

For local Docker monitoring:
```env
DOCKER_HOST=
```

For remote Docker host:
```env
DOCKER_HOST=tcp://192.168.1.30:2375
```

### Google Calendar

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable the Google Calendar API
4. Create credentials (OAuth 2.0 or Service Account)
5. Download the credentials JSON file

For Service Account:
```env
GOOGLE_CREDENTIALS_PATH=/app/config/google_credentials.json
GOOGLE_CALENDAR_IDS=primary,family@group.calendar.google.com
```

Place your `google_credentials.json` in the `config/` directory.

## Deployment on Proxmox LXC

### Create LXC Container

```bash
# Create a new LXC container (Debian/Ubuntu)
pct create 200 local:vztmpl/debian-12-standard_12.0-1_amd64.tar.zst \
  --hostname homelab-dashboard \
  --memory 1024 \
  --cores 2 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --rootfs local-lvm:8 \
  --unprivileged 1 \
  --features nesting=1

# Start the container
pct start 200

# Enter the container
pct enter 200
```

### Install Dependencies

```bash
apt update && apt upgrade -y
apt install -y curl git docker.io docker-compose

# Enable Docker
systemctl enable docker
systemctl start docker
```

### Deploy Dashboard

```bash
# Clone or copy the project
cd /opt
git clone https://your-repo/homelab-dashboard.git
cd homelab-dashboard

# Configure
cp .env.example .env
nano .env  # Edit with your settings

# Create config directory for Google credentials
mkdir -p config
# Copy your google_credentials.json to config/

# Start the application
docker-compose up -d
```

### Auto-start on Boot

Docker Compose containers with `restart: unless-stopped` will automatically start when Docker starts.

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/dashboard` | Complete dashboard status |
| `GET /api/unifi` | Unifi controller status |
| `GET /api/proxmox` | Proxmox status |
| `GET /api/plex` | Plex recently added |
| `GET /api/docker` | Docker container status |
| `GET /api/calendar` | Calendar events |
| `POST /api/refresh` | Force refresh all data |
| `GET /api/health` | Health check |

## Project Structure

```
homelab-dashboard/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   └── schemas.py      # Pydantic models
│   │   ├── routers/
│   │   │   └── dashboard.py    # API routes
│   │   ├── services/
│   │   │   ├── cache.py        # Caching service
│   │   │   ├── unifi.py        # Unifi integration
│   │   │   ├── proxmox.py      # Proxmox integration
│   │   │   ├── plex.py         # Plex integration
│   │   │   ├── docker_service.py # Docker integration
│   │   │   └── calendar.py     # Google Calendar
│   │   ├── config.py           # Configuration
│   │   └── main.py             # FastAPI application
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.js
│   │   │   ├── StatusCard.js
│   │   │   ├── UnifiCard.js
│   │   │   ├── ProxmoxCard.js
│   │   │   ├── PlexCard.js
│   │   │   ├── DockerCard.js
│   │   │   └── CalendarCard.js
│   │   ├── hooks/
│   │   │   └── useDashboard.js
│   │   ├── styles/
│   │   │   └── index.css
│   │   ├── App.js
│   │   └── index.js
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── nginx/
│   └── dashboard.conf          # Reverse proxy config
├── config/                     # Config files (create this)
├── docker-compose.yml
├── .env.example
└── README.md
```

## Troubleshooting

### API Connection Issues

- Check CORS_ORIGINS includes your frontend URL
- Verify backend is running: `curl http://localhost:8000/api/health`
- Check Docker logs: `docker-compose logs backend`

### Unifi Authentication

- Ensure credentials are correct
- Try using IP instead of hostname
- Check if controller is using default port 8443

### Proxmox API Token

- Verify token has correct permissions (PVEAuditor role is sufficient)
- Check token format: `user@realm!tokenname=tokenvalue`

### Google Calendar

- Ensure credentials file is valid JSON
- For service accounts, share calendars with the service account email
- Check if Calendar API is enabled in Google Cloud Console

### Docker Socket

- Backend container needs access to Docker socket
- Check volume mount: `/var/run/docker.sock:/var/run/docker.sock:ro`

## Kiosk Mode Setup

For a dedicated kiosk display:

### Chromium Kiosk (Raspberry Pi / Linux)

```bash
# Install chromium
apt install chromium-browser

# Create autostart script
cat > /etc/xdg/autostart/dashboard.desktop << EOF
[Desktop Entry]
Type=Application
Name=Dashboard
Exec=chromium-browser --kiosk --noerrdialogs --disable-infobars http://localhost
EOF
```

### Disable Screen Blanking

```bash
# Add to /etc/xdg/lxsession/LXDE/autostart
@xset s off
@xset -dpms
@xset s noblank
```

## License

MIT License
