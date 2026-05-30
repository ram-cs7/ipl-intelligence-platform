from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass


class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    short_name = Column(String(5), nullable=False)
    home_city = Column(String)
    titles = Column(Integer, default=0)

    home_matches = relationship("Match", foreign_keys="Match.team1_id", back_populates="team1")
    away_matches = relationship("Match", foreign_keys="Match.team2_id", back_populates="team2")
    players = relationship("Player", back_populates="team")


class Venue(Base):
    __tablename__ = "venues"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    city = Column(String)
    capacity = Column(Integer)
    matches = relationship("Match", back_populates="venue")


class Season(Base):
    __tablename__ = "seasons"
    id = Column(Integer, primary_key=True)
    year = Column(Integer, unique=True, nullable=False)
    winner_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    matches = relationship("Match", back_populates="season")


class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"))
    role = Column(String)          # Batsman / Bowler / All-Rounder / WK-Batsman
    nationality = Column(String, default="Indian")

    team = relationship("Team", back_populates="players")
    batting = relationship("BattingStat", back_populates="player")
    bowling = relationship("BowlingStat", back_populates="player")


class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True)
    season_id = Column(Integer, ForeignKey("seasons.id"))
    match_date = Column(Date)
    venue_id = Column(Integer, ForeignKey("venues.id"))
    team1_id = Column(Integer, ForeignKey("teams.id"))
    team2_id = Column(Integer, ForeignKey("teams.id"))
    toss_winner_id = Column(Integer, ForeignKey("teams.id"))
    toss_decision = Column(String)   # bat / field
    winner_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    win_by_runs = Column(Integer, default=0)
    win_by_wickets = Column(Integer, default=0)
    player_of_match_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    stage = Column(String, default="league")   # league / qualifier / final
    team1_score = Column(Integer)
    team2_score = Column(Integer)

    season = relationship("Season", back_populates="matches")
    venue = relationship("Venue", back_populates="matches")
    team1 = relationship("Team", foreign_keys=[team1_id], back_populates="home_matches")
    team2 = relationship("Team", foreign_keys=[team2_id], back_populates="away_matches")


class BattingStat(Base):
    __tablename__ = "batting_stats"
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    player_id = Column(Integer, ForeignKey("players.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    runs = Column(Integer, default=0)
    balls = Column(Integer, default=0)
    fours = Column(Integer, default=0)
    sixes = Column(Integer, default=0)
    strike_rate = Column(Float, default=0.0)
    dismissed = Column(Boolean, default=True)

    player = relationship("Player", back_populates="batting")


class BowlingStat(Base):
    __tablename__ = "bowling_stats"
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    player_id = Column(Integer, ForeignKey("players.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    overs = Column(Float, default=0.0)
    wickets = Column(Integer, default=0)
    runs_conceded = Column(Integer, default=0)
    economy = Column(Float, default=0.0)
    maidens = Column(Integer, default=0)

    player = relationship("Player", back_populates="bowling")
