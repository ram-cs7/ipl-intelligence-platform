"""
IPL Intelligence Platform — FastAPI Backend
===========================================
Endpoints:
  GET  /teams/                        List all teams
  GET  /teams/win-rates               Win rate analytics (SQL aggregation)
  GET  /teams/head-to-head            H2H stats
  GET  /teams/season-wins-heatmap     Wins per team per season
  GET  /seasons                       Season summaries
  GET  /seasons/{year}                Season detail
  GET  /matches                       Match list (filterable)
  GET  /venues                        Venue analytics
  GET  /toss-impact                   Toss win correlation
  GET  /players/top-batsmen           Top run scorers
  GET  /players/top-bowlers           Top wicket takers
  GET  /players/player-of-match       POTM leaders
  POST /predict/match                 ML win probability prediction

Run:  uvicorn main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.database import init_db
from api.routes import teams, players, matches, predict

app = FastAPI(
    title="🏏 IPL Intelligence Platform",
    description=(
        "Full-stack sports analytics API for Indian Premier League (2008–2024). "
        "Built with FastAPI, SQLAlchemy, SQLite, Pandas, and RandomForest ML. "
        "Demonstrates end-to-end data engineering, SQL analytics, REST API design, "
        "and ML-powered prediction."
    ),
    version="1.0.0",
    contact={"name": "Sairam Chennaka", "url": "https://github.com/ram-cs7"},
    license_info={"name": "MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── DB init on startup ──
@app.on_event("startup")
def startup():
    init_db()

# ── Register routers ──
app.include_router(teams.router)
app.include_router(players.router)
app.include_router(matches.router)
app.include_router(predict.router)

# ── Health check ──
@app.get("/", tags=["Health"])
def root():
    return {
        "service": "IPL Intelligence Platform",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
        "github": "https://github.com/ram-cs7/ipl-intelligence-platform",
    }

@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
