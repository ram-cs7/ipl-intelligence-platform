from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
from ml.predictor import predict_match

router = APIRouter(prefix="/predict", tags=["ML Prediction"])

VALID_TEAMS = ["MI","CSK","KKR","RCB","SRH","DC","PBKS","RR","GT","LSG"]
VALID_VENUES = ["Mumbai","Chennai","Kolkata","Bangalore","Hyderabad",
                "Delhi","Mohali","Jaipur","Ahmedabad","Lucknow"]

class PredictRequest(BaseModel):
    team1:         str = Field(..., example="MI",    description="Team 1 short code")
    team2:         str = Field(..., example="CSK",   description="Team 2 short code")
    venue_city:    str = Field(..., example="Mumbai", description="Host city")
    toss_winner:   str = Field(..., example="MI",    description="Toss winner short code")
    toss_decision: Literal["bat","field"] = Field(..., example="bat")
    stage:         Literal["league","qualifier","final"] = Field("league")
    season_year:   int = Field(2024, ge=2008, le=2025)

class PredictResponse(BaseModel):
    team1: str
    team2: str
    team1_win_probability: float
    team2_win_probability: float
    predicted_winner: str
    confidence: float
    venue: str
    toss_winner: str
    toss_decision: str
    stage: str


@router.post("/match", response_model=PredictResponse,
             summary="Predict IPL match winner using ML model")
def predict(req: PredictRequest):
    for code in [req.team1, req.team2, req.toss_winner]:
        if code.upper() not in VALID_TEAMS:
            raise HTTPException(400, f"'{code}' not a valid team. Choose from: {VALID_TEAMS}")
    if req.team1 == req.team2:
        raise HTTPException(400, "team1 and team2 must be different")
    if req.venue_city not in VALID_VENUES:
        raise HTTPException(400, f"Invalid venue city. Choose from: {VALID_VENUES}")
    try:
        result = predict_match(
            team1=req.team1.upper(), team2=req.team2.upper(),
            venue_city=req.venue_city, toss_winner=req.toss_winner.upper(),
            toss_decision=req.toss_decision, stage=req.stage,
            season_year=req.season_year
        )
        return result
    except Exception as e:
        raise HTTPException(500, f"Prediction error: {str(e)}")


@router.get("/teams", summary="Valid team codes for prediction")
def valid_teams():
    return {"teams": VALID_TEAMS, "venues": VALID_VENUES}
