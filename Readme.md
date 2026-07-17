# GitScope

[![GitScope CI/CD Pipeline](https://github.com/imayank17/GitScope/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/imayank17/GitScope/actions/workflows/ci-cd.yml)

An analytics platform that transforms any public GitHub repository into actionable engineering insights. Paste a repository URL, and GitScope fetches, caches, and visualizes contributors, commits, issues, pull requests, language breakdowns, and historical metric trends — all in real time.

---

## Features

- **Instant Repository Analysis** — Enter any `owner/repo` or full GitHub URL and get a comprehensive breakdown in seconds.
- **Smart Caching & Background Sync** — Data is cached in PostgreSQL with a configurable TTL. Stale repositories are silently refreshed in the background without blocking the UI.
- **Interactive Dashboard** — A rich React frontend with charts for language distribution, contributor activity, commit timelines, and more.
- **Paginated API** — Every list endpoint supports `page` and `per_page` query parameters for clean pagination.
- **Manual Refresh** — Trigger on-demand re-sync of any tracked repository via the sync management page.
- **Historical Snapshots** — Each sync captures a point-in-time snapshot of repository metrics, enabling trend analysis over time.
- **Structured Logging** — UTC-timestamped, color-coded logs with domain-specific log files (app, GitHub, sync, error).
- **Fully Dockerized** — One command (`docker compose up`) boots the entire stack: database, backend, and frontend.
- **CI/CD Pipeline** — A unified GitHub Actions workflow runs linting, unit tests, E2E tests, Docker builds, and automated releases.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.12, FastAPI, SQLAlchemy 2.0 (Async), Pydantic v2 |
| **Database** | PostgreSQL 16 with `asyncpg` driver |
| **Frontend** | React 19, TypeScript, Vite, TailwindCSS v4, Recharts, Framer Motion |
| **State Management** | TanStack React Query v5 |
| **Testing** | Pytest (backend), Playwright (E2E — Chromium & Firefox) |
| **Containerization** | Docker, Docker Compose, Nginx |
| **CI/CD** | GitHub Actions (unified pipeline) |

---

## Project Structure

```
GitScope/
├── backend/
│   ├── app/
│   │   ├── core/              # Config, dependencies, logging
│   │   ├── database/          # SQLAlchemy engine, session, base
│   │   ├── models/            # ORM models (Repository, Contributor, Commit, etc.)
│   │   ├── repositories/      # Data-access layer (GitHub API + DB)
│   │   ├── routers/           # FastAPI route handlers
│   │   ├── schemas/           # Pydantic request/response models
│   │   ├── services/          # Business logic (sync, analytics, GitHub service)
│   │   └── main.py            # App entrypoint, lifespan, middleware
│   ├── tests/                 # Pytest suite (51 tests)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/               # Axios client configuration
│   │   ├── components/        # Reusable UI (charts, dashboard, layout, common)
│   │   ├── hooks/             # Custom React Query hooks
│   │   ├── layouts/           # Page layout wrappers
│   │   ├── pages/             # Route-level pages (Landing, Dashboard, etc.)
│   │   ├── routes/            # React Router configuration
│   │   ├── services/          # API service functions
│   │   └── types/             # TypeScript type definitions
│   ├── tests/                 # Playwright E2E tests (48 tests)
│   ├── Dockerfile
│   ├── nginx.conf
│   └── playwright.config.ts
├── .github/workflows/
│   └── ci-cd.yml              # Unified CI/CD pipeline
├── docker-compose.yml
└── Readme.md
```

---

## API Endpoints

### Health

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Application info (name, version, debug mode) |
| `GET` | `/health` | Health check |

### Repository Analysis

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/repositories/analyze` | Analyze a repository by URL or `owner/repo` format |
| `GET` | `/github/{owner}/{repo}` | Get repository details by owner and repo name |

### Repository Data (Paginated)

| Method | Endpoint | Query Params | Description |
|---|---|---|---|
| `GET` | `/repositories/{owner}/{repo}/contributors` | `page`, `per_page` | List contributors sorted by contributions |
| `GET` | `/repositories/{owner}/{repo}/commits` | `page`, `per_page` | List commits (most recent first) |
| `GET` | `/repositories/{owner}/{repo}/languages` | — | Language breakdown with byte counts and percentages |
| `GET` | `/repositories/{owner}/{repo}/pulls` | `state`, `page`, `per_page` | List pull requests (filter: `open`, `closed`, `all`) |
| `GET` | `/repositories/{owner}/{repo}/issues` | `state`, `page`, `per_page` | List issues (filter: `open`, `closed`, `all`) |

### Synchronization & Analytics

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/repositories/{id}/refresh` | Trigger a manual background refresh (returns `202 Accepted`) |
| `GET` | `/repositories/{id}/sync-status` | Check the current sync status of a repository |
| `GET` | `/repositories/{id}/metrics/history` | Fetch historical metric snapshots for trend analysis |

> **Interactive Docs**: Once the backend is running, explore all endpoints at [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI) or [http://localhost:8000/redoc](http://localhost:8000/redoc) (ReDoc).

---

## Getting Started

### Prerequisites

- **Python** 3.12+
- **Node.js** 20+
- **PostgreSQL** 16+
- **Docker** & **Docker Compose** (optional, for containerized setup)
- A **GitHub Personal Access Token** (optional, increases API rate limits from 60 to 5,000 requests/hour)

---

### Option 1: Docker Compose (Recommended)

The fastest way to get GitScope running — no local installs required beyond Docker.

**1. Clone the repository**

```bash
git clone https://github.com/imayank17/GitScope.git
cd GitScope
```

**2. Create the backend `.env` file**

```bash
cat > backend/.env << 'EOF'
APP_NAME=GitScope
APP_VERSION=1.0.0
DEBUG=True
DATABASE_URL=postgresql+asyncpg://mayank:postgres@db:5432/gitscope_db
SECRET_KEY=replace_this_with_a_long_random_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
GITHUB_TOKEN=your_github_personal_access_token
EOF
```

> Replace `your_github_personal_access_token` with a valid token. You can generate one at [github.com/settings/tokens](https://github.com/settings/tokens).

**3. Start the stack**

```bash
docker compose up --build
```

**4. Access the application**

| Service | URL |
|---|---|
| **Frontend** | [http://localhost:5173](http://localhost:5173) |
| **Backend API** | [http://localhost:8000](http://localhost:8000) |
| **Swagger Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) |

---

### Option 2: Local Development Setup

Run each service individually for a development workflow with hot-reloading.

#### Backend

**1. Navigate to the backend directory**

```bash
cd backend
```

**2. Create and activate a virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate      # Linux/macOS
# venv\Scripts\activate.bat   # Windows CMD
# venv\Scripts\Activate.ps1   # Windows PowerShell
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Create the `.env` file**

Create a `.env` file inside the `backend/` directory:

```env
APP_NAME=GitScope
APP_VERSION=1.0.0
DEBUG=True
DATABASE_URL=postgresql+asyncpg://your_user:your_password@localhost:5432/gitscope_db
SECRET_KEY=replace_this_with_a_long_random_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
GITHUB_TOKEN=your_github_personal_access_token
```

> Ensure PostgreSQL is running locally and the database `gitscope_db` exists. Create it with:
> ```bash
> createdb gitscope_db
> ```

**5. Start the development server**

```bash
uvicorn app.main:app --reload
```

The backend will be available at:
- **API**: [http://localhost:8000](http://localhost:8000)
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

#### Frontend

**1. Navigate to the frontend directory**

```bash
cd frontend
```

**2. Install dependencies**

```bash
npm install
```

**3. Start the dev server**

```bash
npm run dev
```

The frontend will be available at [http://localhost:5173](http://localhost:5173).

---

## Running Tests

### Backend Tests (Pytest)

```bash
cd backend
source venv/bin/activate
PYTHONPATH=. pytest -v
```

Runs 51 tests covering routers, services, repositories, health checks, and structured logging.

### End-to-End Tests (Playwright)

```bash
cd frontend
npx playwright install --with-deps   # First time only
npx playwright test
```

Runs 48 E2E tests across Chromium and Firefox covering landing page flows, dashboard rendering, navigation, responsive layouts, and sync management.

---

## Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `APP_NAME` | Yes | Application display name |
| `APP_VERSION` | Yes | Application version string |
| `DEBUG` | Yes | Enable debug mode (`True`/`False`) |
| `DATABASE_URL` | Yes | PostgreSQL async connection string |
| `SECRET_KEY` | Yes | Secret key for JWT signing |
| `ALGORITHM` | Yes | JWT hashing algorithm (e.g. `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Yes | Access token TTL in minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Yes | Refresh token TTL in days |
| `GITHUB_TOKEN` | No | GitHub PAT for higher API rate limits |
| `LOG_LEVEL` | No | Logging level (default: `INFO`) |
| `LOG_TO_FILE` | No | Write logs to files (default: `True`) |
| `LOG_DIRECTORY` | No | Log output directory (default: `logs`) |
| `SYNC_TTL_SECONDS` | No | Cache freshness duration in seconds (default: `3600`) |

---

## CI/CD Pipeline

The unified GitHub Actions workflow (`.github/workflows/ci-cd.yml`) runs the following connected jobs:

```
┌──────────────┐   ┌──────────────┐   ┌───────────────────┐   ┌────────────────────┐
│ Backend Lint │   │Backend Pytest│   │Frontend Lint+Build│   │ Docker Validate &  │
│  & Style     │   │              │   │                   │   │   Build Check      │
└──────┬───────┘   └──────┬───────┘   └────────┬──────────┘   └─────────┬──────────┘
       │                  │                     │                       │
       │                  └──────────┬──────────┘                       │
       │                             │                                  │
       │                  ┌──────────▼──────────┐                       │
       │                  │  Playwright E2E     │                       │
       │                  │  Tests              │                       │
       │                  └──────────┬──────────┘                       │
       │                             │                                  │
       │                  ┌──────────▼──────────┐              ┌───────▼────────┐
       │                  │  Generate GitHub    │              │ Publish to     │
       │                  │  Release (tags v*)  │              │ Docker Hub     │
       │                  └─────────────────────┘              │ (main branch)  │
       │                                                       └────────────────┘
```

- **On every push/PR**: Lint, test, build verification, and Docker validation run in parallel.
- **E2E tests** wait for backend tests and frontend build to pass.
- **Docker publish** runs only on merges to `main` after all checks pass.
- **GitHub Release** is created automatically when a `v*` tag is pushed.

---

## License

This project is open source and available under the [MIT License](LICENSE).