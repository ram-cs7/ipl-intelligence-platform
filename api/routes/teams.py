from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Team
from database import analytics

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get("/", summary="List all IPL teams")
def list_teams(db: Session = Depends(get_db)):
    teams = db.query(Team).order_by(Team.name).all()
    return [{"id": t.id, "name": t.name, "short_name": t.short_name,
             "city": t.home_city, "titles": t.titles} for t in teams]


@router.get("/win-rates", summary="Win rates for all teams")
def win_rates(min_matches: int = Query(10, ge=1)):
    return analytics.team_win_rates(min_matches)


@router.get("/head-to-head", summary="Head-to-head between two teams")
def h2h(team1: str = Query(..., example="MI"), team2: str = Query(..., example="CSK")):
    result = analytics.head_to_head(team1.upper(), team2.upper())
    if not result:
        raise HTTPException(404, f"No matches found between {team1} and {team2}")
    return result


@router.get("/season-wins-heatmap", summary="Wins per team per season (heatmap data)")
def heatmap():
    return analytics.season_wins_by_team()


@router.get("/{short_name}", summary="Single team details")
def get_team(short_name: str, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.short_name == short_name.upper()).first()
    if not team:
        raise HTTPException(404, f"Team '{short_name}' not found")
    return {"id": team.id, "name": team.name, "short_name": team.short_name,
            "city": team.home_city, "titles": team.titles}
