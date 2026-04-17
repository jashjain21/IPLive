# 🏏 IPLive — IPL Cricket Live Scores & Statistics Dashboard

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.3-000000?logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-8.1-4479A1?logo=mysql&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-33_passing-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)

## 🚀 Overview

IPLive is a full-stack web application that delivers real-time IPL (Indian Premier League) cricket scores, detailed match statistics, and player performance analytics. It ingests live match data, persists it in a normalized MySQL database, and serves it through a Flask-based web interface with server-rendered HTML templates.

The project demonstrates end-to-end backend engineering — from database schema design and connection pooling to a clean Repository pattern, typed data models, and a comprehensive test suite with 33 tests.

## ✨ Key Features

- **Live Score Dashboard** — Real-time match scores with current run rate, required run rate, active batsmen, and current bowler
- **Match Archive** — Browse completed matches with full scorecards, batting/bowling stats, and fall-of-wicket timelines
- **Ball-by-Ball Score Viewer** — Drill into any over of any match with per-ball commentary
- **Player Statistics Engine** — Search players by name/team, view career aggregates (runs, wickets, strike rate, economy, averages)
- **Leaderboard Awards** — Orange Cap (most runs), Purple Cap (most wickets), best economy, best strike rate computed from live data
- **Offline/Mock Mode** — Full application runs without external API dependencies using a `MockCricbuzz` data layer and database seed script

## 🧠 Technical Highlights

- **Repository Pattern** — All database access is encapsulated in `repository.py` with 11 well-typed query functions, keeping route handlers thin and testable
- **Connection Pooling** — `DatabaseManager` wraps `mysql.connector.pooling.MySQLConnectionPool` (pool_size=5) with Python context manager protocol (`__enter__`/`__exit__`) for automatic connection lifecycle management
- **Typed Data Models** — Python `dataclass` models (`Player`, `Match`, `BattingStat`, `BowlingStat`) with `__post_init__` validation that rejects negative stats and empty required fields
- **Enum-Based Constants** — `Team` enum and `Table` class eliminate magic strings across the codebase
- **Mock Data Layer** — `MockCricbuzz` class implements the same interface as the external `pycricbuzz` API, enabling full offline development and deterministic testing without network calls
- **Structured Error Handling** — Every repository function catches `mysql.connector.Error` and generic exceptions separately, logs with context, and returns safe defaults instead of crashing
- **Environment-Based Configuration** — Database credentials loaded via `python-dotenv` with sensible defaults, no hardcoded secrets in application code
- **Optional Caching** — Graceful `flask_caching` integration with `try/except ImportError` — app works with or without the caching dependency

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.8+ |
| Web Framework | Flask 2.3 |
| Database | MySQL 8.x |
| DB Connector | mysql-connector-python 8.1 |
| Templating | Jinja2 (via Flask) |
| Testing | pytest 7.4, pytest-flask, pytest-mock, unittest.mock |
| Config | python-dotenv |
| Production Server | Gunicorn 21.2 |
| Caching (optional) | flask_caching |

## 🏗 Architecture / How It Works

```
┌─────────────────────────────────────────────────────────┐
│                      Client (Browser)                   │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP
┌──────────────────────────▼──────────────────────────────┐
│                   Flask Routes (app.py)                  │
│  /  /archive/  /archive/match  /archive/score           │
│  /playerstats/  /playerstats/player                     │
└──────┬───────────────────────────────┬──────────────────┘
       │                               │
┌──────▼──────────┐          ┌─────────▼─────────┐
│  MockCricbuzz   │          │  repository.py    │
│  (mock_data.py) │          │  11 query funcs   │
│  Live score API │          │  Repository Layer │
│  replacement    │          └─────────┬─────────┘
└─────────────────┘                    │
                             ┌─────────▼─────────┐
                             │ DatabaseManager    │
                             │ (databases.py)     │
                             │ Connection Pooling │
                             └─────────┬─────────┘
                                       │
                             ┌─────────▼─────────┐
                             │   MySQL Database   │
                             │                    │
                             │  MATCHH   PLAYER   │
                             │  BATSMAN  BOWLER   │
                             │  WICKETS  SCORE    │
                             └────────────────────┘
```

