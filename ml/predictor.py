"""
IPL Match Win Predictor
- Features: team strengths, toss, venue, season form
- Model: RandomForestClassifier with cross-validation
- Outputs: win probability + feature importance
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
from database.database import execute_sql

MODEL_PATH = os.path.join(os.path.dirname(__file__), "win_predictor.pkl")
ENCODER_PATH = os.path.join(os.path.dirname(__file__), "encoders.pkl")


# ── Feature Engineering ────────────────────────────────────────────────────────

def build_feature_df() -> pd.DataFrame:
    query = """
        SELECT
            m.id                    AS match_id,
            m.season_id,
            s.year                  AS season_year,
            t1.short_name           AS team1,
            t2.short_name           AS team2,
            tw.short_name           AS toss_winner,
            m.toss_decision,
            v.city                  AS venue_city,
            m.team1_score,
            m.team2_score,
            m.stage,
            CASE WHEN m.winner_id = m.team1_id THEN 1 ELSE 0 END AS team1_won
        FROM matches m
        JOIN teams t1  ON t1.id = m.team1_id
        JOIN teams t2  ON t2.id = m.team2_id
        JOIN teams tw  ON tw.id = m.toss_winner_id
        JOIN venues v  ON v.id  = m.venue_id
        JOIN seasons s ON s.id  = m.season_id
        WHERE m.winner_id IS NOT NULL
    """
    rows = execute_sql(query)
    df = pd.DataFrame(rows)

    # Win-rate features per team (computed from raw data)
    wins_q = """
        SELECT t.short_name AS team, COUNT(*) AS wins
        FROM matches m JOIN teams t ON t.id = m.winner_id
        GROUP BY t.short_name
    """
    played_q = """
        SELECT short_name AS team,
               (SELECT COUNT(*) FROM matches WHERE team1_id=teams.id OR team2_id=teams.id) AS played
        FROM teams
    """
    wins_df   = pd.DataFrame(execute_sql(wins_q))
    played_df = pd.DataFrame(execute_sql(played_q))
    team_stats = played_df.merge(wins_df, on="team", how="left").fillna(0)
    team_stats["win_rate"] = team_stats["wins"] / team_stats["played"].replace(0, 1)
    wr = dict(zip(team_stats["team"], team_stats["win_rate"]))

    df["team1_win_rate"]  = df["team1"].map(wr).fillna(0.5)
    df["team2_win_rate"]  = df["team2"].map(wr).fillna(0.5)
    df["win_rate_diff"]   = df["team1_win_rate"] - df["team2_win_rate"]
    df["toss_is_team1"]   = (df["toss_winner"] == df["team1"]).astype(int)
    df["toss_chose_bat"]  = (df["toss_decision"] == "bat").astype(int)
    df["is_final"]        = (df["stage"] == "final").astype(int)
    df["is_qualifier"]    = (df["stage"] == "qualifier").astype(int)
    df["score_diff"]      = df["team1_score"] - df["team2_score"]

    return df


def encode_and_split(df: pd.DataFrame):
    le_team   = LabelEncoder().fit(list(set(df["team1"].tolist() + df["team2"].tolist())))
    le_venue  = LabelEncoder().fit(df["venue_city"])
    le_toss   = LabelEncoder().fit(df["toss_winner"])

    df["team1_enc"]  = le_team.transform(df["team1"])
    df["team2_enc"]  = le_team.transform(df["team2"])
    df["venue_enc"]  = le_venue.transform(df["venue_city"])
    df["toss_enc"]   = le_toss.transform(df["toss_winner"])

    feature_cols = [
        "team1_enc", "team2_enc", "venue_enc",
        "toss_is_team1", "toss_chose_bat",
        "team1_win_rate", "team2_win_rate", "win_rate_diff",
        "is_final", "is_qualifier", "season_year"
    ]
    X = df[feature_cols]
    y = df["team1_won"]

    encoders = {"team": le_team, "venue": le_venue, "toss": le_toss, "features": feature_cols}
    return X, y, encoders


# ── Training ──────────────────────────────────────────────────────────────────

def train():
    print("🔧 Building feature matrix...")
    df = build_feature_df()
    X, y, encoders = encode_and_split(df)

    print(f"   Dataset: {len(X)} matches  |  Features: {X.shape[1]}")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(
        n_estimators=200, max_depth=8, min_samples_leaf=5,
        class_weight="balanced", random_state=42, n_jobs=-1
    )
    model.fit(X_train, y_train)

    # Cross-validation
    cv_scores = cross_val_score(model, X, y, cv=5, scoring="accuracy")
    y_pred    = model.predict(X_test)
    acc       = accuracy_score(y_test, y_pred)

    print(f"\n📊 Model Performance:")
    print(f"   Test Accuracy  : {acc:.4f}")
    print(f"   CV Accuracy    : {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    print(f"\n{classification_report(y_test, y_pred, target_names=['Team2 Wins','Team1 Wins'])}")

    # Feature importance
    fi = pd.Series(model.feature_importances_, index=encoders["features"]).sort_values(ascending=False)
    print("🔑 Feature Importances:")
    for feat, imp in fi.items():
        print(f"   {feat:<25} {imp:.4f}")

    joblib.dump(model, MODEL_PATH)
    joblib.dump(encoders, ENCODER_PATH)
    print(f"\n✅ Model saved → {MODEL_PATH}")
    return model, encoders, acc, cv_scores.mean()


# ── Inference ─────────────────────────────────────────────────────────────────

def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model not trained yet. Run ml/predictor.py first.")
    model    = joblib.load(MODEL_PATH)
    encoders = joblib.load(ENCODER_PATH)
    return model, encoders


def predict_match(team1: str, team2: str, venue_city: str,
                  toss_winner: str, toss_decision: str,
                  stage: str = "league", season_year: int = 2024):
    model, encoders = load_model()

    # Win-rate lookup from DB
    wr_q = """
        SELECT t.short_name AS team,
               CAST(COUNT(CASE WHEN m.winner_id = t.id THEN 1 END) AS FLOAT) /
               CAST(COUNT(*) AS FLOAT) AS win_rate
        FROM teams t
        LEFT JOIN matches m ON (m.team1_id = t.id OR m.team2_id = t.id)
        GROUP BY t.short_name
    """
    wr_rows = execute_sql(wr_q)
    wr = {r["team"]: r["win_rate"] for r in wr_rows}

    t1_wr = wr.get(team1, 0.5)
    t2_wr = wr.get(team2, 0.5)

    try:
        t1_enc = encoders["team"].transform([team1])[0]
        t2_enc = encoders["team"].transform([team2])[0]
        v_enc  = encoders["venue"].transform([venue_city])[0]
    except ValueError as e:
        raise ValueError(f"Unknown value: {e}. Valid teams: {list(encoders['team'].classes_)}")

    features = pd.DataFrame([{
        "team1_enc":       t1_enc,
        "team2_enc":       t2_enc,
        "venue_enc":       v_enc,
        "toss_is_team1":   int(toss_winner == team1),
        "toss_chose_bat":  int(toss_decision == "bat"),
        "team1_win_rate":  t1_wr,
        "team2_win_rate":  t2_wr,
        "win_rate_diff":   t1_wr - t2_wr,
        "is_final":        int(stage == "final"),
        "is_qualifier":    int(stage == "qualifier"),
        "season_year":     season_year,
    }])

    proba = model.predict_proba(features[encoders["features"]])[0]
    return {
        "team1": team1, "team2": team2,
        "team1_win_probability": round(float(proba[1]) * 100, 1),
        "team2_win_probability": round(float(proba[0]) * 100, 1),
        "predicted_winner": team1 if proba[1] > 0.5 else team2,
        "confidence": round(float(max(proba)) * 100, 1),
        "venue": venue_city, "toss_winner": toss_winner,
        "toss_decision": toss_decision, "stage": stage,
    }


if __name__ == "__main__":
    train()
