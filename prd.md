# PRD.md — HomeLab Dashboard Evolution

## 1. Product Goal

HomeLab Dashboard is a self-hosted monitoring dashboard for homelab environments.  
Its purpose is to present clear, high-signal status information for core services with minimal interaction.

Primary services:
- UniFi
- Proxmox
- Plex
- Docker
- Optional: Calendar, Weather, News

---

## 2. Roadmap (Strict Order)

Claude Code must work on one item at a time.  
Do not proceed to the next item until the current one is complete, tested, and documented in SUMMARY.md.

| Priority | Feature | Description |
|---------|--------|-------------|
| 1 | Web-based Setup Wizard | Configure services via UI instead of editing `.env` |
| 2 | Service Toggles | Enable/disable service cards dynamically |
| 3 | Theme Support | Light/Dark mode and accent color |
| 4 | Mobile Responsive | Support phones and tablets |
| 5 | Docker Hub Images | Pre-built images and CI pipeline |

---

## 3. Feature Requirements

### 3.1 Web-based Setup Wizard

Goal:  
Allow users to configure service credentials through a secure UI.

Requirements:
- UI-based configuration flow
- Credential validation before saving
- Works with Docker Compose
- Existing `.env` support must continue to work

Done when:
- Dashboard runs without a pre-filled `.env`
- Services begin polling after setup
- Configuration persists across restarts

---

### 3.2 Service Toggles

Goal:  
Let users show or hide service cards without code changes.

Requirements:
- Settings UI with per-service toggles
- Disabled services are not polled
- Layout updates automatically

Done when:
- Toggling a service immediately hides/shows its card
- Disabled services produce no backend activity

---

### 3.3 Theme Support

Goal:  
Allow visual customization without breaking layout.

Requirements:
- Light/Dark mode toggle
- Configurable accent color
- Use CSS variables only

Done when:
- Theme changes apply instantly
- Status colors remain consistent

---

### 3.4 Mobile Responsive

Goal:  
Support smaller screens while keeping desktop behavior unchanged.

Requirements:
- Responsive breakpoints
- Vertical scrolling allowed on small screens only
- No horizontal scrolling

Done when:
- Dashboard is usable on phones and tablets
- Desktop layout remains unchanged

---

### 3.5 Docker Hub Images

Goal:  
Make deployment easier with pre-built images.

Requirements:
- CI pipeline
- Versioned images
- Clear documentation

Done when:
- Users can deploy without building locally

---

## 4. Mandatory Developer Workflow (Strict)

### Phase 1: Planning (Required)

Claude Code MUST use the ask_user_questions tool before writing any code.

This step is mandatory and non-optional.

Questions must clarify:
- UX expectations
- Storage approach
- Security assumptions
- Any ambiguity in requirements

No implementation may begin until questions are answered.

---

### Phase 2: Implementation & Testing

- Backend: FastAPI (Python 3.11)
- Frontend: React 18
- Must work with existing docker-compose.yml
- Must not break existing services or status enums
- Run or create tests as needed
- Be mindful of the known Docker service connection issue

---

### Phase 3: Documentation (Required)

After each feature:
- Update SUMMARY.md with:
  - Description of the change
  - Test results
  - Date of completion (January 21, 2026)

---

## 5. Technical Constraints

Layout:
- Primary dashboard must use:
  height: 100vh;
  overflow: hidden;
- Internal card scrolling is allowed
- Page-level scrolling is not (except on mobile)

Styling:
- Use CSS variable:
  --spacing-unit: 20px;
- Status enums must remain:
  HEALTHY
  WARNING
  ERROR
  UNKNOWN

---

## 6. Success Criteria

This PRD is successful when:
- Users can configure the dashboard without editing files
- Services can be enabled or disabled dynamically
- Visual changes do not affect stability
- Changes are incremental, documented, and reversible

