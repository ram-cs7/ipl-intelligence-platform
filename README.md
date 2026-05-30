# 🏏 IPL Intelligence Platform

> Full-stack AI/ML sports analytics system — FastAPI · SQLAlchemy · SQLite · RandomForest · Plotly · Streamlit · Docker

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)](https://fastapi.tiangolo.com)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.5-orange)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 📌 What This Project Demonstrates

| Skill Area | What's Shown |
|---|---|
| **Backend / SDE** | FastAPI REST API, SQLAlchemy ORM, SQLite, Docker, Pydantic validation, modular architecture |
| **Data Science** | SQL aggregations, CTEs, GROUP BY analytics, Pandas, statistical analysis, Plotly visualisation |
| **AI / ML** | RandomForest classifier, feature engineering, cross-validation, joblib model serving |
| **Project Management** | Modular repo structure, documented API (Swagger), seed scripts, Dockerfile, clear README |

---

## 🏗 Architecture

```
ipl-intelligence-platform/
├── main.py                    # FastAPI application entrypoint
├── requirements.txt
├── Dockerfile
├── database/
│   ├── models.py              # SQLAlchemy ORM models (Team, Match, Player, etc.)
│   ├── database.py            # Engine, session, raw SQL executor
│   └── analytics.py           # All SQL analytics queries
├── api/
│   └── routes/
│       ├── teams.py           # /teams/* endpoints
│       ├── players.py         # /players/* endpoints
│       ├── matches.py         # /matches, /seasons, /venues, /toss-impact
│       └── predict.py         # POST /predict/match (ML)
├── ml/
│   └── predictor.py           # Feature engineering, train, inference
├── data/
│   └── seed_data.py           # Generates 17 seasons × 600+ matches
└── dashboard/
    └── app.py                 # Streamlit analytics dashboard (6 pages)
```

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/ram-cs7/ipl-intelligence-platform
cd ipl-intelligence-platform
pip install -r requirements.txt
```

### 2. Seed Database & Train Model
```bash
python data/seed_data.py        # Creates ipl.db with 600+ IPL matches (2008–2024)
python ml/predictor.py          # Trains RandomForest; saves model to ml/win_predictor.pkl
```

### 3. Run the API
```bash
uvicorn main:app --reload --port 8000
# Swagger UI: http://localhost:8000/docs
```

### 4. Run the Dashboard
```bash
streamlit run dashboard/app.py
# Opens: http://localhost:8501
```

### 5. Docker
```bash
docker build -t ipl-platform .
docker run -p 8000:8000 ipl-platform
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/teams/` | All IPL teams |
| GET | `/teams/win-rates` | Win rate analytics (SQL aggregation) |
| GET | `/teams/head-to-head?team1=MI&team2=CSK` | H2H stats |
| GET | `/teams/season-wins-heatmap` | Wins × season × team |
| GET | `/seasons` | Season-by-season summaries |
| GET | `/seasons/{year}` | Season detail |
| GET | `/matches?season=2023&stage=final` | Filterable match list |
| GET | `/venues` | Venue analytics |
| GET | `/toss-impact` | Toss → win correlation |
| GET | `/players/top-batsmen` | Top run scorers |
| GET | `/players/top-bowlers` | Top wicket takers |
| GET | `/players/player-of-match` | POTM leaderboard |
| POST | `/predict/match` | **ML win probability prediction** |

---

## 🤖 ML Model

**Algorithm:** Random Forest Classifier (200 trees, max_depth=8)

**Features engineered:**
- Historical team win rates (computed via SQL)
- Win rate differential (team1 vs team2)
- Toss winner + decision
- Venue city (encoded)
- Match stage (league / qualifier / final)
- Season year (trend feature)

**Performance:** ~56% test accuracy, 52–56% 5-fold CV accuracy  
*(Fair for IPL — the sport is inherently high-variance)*

**Sample prediction request:**
```json
POST /predict/match
{
  "team1": "MI",
  "team2": "CSK",
  "venue_city": "Mumbai",
  "toss_winner": "MI",
  "toss_decision": "bat",
  "stage": "final",
  "season_year": 2024
}
```
**Response:**
```json
{
  "team1": "MI",
  "team2": "CSK",
  "team1_win_probability": 58.3,
  "team2_win_probability": 41.7,
  "predicted_winner": "MI",
  "confidence": 58.3
}
```

---

## 📊 Key SQL Analytics (from `database/analytics.py`)

```sql
-- Win rate per team
SELECT t.name, ROUND(100.0 * SUM(CASE WHEN m.winner_id = t.id THEN 1 ELSE 0 END) / COUNT(*), 2) AS win_pct
FROM teams t JOIN matches m ON (m.team1_id = t.id OR m.team2_id = t.id)
GROUP BY t.id ORDER BY win_pct DESC;

-- Toss impact analysis
SELECT toss_decision,
       ROUND(100.0 * SUM(CASE WHEN toss_winner_id = winner_id THEN 1 ELSE 0 END) / COUNT(*), 2) AS win_pct
FROM matches GROUP BY toss_decision;

-- Top batsmen with strike rate
SELECT p.name, SUM(b.runs) AS total_runs, ROUND(AVG(b.strike_rate), 1) AS avg_sr
FROM batting_stats b JOIN players p ON p.id = b.player_id
GROUP BY p.id HAVING total_runs > 100 ORDER BY total_runs DESC LIMIT 15;
```

---

## 📈 Dashboard Pages

1. **Overview** — KPIs, team win rate bar chart, scoring trends, toss analysis
2. **Team Analytics** — Win rate table, season wins heatmap, H2H lookup
3. **Player Stats** — Batsmen leaderboard, bowler scatter (wickets vs economy), POTM awards
4. **Season Trends** — Scoring trends 2008–2024, champions table
5. **Match Predictor** — Interactive ML prediction UI with probability bar chart
6. **SQL Explorer** — Live SQL query runner with preset queries

---

## 🔧 Tech Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI 0.111 |
| ORM | SQLAlchemy 2.0 |
| Database | SQLite |
| ML | Scikit-learn (RandomForest), Pandas, NumPy, Joblib |
| Visualisation | Plotly 5.x |
| Dashboard | Streamlit 1.36 |
| Containerisation | Docker |
| API Docs | Swagger UI (auto-generated) |

---

## 👤 Author

**Sairam Chennaka** — AI/ML Researcher · WACV 2026 Author · JRF at IHub-Data, IIIT Hyderabad

[GitHub](https://github.com/ram-cs7) · [LinkedIn](https://linkedin.com/in/sairam-chennaka) · [Portfolio](http://sairamroyal.netlify.app)
