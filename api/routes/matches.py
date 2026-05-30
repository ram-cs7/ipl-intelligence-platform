from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Match, Season
from database import analytics

router = APIRouter(tags=["Matches & Seasons"])

# ── Seasons ──

@router.get("/seasons", summary="Season-by-season summary")
def season_summary():
    return analytics.season_summary()


@router.get("/seasons/{year}", summary="Matches in a specific season")
def season_detail(year: int, db: Session = Depends(get_db)):
    season = db.query(Season).filter(Season.year == year).first()
    if not season:
        raise HTTPException(404, f"Season {year} not found")
    matches = db.query(Match).filter(Match.season_id == season.id).all()
    return {
        "year": year,
        "total_matches": len(matches),
        "matches": [{"id": m.id, "date": str(m.match_date), "stage": m.stage,
                     "team1_id": m.team1_id, "team2_id": m.team2_id,
                     "team1_score": m.team1_score, "team2_score": m.team2_score,
                     "winner_id": m.winner_id} for m in matches]
    }


# ── Matches ──

@router.get("/matches", summary="List matches with optional filters")
def list_matches(
    season: int = Query(None, description="Filter by season year"),
    stage:  str = Query(None, description="league | qualifier | final"),
    limit:  int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    q = db.query(Match)
    if season:
        s = db.query(Season).filter(Season.year == season).first()
        if not s:
            raise HTTPException(404, f"Season {season} not found")
        q = q.filter(Match.season_id == s.id)
    if stage:
        q = q.filter(Match.stage == stage)
    matches = q.order_by(Match.match_date.desc()).limit(limit).all()
    return [{"id": m.id, "date": str(m.match_date), "stage": m.stage,
             "team1_id": m.team1_id, "team2_id": m.team2_id,
             "team1_score": m.team1_score, "team2_score": m.team2_score,
             "winner_id": m.winner_id, "venue_id": m.venue_id} for m in matches]


# ── Venues & Toss ──

@router.get("/venues", summary="Venue statistics")
def venue_stats():
    return analytics.venue_stats()


@router.get("/toss-impact", summary="Does winning the toss help?")
def toss_impact():
    return analytics.toss_impact()
