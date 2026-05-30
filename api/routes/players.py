from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Player
from database import analytics

router = APIRouter(prefix="/players", tags=["Players"])


@router.get("/top-batsmen", summary="Top run scorers")
def top_batsmen(limit: int = Query(15, ge=1, le=50)):
    return analytics.top_batsmen(limit)


@router.get("/top-bowlers", summary="Top wicket takers")
def top_bowlers(limit: int = Query(15, ge=1, le=50)):
    return analytics.top_bowlers(limit)


@router.get("/player-of-match", summary="Player of the Match leaders")
def potm(limit: int = Query(10, ge=1, le=30)):
    return analytics.player_of_match_leaders(limit)


@router.get("/{player_id}", summary="Single player profile")
def get_player(player_id: int, db: Session = Depends(get_db)):
    p = db.query(Player).filter(Player.id == player_id).first()
    if not p:
        raise HTTPException(404, f"Player {player_id} not found")
    return {"id": p.id, "name": p.name, "role": p.role,
            "nationality": p.nationality, "team_id": p.team_id}
