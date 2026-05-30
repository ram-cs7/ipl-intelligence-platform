"""
Generates and seeds realistic IPL data (2008-2024) into SQLite.
Run: python data/seed_data.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import random
import numpy as np
from datetime import date, timedelta
from database.database import SessionLocal, init_db
from database.models import Team, Venue, Season, Player, Match, BattingStat, BowlingStat

random.seed(42)
np.random.seed(42)

# ── Master data ───────────────────────────────────────────────────────────────

TEAMS = [
    {"name": "Mumbai Indians",           "short": "MI",   "city": "Mumbai",    "titles": 5},
    {"name": "Chennai Super Kings",      "short": "CSK",  "city": "Chennai",   "titles": 5},
    {"name": "Kolkata Knight Riders",    "short": "KKR",  "city": "Kolkata",   "titles": 3},
    {"name": "Royal Challengers Bangalore","short":"RCB", "city": "Bangalore", "titles": 0},
    {"name": "Sunrisers Hyderabad",      "short": "SRH",  "city": "Hyderabad", "titles": 1},
    {"name": "Delhi Capitals",           "short": "DC",   "city": "Delhi",     "titles": 0},
    {"name": "Punjab Kings",             "short": "PBKS", "city": "Mohali",    "titles": 0},
    {"name": "Rajasthan Royals",         "short": "RR",   "city": "Jaipur",    "titles": 2},
    {"name": "Gujarat Titans",           "short": "GT",   "city": "Ahmedabad", "titles": 1},
    {"name": "Lucknow Super Giants",     "short": "LSG",  "city": "Lucknow",   "titles": 0},
]

VENUES = [
    {"name": "Wankhede Stadium",            "city": "Mumbai",    "capacity": 33108},
    {"name": "M.A. Chidambaram Stadium",    "city": "Chennai",   "capacity": 50000},
    {"name": "Eden Gardens",                "city": "Kolkata",   "capacity": 66000},
    {"name": "M. Chinnaswamy Stadium",      "city": "Bangalore", "capacity": 40000},
    {"name": "Rajiv Gandhi Int. Stadium",   "city": "Hyderabad", "capacity": 55000},
    {"name": "Arun Jaitley Stadium",        "city": "Delhi",     "capacity": 41842},
    {"name": "IS Bindra Stadium",           "city": "Mohali",    "capacity": 27000},
    {"name": "Sawai Mansingh Stadium",      "city": "Jaipur",    "capacity": 30000},
    {"name": "Narendra Modi Stadium",       "city": "Ahmedabad", "capacity": 132000},
    {"name": "BRSABV Ekana Cricket Stadium","city": "Lucknow",   "capacity": 50000},
]

# IPL-style player pool (role: Batsman/Bowler/All-Rounder/WK-Batsman)
PLAYER_TEMPLATES = {
    "MI":   [("Rohit Sharma","Batsman"),("Hardik Pandya","All-Rounder"),("Jasprit Bumrah","Bowler"),
             ("Suryakumar Yadav","Batsman"),("Ishan Kishan","WK-Batsman"),("Kieron Pollard","All-Rounder"),
             ("Trent Boult","Bowler"),("Krunal Pandya","All-Rounder"),("Quinton de Kock","WK-Batsman"),
             ("Tim David","Batsman"),("Tilak Varma","Batsman"),("Jason Behrendorff","Bowler")],
    "CSK":  [("MS Dhoni","WK-Batsman"),("Ruturaj Gaikwad","Batsman"),("Devon Conway","WK-Batsman"),
             ("Shivam Dube","All-Rounder"),("Ravindra Jadeja","All-Rounder"),("Deepak Chahar","Bowler"),
             ("Tushar Deshpande","Bowler"),("Moeen Ali","All-Rounder"),("Ambati Rayudu","Batsman"),
             ("Mitchell Santner","All-Rounder"),("Faf du Plessis","Batsman"),("Shardul Thakur","All-Rounder")],
    "KKR":  [("Shreyas Iyer","Batsman"),("Venkatesh Iyer","All-Rounder"),("Andre Russell","All-Rounder"),
             ("Sunil Narine","All-Rounder"),("Pat Cummins","All-Rounder"),("Varun Chakravarthy","Bowler"),
             ("Nitish Rana","Batsman"),("Rinku Singh","Batsman"),("Phil Salt","WK-Batsman"),
             ("Angkrish Raghuvanshi","Batsman"),("Mitchell Starc","Bowler"),("Harshit Rana","Bowler")],
    "RCB":  [("Virat Kohli","Batsman"),("Faf du Plessis","Batsman"),("Glenn Maxwell","All-Rounder"),
             ("Mohammed Siraj","Bowler"),("Dinesh Karthik","WK-Batsman"),("Harshal Patel","Bowler"),
             ("Wanindu Hasaranga","All-Rounder"),("Rajat Patidar","Batsman"),("Shahbaz Ahmed","All-Rounder"),
             ("Suyash Prabhudessai","Batsman"),("Josh Hazlewood","Bowler"),("Cameron Green","All-Rounder")],
    "SRH":  [("Heinrich Klaasen","WK-Batsman"),("Pat Cummins","All-Rounder"),("Travis Head","Batsman"),
             ("Abhishek Sharma","Batsman"),("Mayank Agarwal","Batsman"),("Bhuvneshwar Kumar","Bowler"),
             ("T Natarajan","Bowler"),("Washington Sundar","All-Rounder"),("Aiden Markram","Batsman"),
             ("Nitish Reddy","All-Rounder"),("Marco Jansen","All-Rounder"),("Shahbaz Ahmed","All-Rounder")],
    "DC":   [("David Warner","Batsman"),("Rishabh Pant","WK-Batsman"),("Axar Patel","All-Rounder"),
             ("Anrich Nortje","Bowler"),("Prithvi Shaw","Batsman"),("Mitchell Marsh","All-Rounder"),
             ("Kuldeep Yadav","Bowler"),("Rovman Powell","Batsman"),("Jake Fraser-McGurk","Batsman"),
             ("Tristan Stubbs","Batsman"),("Ishant Sharma","Bowler"),("Khaleel Ahmed","Bowler")],
    "PBKS": [("Shikhar Dhawan","Batsman"),("Jonny Bairstow","WK-Batsman"),("Liam Livingstone","All-Rounder"),
             ("Kagiso Rabada","Bowler"),("Arshdeep Singh","Bowler"),("Sam Curran","All-Rounder"),
             ("Shahrukh Khan","Batsman"),("Harpreet Brar","All-Rounder"),("Jitesh Sharma","WK-Batsman"),
             ("Rahul Chahar","Bowler"),("Matthew Short","Batsman"),("Harshal Patel","Bowler")],
    "RR":   [("Sanju Samson","WK-Batsman"),("Jos Buttler","WK-Batsman"),("Yashasvi Jaiswal","Batsman"),
             ("Trent Boult","Bowler"),("Ravichandran Ashwin","All-Rounder"),("Shimron Hetmyer","Batsman"),
             ("Devdutt Padikkal","Batsman"),("Yuzvendra Chahal","Bowler"),("Riyan Parag","All-Rounder"),
             ("Dhruv Jurel","WK-Batsman"),("Jason Holder","All-Rounder"),("Navdeep Saini","Bowler")],
    "GT":   [("Shubman Gill","Batsman"),("Hardik Pandya","All-Rounder"),("Mohammed Shami","Bowler"),
             ("David Miller","Batsman"),("Rashid Khan","All-Rounder"),("Wriddhiman Saha","WK-Batsman"),
             ("Abhinav Manohar","Batsman"),("Noor Ahmad","Bowler"),("Vijay Shankar","All-Rounder"),
             ("Darshan Nalkande","Bowler"),("Azmatullah Omarzai","All-Rounder"),("B Sai Sudharsan","Batsman")],
    "LSG":  [("KL Rahul","WK-Batsman"),("Quinton de Kock","WK-Batsman"),("Marcus Stoinis","All-Rounder"),
             ("Krunal Pandya","All-Rounder"),("Avesh Khan","Bowler"),("Ravi Bishnoi","Bowler"),
             ("Deepak Hooda","All-Rounder"),("Manan Vohra","Batsman"),("Kyle Mayers","All-Rounder"),
             ("Ayush Badoni","Batsman"),("Mark Wood","Bowler"),("Nicholas Pooran","WK-Batsman")],
}

# IPL season winners (historical + projected)
SEASON_WINNERS = {
    2008:"RR", 2009:"DC", 2010:"CSK", 2011:"CSK", 2012:"KKR", 2013:"MI",
    2014:"KKR", 2015:"MI", 2016:"SRH", 2017:"MI", 2018:"CSK", 2019:"MI",
    2020:"MI", 2021:"CSK", 2022:"GT",  2023:"CSK", 2024:"KKR",
}


def generate_score():
    return int(np.random.normal(165, 20))


def generate_batting_stats(player_id, team_id, match_id, role, is_top_order):
    runs = 0
    balls = 0
    if role in ("Batsman", "WK-Batsman", "All-Rounder"):
        if is_top_order:
            runs = max(0, int(np.random.normal(38, 28)))
        else:
            runs = max(0, int(np.random.normal(18, 15)))
        balls = max(1, int(runs / (np.random.uniform(1.1, 1.7))))
    fours = min(runs // 8, int(np.random.poisson(3)))
    sixes = min(runs // 12, int(np.random.poisson(1.5)))
    sr = round((runs / balls) * 100, 2) if balls > 0 else 0
    return {"player_id": player_id, "team_id": team_id, "match_id": match_id,
            "runs": runs, "balls": balls, "fours": fours, "sixes": sixes,
            "strike_rate": sr, "dismissed": random.random() > 0.15}


def generate_bowling_stats(player_id, team_id, match_id, role):
    if role not in ("Bowler", "All-Rounder"):
        return None
    overs = round(random.choice([2.0, 3.0, 3.1, 4.0]), 1)
    wickets = int(np.random.choice([0, 1, 2, 3, 4], p=[0.40, 0.30, 0.18, 0.09, 0.03]))
    runs_conceded = int(overs * np.random.uniform(7.5, 10.5))
    eco = round(runs_conceded / overs, 2) if overs > 0 else 0
    return {"player_id": player_id, "team_id": team_id, "match_id": match_id,
            "overs": overs, "wickets": wickets, "runs_conceded": runs_conceded,
            "economy": eco, "maidens": 1 if eco < 7 and random.random() > 0.8 else 0}


def seed():
    init_db()
    db = SessionLocal()

    print("⚡ Seeding teams...")
    team_objs = {}
    for t in TEAMS:
        obj = Team(name=t["name"], short_name=t["short"], home_city=t["city"], titles=t["titles"])
        db.add(obj)
    db.commit()
    for t in db.query(Team).all():
        team_objs[t.short_name] = t

    print("⚡ Seeding venues...")
    venue_objs = []
    for v in VENUES:
        obj = Venue(name=v["name"], city=v["city"], capacity=v["capacity"])
        db.add(obj)
    db.commit()
    venue_objs = db.query(Venue).all()

    print("⚡ Seeding players...")
    player_objs = {}  # short_name -> [Player]
    for short, players in PLAYER_TEMPLATES.items():
        team = team_objs[short]
        player_objs[short] = []
        for pname, prole in players:
            nat = "Indian" if not any(x in pname for x in ["Kieron","Trent","Tim","Devon","Moeen",
                "Mitchell","Andre","Sunil","Pat","Phil","Faf","Glenn","Josh","Cameron","Heinrich",
                "Travis","Aiden","Marco","David W","Anrich","Liam","Jonny","Kagiso","Sam C",
                "Jos","Matthew","Jason H","Shimron","Trent B","Navdeep","David M","Rashid",
                "Wriddhiman","Noor","Azmatullah","Quinton","Marcus","Kyle","Mark W","Nicholas"]) else "Overseas"
            p = Player(name=pname, team_id=team.id, role=prole, nationality=nat)
            db.add(p)
            player_objs[short].append(p)
    db.commit()

    print("⚡ Seeding seasons, matches, and player stats...")
    all_shorts = list(team_objs.keys())

    for year in range(2008, 2025):
        winner_short = SEASON_WINNERS.get(year, random.choice(all_shorts))
        winner_team = team_objs[winner_short]
        season_obj = Season(year=year, winner_id=winner_team.id)
        db.add(season_obj)
        db.commit()

        # active teams (GT and LSG joined in 2022)
        active = all_shorts if year >= 2022 else [s for s in all_shorts if s not in ("GT", "LSG")]
        n_teams = len(active)
        n_matches = (n_teams * (n_teams - 1)) // 2 + 4  # round-robin + playoffs

        season_start = date(year, 3, 25)
        match_dates = [season_start + timedelta(days=i * 2) for i in range(n_matches)]

        pairs = [(active[i], active[j]) for i in range(n_teams) for j in range(i+1, n_teams)]
        random.shuffle(pairs)
        match_pairs = pairs[:n_matches - 4] + [(random.choice(active), random.choice(active)) for _ in range(4)]

        for idx, (s1, s2) in enumerate(match_pairs):
            if s1 == s2:
                candidates = [s for s in active if s != s1]
                s2 = random.choice(candidates)

            t1 = team_objs[s1]
            t2 = team_objs[s2]

            # Toss
            toss_winner = random.choice([t1, t2])
            toss_decision = random.choice(["bat", "field"])

            # Scores
            t1_score = generate_score()
            t2_score = generate_score()
            while t1_score == t2_score:
                t2_score = generate_score()

            # Winner determination (home team slight edge + winner_short boost)
            if s1 == winner_short:
                win_prob_t1 = 0.62
            elif s2 == winner_short:
                win_prob_t1 = 0.38
            else:
                win_prob_t1 = 0.50
            winner = t1 if random.random() < win_prob_t1 else t2
            loser = t2 if winner == t1 else t1

            win_by_runs = abs(t1_score - t2_score) if winner == t1 else 0
            win_by_wickets = random.randint(1, 7) if winner == t2 else 0

            stage = "final" if idx >= n_matches - 1 else ("qualifier" if idx >= n_matches - 4 else "league")

            # Player of match from winning team
            w_short = s1 if winner == t1 else s2
            potm = random.choice(player_objs[w_short])

            venue = random.choice([v for v in venue_objs if v.city in (t1.home_city, t2.home_city)] or venue_objs)

            match = Match(
                season_id=season_obj.id,
                match_date=match_dates[min(idx, len(match_dates)-1)],
                venue_id=venue.id,
                team1_id=t1.id, team2_id=t2.id,
                toss_winner_id=toss_winner.id,
                toss_decision=toss_decision,
                winner_id=winner.id,
                win_by_runs=win_by_runs,
                win_by_wickets=win_by_wickets,
                player_of_match_id=potm.id,
                stage=stage,
                team1_score=t1_score,
                team2_score=t2_score,
            )
            db.add(match)
            db.commit()

            # Batting stats
            for pidx, p in enumerate(player_objs[s1][:8]):
                stat = generate_batting_stats(p.id, t1.id, match.id, p.role, pidx < 5)
                db.add(BattingStat(**stat))
            for pidx, p in enumerate(player_objs[s2][:8]):
                stat = generate_batting_stats(p.id, t2.id, match.id, p.role, pidx < 5)
                db.add(BattingStat(**stat))

            # Bowling stats
            for p in player_objs[s1][2:9]:
                stat = generate_bowling_stats(p.id, t1.id, match.id, p.role)
                if stat:
                    db.add(BowlingStat(**stat))
            for p in player_objs[s2][2:9]:
                stat = generate_bowling_stats(p.id, t2.id, match.id, p.role)
                if stat:
                    db.add(BowlingStat(**stat))

        db.commit()
        print(f"  ✅ Season {year} seeded ({n_matches} matches)")

    db.close()
    print("\n🏏 Database seeded successfully!")
    print(f"   Seasons: 2008–2024  |  Teams: {len(TEAMS)}  |  Venues: {len(VENUES)}")


if __name__ == "__main__":
    seed()
