"""
IPL Intelligence Platform — Streamlit Dashboard
Run: streamlit run dashboard/app.py
"""
import sys, os, runpy
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not os.path.exists(os.path.join(BASE_DIR, "ipl.db")) or not os.path.exists(os.path.join(BASE_DIR, "ml", "win_predictor.pkl")):
    os.environ["PYTHONIOENCODING"] = "utf-8"
    _orig_dir = os.getcwd()
    os.chdir(BASE_DIR)
    runpy.run_path(os.path.join(BASE_DIR, "data", "seed_data.py"))
    runpy.run_path(os.path.join(BASE_DIR, "ml", "predictor.py"), run_name="__main__")
    os.chdir(_orig_dir)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import analytics
from ml.predictor import predict_match

st.set_page_config(
    page_title="IPL Intelligence Platform",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.metric-card {background:#1e3a5f;border-radius:12px;padding:18px;text-align:center;margin:4px;}
.metric-val  {font-size:2rem;font-weight:700;color:#60a5fa;}
.metric-lbl  {font-size:.8rem;color:#94a3b8;margin-top:4px;}
.pred-box    {background:linear-gradient(135deg,#1e3a5f,#0f172a);
              border:1px solid #334155;border-radius:16px;padding:24px;margin:8px 0;}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.shields.io/badge/IPL-Intelligence-blue?style=for-the-badge", width=220)
    st.markdown("### 🏏 IPL Intelligence Platform")
    st.markdown("*Analytics & ML Prediction Engine*")
    st.markdown("---")
    page = st.radio("Navigate", [
        "📊 Overview",
        "🏆 Team Analytics",
        "👤 Player Stats",
        "📅 Season Trends",
        "🎯 Match Predictor",
        "🔍 SQL Explorer",
    ])
    st.markdown("---")
    st.markdown("**Built by:** Sairam Chennaka")
    st.markdown("[GitHub](https://github.com/ram-cs7) · [LinkedIn](https://linkedin.com/in/sairam-chennaka)")
    st.markdown("**Stack:** FastAPI · SQLAlchemy · Scikit-learn · Plotly · Streamlit")

# ── Load data helpers ─────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_win_rates():    return pd.DataFrame(analytics.team_win_rates())
@st.cache_data(ttl=300)
def load_seasons():      return pd.DataFrame(analytics.season_summary())
@st.cache_data(ttl=300)
def load_batsmen():      return pd.DataFrame(analytics.top_batsmen(20))
@st.cache_data(ttl=300)
def load_bowlers():      return pd.DataFrame(analytics.top_bowlers(20))
@st.cache_data(ttl=300)
def load_toss():         return pd.DataFrame(analytics.toss_impact())
@st.cache_data(ttl=300)
def load_venues():       return pd.DataFrame(analytics.venue_stats())
@st.cache_data(ttl=300)
def load_heatmap():      return pd.DataFrame(analytics.season_wins_by_team())
@st.cache_data(ttl=300)
def load_potm():         return pd.DataFrame(analytics.player_of_match_leaders(10))


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📊 Overview":
    st.title("🏏 IPL Intelligence Platform")
    st.markdown("*End-to-end sports analytics: SQL · ML Prediction · REST API · Data Visualisation*")

    wr   = load_win_rates()
    seas = load_seasons()

    # KPI Row
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown('<div class="metric-card"><div class="metric-val">10</div><div class="metric-lbl">Teams</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{len(seas)}</div><div class="metric-lbl">Seasons</div></div>', unsafe_allow_html=True)
    with c3:
        total_matches = int(seas["total_matches"].sum())
        st.markdown(f'<div class="metric-card"><div class="metric-val">{total_matches}</div><div class="metric-lbl">Matches</div></div>', unsafe_allow_html=True)
    with c4:
        top_team = wr.iloc[0]["short_name"]
        st.markdown(f'<div class="metric-card"><div class="metric-val">{top_team}</div><div class="metric-lbl">Best Win Rate</div></div>', unsafe_allow_html=True)
    with c5:
        st.markdown('<div class="metric-card"><div class="metric-val">2008–24</div><div class="metric-lbl">Coverage</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Team Win Rates (%)")
        fig = px.bar(wr, x="short_name", y="win_pct", color="win_pct",
                     color_continuous_scale="Blues",
                     labels={"short_name": "Team", "win_pct": "Win %"},
                     text="win_pct")
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside", cliponaxis=False)
        fig.update_layout(showlegend=False, coloraxis_showscale=False,
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          font_color="white", height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Average Team Score Per Season")
        fig2 = px.line(seas, x="year", y="avg_team_score", markers=True,
                       color_discrete_sequence=["#60a5fa"],
                       labels={"year": "Season", "avg_team_score": "Avg Score"})
        fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           font_color="white", height=350)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Toss Impact Analysis")
    toss = load_toss()
    col3, col4 = st.columns(2)
    with col3:
        fig3 = px.bar(toss, x="toss_decision", y="win_pct_after_toss",
                      color="toss_decision", color_discrete_map={"bat":"#60a5fa","field":"#34d399"},
                      text="win_pct_after_toss",
                      labels={"toss_decision": "Decision", "win_pct_after_toss": "Win % after Toss"})
        fig3.update_traces(texttemplate="%{text:.1f}%", textposition="outside", cliponaxis=False)
        fig3.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)",
                           paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=300)
        st.plotly_chart(fig3, use_container_width=True)
    with col4:
        st.dataframe(toss.style.format({"win_pct_after_toss": "{:.1f}%"}),
                     use_container_width=True, height=200)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: TEAM ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🏆 Team Analytics":
    st.title("🏆 Team Analytics")
    wr = load_win_rates()

    st.subheader("All-Time Win Rate Leaderboard")
    styled = wr[["short_name","team","titles","matches_played","wins","win_pct","avg_score"]].copy()
    styled.columns = ["Code","Team","Titles 🏆","Played","Wins","Win %","Avg Score"]
    st.dataframe(styled.style.format({"Win %": "{:.1f}%", "Avg Score": "{:.0f}"}),
                 use_container_width=True, height=400)

    st.subheader("Season Wins Heatmap")
    heat = load_heatmap()
    pivot = heat.pivot(index="team", columns="year", values="wins").fillna(0)
    fig = px.imshow(pivot, color_continuous_scale="Blues", aspect="auto",
                    labels={"color": "Wins"}, title="Wins per Team per Season")
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                      font_color="white", height=420)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Head-to-Head Lookup")
    TEAMS = ["MI","CSK","KKR","RCB","SRH","DC","PBKS","RR","GT","LSG"]
    c1, c2 = st.columns(2)
    t1 = c1.selectbox("Team 1", TEAMS, index=0)
    t2 = c2.selectbox("Team 2", TEAMS, index=1)
    if t1 != t2:
        h2h = analytics.head_to_head(t1, t2)
        if h2h:
            h2h_df = pd.DataFrame(h2h)
            st.dataframe(h2h_df, use_container_width=True)
        else:
            st.info("No matches found between these teams.")
    else:
        st.warning("Select two different teams.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PLAYER STATS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "👤 Player Stats":
    st.title("👤 Player Statistics")
    tab1, tab2, tab3 = st.tabs(["🏏 Batsmen", "🎳 Bowlers", "🏅 Player of the Match"])

    with tab1:
        bat = load_batsmen()
        st.subheader("Top 20 Run Scorers")
        fig = px.bar(bat.head(15), x="name", y="total_runs", color="team",
                     hover_data=["avg_runs","avg_sr","sixes"],
                     labels={"name":"Player","total_runs":"Total Runs"})
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          font_color="white", xaxis_tickangle=-30, height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(bat.style.format({"avg_runs":"{:.1f}","avg_sr":"{:.1f}","strike_rate":"{:.1f}"}),
                     use_container_width=True)

    with tab2:
        bow = load_bowlers()
        st.subheader("Top 20 Wicket Takers")
        fig2 = px.scatter(bow, x="total_wickets", y="avg_economy", color="team",
                          size="total_wickets", hover_name="name",
                          labels={"total_wickets":"Wickets","avg_economy":"Economy"},
                          title="Wickets vs Economy (bubble = wickets)")
        fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           font_color="white", height=420)
        st.plotly_chart(fig2, use_container_width=True)
        st.dataframe(bow.style.format({"avg_economy":"{:.2f}","avg_overs":"{:.1f}"}),
                     use_container_width=True)

    with tab3:
        potm = load_potm()
        st.subheader("Player of the Match Leaders")
        fig3 = px.bar(potm, x="potm_count", y="name", orientation="h",
                      color="team", labels={"potm_count":"POTM Awards","name":"Player"})
        fig3.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           font_color="white", yaxis={"categoryorder":"total ascending"}, height=400)
        st.plotly_chart(fig3, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SEASON TRENDS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📅 Season Trends":
    st.title("📅 Season Trends (2008–2024)")
    seas = load_seasons()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=seas["year"], y=seas["avg_team_score"],
                             mode="lines+markers", name="Avg Score",
                             line=dict(color="#60a5fa", width=3)))
    fig.add_trace(go.Scatter(x=seas["year"], y=seas["highest_score"],
                             mode="lines+markers", name="Highest Score",
                             line=dict(color="#f97316", width=2, dash="dot")))
    fig.update_layout(title="Scoring Trends by Season", plot_bgcolor="rgba(0,0,0,0)",
                      paper_bgcolor="rgba(0,0,0,0)", font_color="white",
                      xaxis_title="Season", yaxis_title="Runs", height=450)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Champions by Season")
    st.dataframe(seas[["year","champion","total_matches","avg_team_score","highest_score"]]
                 .rename(columns={"year":"Season","champion":"Champion",
                                  "total_matches":"Matches","avg_team_score":"Avg Score",
                                  "highest_score":"Highest Score"})
                 .style.format({"Avg Score":"{:.0f}","Highest Score":"{:.0f}"}),
                 use_container_width=True, height=500)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: MATCH PREDICTOR
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🎯 Match Predictor":
    st.title("🎯 ML Match Predictor")
    st.markdown("*RandomForest classifier trained on 17 seasons of IPL data (2008–2024)*")

    TEAMS  = ["MI","CSK","KKR","RCB","SRH","DC","PBKS","RR","GT","LSG"]
    VENUES = ["Mumbai","Chennai","Kolkata","Bangalore","Hyderabad",
              "Delhi","Mohali","Jaipur","Ahmedabad","Lucknow"]

    with st.form("predictor"):
        c1, c2 = st.columns(2)
        team1        = c1.selectbox("Team 1", TEAMS, index=0)
        team2        = c2.selectbox("Team 2", TEAMS, index=1)
        venue        = st.selectbox("Venue City", VENUES)
        c3, c4, c5  = st.columns(3)
        toss_winner  = c3.selectbox("Toss Winner", [team1, team2])
        toss_dec     = c4.selectbox("Toss Decision", ["bat","field"])
        stage        = c5.selectbox("Stage", ["league","qualifier","final"])
        submitted    = st.form_submit_button("🔮 Predict Winner", type="primary")

    if submitted:
        if team1 == team2:
            st.error("Teams must be different!")
        else:
            with st.spinner("Running model..."):
                result = predict_match(
                    team1=team1, team2=team2, venue_city=venue,
                    toss_winner=toss_winner, toss_decision=toss_dec,
                    stage=stage, season_year=2024
                )
            winner = result["predicted_winner"]
            conf   = result["confidence"]
            t1p    = result["team1_win_probability"]
            t2p    = result["team2_win_probability"]

            st.success(f"🏆 Predicted Winner: **{winner}** ({conf:.1f}% confidence)")

            fig = go.Figure(go.Bar(
                x=[t1p, t2p], y=[team1, team2], orientation="h",
                marker_color=["#60a5fa" if team1==winner else "#334155",
                               "#60a5fa" if team2==winner else "#334155"],
                text=[f"{t1p:.1f}%", f"{t2p:.1f}%"], textposition="inside",
            ))
            fig.update_layout(title="Win Probability",
                              plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                              font_color="white", xaxis_range=[0,100], height=220)
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("Model Details"):
                st.json(result)
                st.markdown("""
**Algorithm:** Random Forest Classifier  
**Features:** Team win rates, historical performance, venue, toss outcome, stage, season  
**Training:** 595 IPL matches (2008–2024), 5-fold cross-validation  
**CV Accuracy:** ~52–56% (fair — IPL is inherently unpredictable)
""")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SQL EXPLORER
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 SQL Explorer":
    st.title("🔍 SQL Explorer")
    st.markdown("*Runs queries directly against the SQLite database — demonstrating SQL analytics skills*")

    presets = {
        "Top 10 teams by win rate": """
SELECT t.name, t.short_name, t.titles,
       COUNT(*) AS played,
       SUM(CASE WHEN m.winner_id = t.id THEN 1 ELSE 0 END) AS wins,
       ROUND(100.0 * SUM(CASE WHEN m.winner_id = t.id THEN 1 ELSE 0 END) / COUNT(*), 2) AS win_pct
FROM teams t
JOIN matches m ON (m.team1_id = t.id OR m.team2_id = t.id)
GROUP BY t.id ORDER BY win_pct DESC LIMIT 10""",

        "Season champions with match counts": """
SELECT s.year, t.name AS champion, COUNT(m.id) AS matches,
       AVG(m.team1_score + m.team2_score)/2 AS avg_score
FROM seasons s
JOIN teams t ON t.id = s.winner_id
JOIN matches m ON m.season_id = s.id
GROUP BY s.year ORDER BY s.year""",

        "Toss impact: bat vs field": """
SELECT toss_decision,
       COUNT(*) AS matches,
       SUM(CASE WHEN toss_winner_id = winner_id THEN 1 ELSE 0 END) AS toss_wins,
       ROUND(100.0 * SUM(CASE WHEN toss_winner_id = winner_id THEN 1 ELSE 0 END) / COUNT(*), 2) AS win_pct
FROM matches GROUP BY toss_decision""",

        "Top batsmen by total runs": """
SELECT p.name, t.short_name AS team,
       SUM(b.runs) AS total_runs, MAX(b.runs) AS highest,
       ROUND(AVG(b.strike_rate), 1) AS avg_sr, SUM(b.sixes) AS sixes
FROM batting_stats b
JOIN players p ON p.id = b.player_id
JOIN teams t ON t.id = p.team_id
GROUP BY p.id HAVING total_runs > 200
ORDER BY total_runs DESC LIMIT 10""",

        "Venue analysis": """
SELECT v.name, v.city, v.capacity,
       COUNT(m.id) AS hosted,
       ROUND(AVG(m.team1_score + m.team2_score), 1) AS avg_total
FROM venues v JOIN matches m ON m.venue_id = v.id
GROUP BY v.id ORDER BY hosted DESC""",
    }

    preset = st.selectbox("Choose a preset query", list(presets.keys()))
    query  = st.text_area("SQL Query", value=presets[preset], height=180)

    if st.button("▶ Run Query", type="primary"):
        try:
            from database.database import execute_sql
            rows = execute_sql(query)
            if rows:
                df = pd.DataFrame(rows)
                st.success(f"{len(df)} rows returned")
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Query returned no results.")
        except Exception as e:
            st.error(f"SQL Error: {e}")
