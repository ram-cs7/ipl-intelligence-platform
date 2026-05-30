"""
All analytics queries — demonstrating SQL fluency for DS roles.
Heavy use of aggregations, window functions, CTEs, and GROUP BY.
"""
from database.database import execute_sql


def team_win_rates(min_matches: int = 10):
    return execute_sql("""
        SELECT
            t.name                                             AS team,
            t.short_name,
            t.titles,
            COUNT(*)                                           AS matches_played,
            SUM(CASE WHEN m.winner_id = t.id THEN 1 ELSE 0 END) AS wins,
            ROUND(
                100.0 * SUM(CASE WHEN m.winner_id = t.id THEN 1 ELSE 0 END)
                / NULLIF(COUNT(*), 0), 2
            )                                                  AS win_pct,
            AVG(CASE WHEN m.team1_id = t.id THEN m.team1_score
                     WHEN m.team2_id = t.id THEN m.team2_score END)  AS avg_score
        FROM teams t
        JOIN matches m ON (m.team1_id = t.id OR m.team2_id = t.id)
        GROUP BY t.id
        HAVING COUNT(*) >= :min_matches
        ORDER BY win_pct DESC
    """, {"min_matches": min_matches})


def season_summary():
    return execute_sql("""
        SELECT
            s.year,
            t.name                                     AS champion,
            t.short_name                               AS champion_short,
            COUNT(m.id)                                AS total_matches,
            AVG(m.team1_score + m.team2_score) / 2.0  AS avg_team_score,
            MAX(m.team1_score)                         AS highest_score
        FROM seasons s
        JOIN teams t    ON t.id = s.winner_id
        JOIN matches m  ON m.season_id = s.id
        GROUP BY s.year
        ORDER BY s.year
    """)


def top_batsmen(limit: int = 15):
    return execute_sql("""
        SELECT
            p.name,
            t.short_name                  AS team,
            p.role,
            COUNT(b.id)                   AS innings,
            SUM(b.runs)                   AS total_runs,
            MAX(b.runs)                   AS highest_score,
            ROUND(AVG(b.runs), 1)         AS avg_runs,
            ROUND(AVG(b.strike_rate), 1)  AS avg_sr,
            SUM(b.fours)                  AS fours,
            SUM(b.sixes)                  AS sixes
        FROM batting_stats b
        JOIN players p ON p.id = b.player_id
        JOIN teams   t ON t.id = b.team_id
        GROUP BY p.id
        HAVING SUM(b.runs) > 100
        ORDER BY total_runs DESC
        LIMIT :limit
    """, {"limit": limit})


def top_bowlers(limit: int = 15):
    return execute_sql("""
        SELECT
            p.name,
            t.short_name              AS team,
            COUNT(bw.id)              AS appearances,
            SUM(bw.wickets)           AS total_wickets,
            ROUND(AVG(bw.economy),2)  AS avg_economy,
            ROUND(AVG(bw.overs),1)    AS avg_overs,
            MIN(bw.economy)           AS best_economy,
            SUM(bw.maidens)           AS maidens
        FROM bowling_stats bw
        JOIN players p ON p.id = bw.player_id
        JOIN teams   t ON t.id = bw.team_id
        GROUP BY p.id
        HAVING SUM(bw.wickets) > 5
        ORDER BY total_wickets DESC
        LIMIT :limit
    """, {"limit": limit})


def toss_impact():
    return execute_sql("""
        SELECT
            m.toss_decision,
            COUNT(*)                                                       AS total_matches,
            SUM(CASE WHEN m.toss_winner_id = m.winner_id THEN 1 ELSE 0 END) AS toss_then_won,
            ROUND(
                100.0 * SUM(CASE WHEN m.toss_winner_id = m.winner_id THEN 1 ELSE 0 END)
                / COUNT(*), 2
            ) AS win_pct_after_toss
        FROM matches m
        GROUP BY m.toss_decision
    """)


def venue_stats():
    return execute_sql("""
        SELECT
            v.name                              AS venue,
            v.city,
            v.capacity,
            COUNT(m.id)                         AS matches_hosted,
            AVG(m.team1_score + m.team2_score)  AS avg_total_runs,
            MAX(m.team1_score)                  AS highest_team_score,
            MIN(m.team1_score)                  AS lowest_team_score
        FROM venues v
        JOIN matches m ON m.venue_id = v.id
        GROUP BY v.id
        ORDER BY matches_hosted DESC
    """)


def head_to_head(team1_short: str, team2_short: str):
    return execute_sql("""
        SELECT
            t1.short_name  AS team1,
            t2.short_name  AS team2,
            COUNT(*)       AS total_matches,
            SUM(CASE WHEN m.winner_id = t1.id THEN 1 ELSE 0 END) AS team1_wins,
            SUM(CASE WHEN m.winner_id = t2.id THEN 1 ELSE 0 END) AS team2_wins
        FROM matches m
        JOIN teams t1 ON t1.id = m.team1_id
        JOIN teams t2 ON t2.id = m.team2_id
        WHERE (t1.short_name = :t1 AND t2.short_name = :t2)
           OR (t1.short_name = :t2 AND t2.short_name = :t1)
        GROUP BY t1.short_name, t2.short_name
    """, {"t1": team1_short, "t2": team2_short})


def season_wins_by_team():
    """Heatmap data: team × year wins."""
    return execute_sql("""
        SELECT
            t.short_name AS team,
            s.year,
            SUM(CASE WHEN m.winner_id = t.id THEN 1 ELSE 0 END) AS wins
        FROM teams t
        CROSS JOIN seasons s
        LEFT JOIN matches m ON m.season_id = s.id
            AND (m.team1_id = t.id OR m.team2_id = t.id)
        GROUP BY t.short_name, s.year
        ORDER BY t.short_name, s.year
    """)


def player_of_match_leaders(limit: int = 10):
    return execute_sql("""
        SELECT
            p.name,
            t.short_name  AS team,
            COUNT(m.id)   AS potm_count
        FROM matches m
        JOIN players p ON p.id = m.player_of_match_id
        JOIN teams   t ON t.id = p.team_id
        GROUP BY p.id
        ORDER BY potm_count DESC
        LIMIT :limit
    """, {"limit": limit})