**Data Flow:**
1. Flask routes receive HTTP requests and delegate to the repository layer
2. `repository.py` acquires a pooled connection via `DatabaseManager`, executes parameterized queries, maps results to dataclass models
3. `MockCricbuzz` provides match/scorecard/commentary data for the live dashboard (replaces external API in offline mode)
4. Jinja2 templates render the response HTML with match data, stats tables, and leaderboards

**Database Schema (6 tables):**
- `MATCHH` — Match metadata (teams, venue, date, result)
- `PLAYER` — Player profiles with aggregate career stats (13 columns)
- `BATSMAN` — Per-match batting stats (runs, strike rate, boundaries, fours, sixes)
- `BOWLER` — Per-match bowling stats (wickets, economy, average, strike rate)
- `WICKETS` — Fall-of-wicket records (dismissal type, over)
- `SCORE` — Ball-by-ball score state (batsmen, bowler, runs, RRR, CRR, commentary)

## ⚡ Getting Started

### Prerequisites

- Python 3.8+
- MySQL 8.x running locally
- Git

### Setup

```bash
# Clone the repository
git clone https://github.com/jashjain21/IPLive.git
cd IPLive

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create the MySQL database
mysql -u root -p -e "CREATE DATABASE scratch;"

# Configure environment variables (optional — defaults work for local dev)
echo "DB_HOST=localhost" > .env
echo "DB_USER=root" >> .env
echo "DB_PASSWORD=password" >> .env
echo "DB_NAME=scratch" >> .env

# Seed the database with sample IPL data (88 players, 5 matches)
python seed_data.py

# Run the application
python -m App.app
```

The app will be available at `http://localhost:5000`.

### Running Tests

```bash
pytest tests/ -v
```

### Production

```bash
gunicorn -w 4 -b 0.0.0.0:8000 App.app:app
```

## 📌 Example Usage

1. **Home Page (`/`)** — View the live/mock score dashboard showing current match state: runs, wickets, run rate, active batsmen, and bowler
2. **Match Archive (`/archive/`)** — Browse all completed matches; click any match to see full batting/bowling scorecards
3. **Ball-by-Ball (`/archive/score?id=M001`)** — Select a team and over number to view the exact game state at that point
4. **Player Stats (`/playerstats/`)** — Search for players by name or team; view Orange Cap, Purple Cap, and other leaderboard awards
5. **Player Profile (`/playerstats/player?id=CSK01`)** — View individual player career stats across all matches

## 🔍 What This Project Demonstrates

- **REST API Design** — 6 routes with GET/POST handling, query parameters, form data processing, and proper HTTP status codes (200, 400, 404, 500)
- **Relational Database Design** — Normalized 6-table MySQL schema with composite primary keys, foreign key relationships, and aggregate stat computation
- **Repository Pattern** — Clean separation between route handlers and data access, making the codebase testable and maintainable
- **Connection Pooling** — Production-grade database connection management using MySQL connection pools with context manager protocol
- **Data Modeling** — Python dataclasses with runtime validation via `__post_init__`
- **Test Engineering** — 33 tests across 3 test modules using pytest fixtures, `unittest.mock` for database mocking, and Flask test client for integration tests
- **Error Handling** — Granular exception handling with structured logging at every layer
- **Configuration Management** — Environment-based config with `python-dotenv`, no secrets in source code
- **Offline-First Design** — Mock data layer that mirrors the external API interface, enabling development and testing without network dependencies

## 🚧 Limitations / Future Improvements

- **No Live API Integration in Current Build** — The app uses `MockCricbuzz` with static data; reconnecting to a live cricket API (e.g., CricAPI, Cricbuzz) would enable real-time scores
- **No Authentication** — All routes are publicly accessible; adding Flask-Login or JWT auth would be needed for production
- **No Frontend Framework** — Server-rendered Jinja2 templates; migrating to React/Vue with a REST or GraphQL API would improve UX and enable real-time updates via WebSockets
- **No CI/CD Pipeline** — Adding GitHub Actions for automated testing, linting, and deployment would strengthen the project
- **No Database Migrations** — Schema is created via raw SQL in `seed_data.py`; adopting Flask-Migrate (Alembic) would enable versioned schema changes
- **SQL Injection Surface** — Some queries in `iplive.py` (legacy module) use string concatenation; the refactored `repository.py` uses parameterized queries throughout
- **No API Documentation** — Adding Swagger/OpenAPI docs would make the endpoints self-documenting
- **Caching Strategy** — The optional `flask_caching` integration exists but is not applied to all expensive queries
