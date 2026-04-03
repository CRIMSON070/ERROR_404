"""
utils.py — AI/ML Core Engine for IPL Match Simulator
=====================================================
Handles:
  - Loading & merging player data from JSON datasets
  - Feature engineering for ML models
  - Training RandomForest regressors for player performance prediction
  - Training Logistic Regression for win probability
  - Team strength aggregation
  - Match simulation with controlled randomness
  - AI insight generation
  - Player comparison
"""

import json
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import warnings
warnings.filterwarnings("ignore")

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
DATA_DIR  = os.path.join(BASE_DIR, "..", "data", "processed")
FILE_ADV  = os.path.join(DATA_DIR, "advanced_ipl_analytics.json")
FILE_2025 = os.path.join(DATA_DIR, "ipl_2025_complete.json")

# ─── Team meta ────────────────────────────────────────────────────────────────
TEAM_INFO = {
    "RCB":  {"full": "Royal Challengers Bengaluru", "color": "#EC1C24", "logo": "🔴"},
    "MI":   {"full": "Mumbai Indians",              "color": "#005DA0", "logo": "🔵"},
    "CSK":  {"full": "Chennai Super Kings",         "color": "#FFCB05", "logo": "🟡"},
    "KKR":  {"full": "Kolkata Knight Riders",       "color": "#3A225D", "logo": "💜"},
    "SRH":  {"full": "Sunrisers Hyderabad",         "color": "#F7A721", "logo": "🟠"},
    "DC":   {"full": "Delhi Capitals",              "color": "#0078BC", "logo": "🔷"},
    "RR":   {"full": "Rajasthan Royals",            "color": "#EA1A85", "logo": "🌸"},
    "GT":   {"full": "Gujarat Titans",              "color": "#1B2133", "logo": "⚡"},
    "LSG":  {"full": "Lucknow Super Giants",        "color": "#A72056", "logo": "💙"},
    "PBKS": {"full": "Punjab Kings",                "color": "#ED1B24", "logo": "🦁"},
}

# ─── 1. DATA LOADING ──────────────────────────────────────────────────────────

def load_players() -> pd.DataFrame:
    """
    Load and merge both JSON datasets.
    ipl_2025_complete.json is treated as primary (more recent).
    advanced_ipl_analytics.json fills in missing data.
    Returns a clean DataFrame.
    """
    def _read(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return pd.DataFrame(data.get("players", []))

    df_2025 = _read(FILE_2025)
    df_adv  = _read(FILE_ADV)

    # Merge on player name + team; prefer 2025 data
    df = pd.merge(
        df_2025, df_adv,
        on=["name", "team", "role"],
        suffixes=("", "_adv"),
        how="outer"
    )

    # Coalesce numeric columns — prefer primary (2025) values
    for col in ["runs", "wickets", "strike_rate", "economy",
                "matches", "price", "performance_score", "value_score"]:
        if f"{col}_adv" in df.columns:
            df[col] = df[col].fillna(df[f"{col}_adv"])
            df.drop(columns=[f"{col}_adv"], inplace=True)

    # Clean up duplicate suffixed columns
    drop_cols = [c for c in df.columns if c.endswith("_adv")]
    df.drop(columns=drop_cols, inplace=True, errors="ignore")

    # Fill remaining NaNs
    df["runs"]              = df["runs"].fillna(0).astype(float)
    df["wickets"]           = df["wickets"].fillna(0).astype(float)
    df["strike_rate"]       = df["strike_rate"].fillna(120.0).astype(float)
    df["economy"]           = df["economy"].fillna(9.0).astype(float)
    df["matches"]           = df["matches"].fillna(1).astype(float)
    df["price"]             = df["price"].fillna(200).astype(float)
    df["performance_score"] = df["performance_score"].fillna(50.0).astype(float)
    df["value_score"]       = df["value_score"].fillna(5.0).astype(float)

    # ── Derived features ──────────────────────────────────────────────────
    df["batting_avg"]       = df["runs"] / df["matches"].clip(lower=1)
    df["bowling_avg"]       = df["wickets"] / df["matches"].clip(lower=1) * 10
    df["is_batsman"]        = df["role"].isin(["Batsman"]).astype(int)
    df["is_bowler"]         = df["role"].isin(["Bowler"]).astype(int)
    df["is_allrounder"]     = df["role"].isin(["All-rounder"]).astype(int)

    df = df.reset_index(drop=True)
    return df


def get_teams(df: pd.DataFrame) -> list:
    """Return sorted list of unique team codes."""
    return sorted(df["team"].dropna().unique().tolist())


def get_team_players(df: pd.DataFrame, team: str) -> pd.DataFrame:
    """Return all players for a given team."""
    return df[df["team"] == team].reset_index(drop=True)


# ─── 2. FEATURE ENGINEERING ───────────────────────────────────────────────────

def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build the ML feature matrix from player stats.
    Features used:
      - batting_avg     : proxy for expected runs per match
      - strike_rate     : scoring speed
      - bowling_avg     : proxy for wicket-taking ability
      - economy         : run-giving rate (inverted for quality)
      - matches         : experience weight
      - performance_score: composite dataset score
      - value_score     : auction efficiency score
    """
    features = df[[
        "batting_avg", "strike_rate", "bowling_avg", "economy",
        "matches", "performance_score", "value_score",
        "is_batsman", "is_bowler", "is_allrounder"
    ]].copy()

    # Economy: lower is better — invert to align direction with other features
    features["economy_inv"] = 1 / (features["economy"].clip(lower=0.1))

    return features


# ─── 3. ML MODEL TRAINING ─────────────────────────────────────────────────────

def _generate_training_data(df: pd.DataFrame):
    """
    ML: Synthetic augmentation to create a training dataset.
    We use each player's real stats as a seed and add Gaussian noise
    to generate N_AUG samples per player, simulating match-to-match variance.
    This gives the Random Forest enough samples to learn from.
    """
    np.random.seed(42)
    N_AUG = 30  # augmented samples per player

    rows_bat, rows_bowl = [], []

    for _, p in df.iterrows():
        for _ in range(N_AUG):
            noise = np.random.normal(0, 0.10)  # 10% noise

            # ── Batting target: expected runs in a 20-over innings ──────────
            base_runs = (p["batting_avg"] * 1.5) * (p["strike_rate"] / 120) * (1 + noise)
            base_runs = max(0, base_runs)

            rows_bat.append({
                "batting_avg":       p["batting_avg"]    * (1 + noise * 0.5),
                "strike_rate":       p["strike_rate"]    * (1 + noise * 0.3),
                "bowling_avg":       p["bowling_avg"]    * (1 + noise * 0.2),
                "economy":           p["economy"]        * (1 + noise * 0.2),
                "economy_inv":       1 / max(p["economy"] * (1 + noise * 0.2), 0.1),
                "matches":           p["matches"],
                "performance_score": p["performance_score"] * (1 + noise * 0.1),
                "value_score":       p["value_score"],
                "is_batsman":        p["is_batsman"],
                "is_bowler":         p["is_bowler"],
                "is_allrounder":     p["is_allrounder"],
                "target_runs":       base_runs,
            })

            # ── Bowling target: expected wickets per match ──────────────────
            base_wkt = (p["wickets"] / max(p["matches"], 1)) * (9.0 / max(p["economy"], 0.1)) * (1 + noise)
            base_wkt = max(0, base_wkt)

            rows_bowl.append({
                "batting_avg":       p["batting_avg"]    * (1 + noise * 0.2),
                "strike_rate":       p["strike_rate"]    * (1 + noise * 0.2),
                "bowling_avg":       p["bowling_avg"]    * (1 + noise * 0.5),
                "economy":           p["economy"]        * (1 + noise * 0.3),
                "economy_inv":       1 / max(p["economy"] * (1 + noise * 0.3), 0.1),
                "matches":           p["matches"],
                "performance_score": p["performance_score"] * (1 + noise * 0.1),
                "value_score":       p["value_score"],
                "is_batsman":        p["is_batsman"],
                "is_bowler":         p["is_bowler"],
                "is_allrounder":     p["is_allrounder"],
                "target_wickets":    base_wkt,
            })

    return pd.DataFrame(rows_bat), pd.DataFrame(rows_bowl)


FEATURE_COLS = [
    "batting_avg", "strike_rate", "bowling_avg", "economy",
    "economy_inv", "matches", "performance_score", "value_score",
    "is_batsman", "is_bowler", "is_allrounder"
]


def train_models(df: pd.DataFrame):
    """
    ML: Train two Random Forest Regressors:
      1. batting_model  → predicts expected runs contribution per player
      2. bowling_model  → predicts expected wickets contribution per player
    Returns (batting_model, bowling_model)
    """
    df_bat, df_bowl = _generate_training_data(df)

    # ── Batting Model (RandomForestRegressor) ───────────────────────────────
    X_bat = df_bat[FEATURE_COLS]
    y_bat = df_bat["target_runs"]

    batting_model = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestRegressor(
            n_estimators=150,
            max_depth=8,
            min_samples_leaf=3,
            random_state=42
        ))
    ])
    batting_model.fit(X_bat, y_bat)

    # ── Bowling Model (RandomForestRegressor) ───────────────────────────────
    X_bowl = df_bowl[FEATURE_COLS]
    y_bowl = df_bowl["target_wickets"]

    bowling_model = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestRegressor(
            n_estimators=150,
            max_depth=8,
            min_samples_leaf=3,
            random_state=42
        ))
    ])
    bowling_model.fit(X_bowl, y_bowl)

    return batting_model, bowling_model


# ─── 4. PLAYER PERFORMANCE PREDICTION ────────────────────────────────────────

def predict_player_performance(player_row: pd.Series,
                                batting_model,
                                bowling_model) -> dict:
    """
    ML: Predict individual player performance score.
    Returns dict with:
      - predicted_runs     : float
      - predicted_wickets  : float
      - player_score       : composite performance score
    """
    feat = {
        "batting_avg":       player_row["batting_avg"],
        "strike_rate":       player_row["strike_rate"],
        "bowling_avg":       player_row["bowling_avg"],
        "economy":           player_row["economy"],
        "economy_inv":       1 / max(player_row["economy"], 0.1),
        "matches":           player_row["matches"],
        "performance_score": player_row["performance_score"],
        "value_score":       player_row["value_score"],
        "is_batsman":        player_row["is_batsman"],
        "is_bowler":         player_row["is_bowler"],
        "is_allrounder":     player_row["is_allrounder"],
    }
    X = pd.DataFrame([feat])[FEATURE_COLS]

    pred_runs    = max(0, batting_model.predict(X)[0])
    pred_wickets = max(0, bowling_model.predict(X)[0])

    # Composite player performance score
    role = player_row.get("role", "")
    if role == "Batsman":
        score = pred_runs * 1.5 + player_row["performance_score"] * 0.3
    elif role == "Bowler":
        score = pred_wickets * 25 + player_row["performance_score"] * 0.3
    else:  # All-rounder
        score = pred_runs * 0.8 + pred_wickets * 15 + player_row["performance_score"] * 0.3

    return {
        "predicted_runs":    round(pred_runs, 1),
        "predicted_wickets": round(pred_wickets, 2),
        "player_score":      round(score, 1),
    }


# ─── 5. TEAM STRENGTH CALCULATION ────────────────────────────────────────────

def calculate_team_strength(players_df: pd.DataFrame,
                             batting_model,
                             bowling_model) -> dict:
    """
    Aggregate predicted player scores into team batting/bowling/overall strengths.
    Returns dict with detailed breakdown.
    """
    batting_scores, bowling_scores, all_scores = [], [], []
    predictions = []

    for _, row in players_df.iterrows():
        pred = predict_player_performance(row, batting_model, bowling_model)
        predictions.append({**row.to_dict(), **pred})
        all_scores.append(pred["player_score"])

        role = row.get("role", "")
        if role == "Batsman":
            batting_scores.append(pred["predicted_runs"])
        elif role == "Bowler":
            bowling_scores.append(pred["predicted_wickets"] * 20)
        else:
            batting_scores.append(pred["predicted_runs"] * 0.7)
            bowling_scores.append(pred["predicted_wickets"] * 12)

    batting_strength = sum(batting_scores)
    bowling_strength = sum(bowling_scores)
    overall_strength = batting_strength * 0.6 + bowling_strength * 0.4

    return {
        "batting_strength": round(batting_strength, 1),
        "bowling_strength": round(bowling_strength, 1),
        "overall_strength": round(overall_strength, 1),
        "players":          pd.DataFrame(predictions),
    }


# ─── 6. WIN PROBABILITY MODEL (Logistic Regression) ─────────────────────────

def build_win_probability_model():
    """
    ML: Logistic Regression trained on synthetic match outcomes.
    Features: [strength_diff_normalised, batting_ratio, bowling_ratio]
    Target:   1 if Team A wins, 0 if Team B wins
    """
    np.random.seed(99)
    N = 2000

    strength_a = np.random.uniform(80, 400, N)
    strength_b = np.random.uniform(80, 400, N)

    diff   = strength_a - strength_b
    ratio  = strength_a / (strength_b + 1e-5)
    noise  = np.random.normal(0, 15, N)

    # Logit: team A more likely to win when stronger, with noise for realism
    logit  = 0.025 * diff + 0.4 * (ratio - 1) + noise * 0.05
    prob_a = 1 / (1 + np.exp(-logit))
    y      = (prob_a > 0.5).astype(int)

    X = np.column_stack([diff, ratio, strength_a, strength_b])

    win_model = Pipeline([
        ("scaler", StandardScaler()),
        ("lr", LogisticRegression(C=1.0, random_state=42))
    ])
    win_model.fit(X, y)
    return win_model


def predict_win_probability(strength_a: float,
                             strength_b: float,
                             win_model) -> float:
    """
    ML: Return probability (0–1) that Team A wins.
    Uses the trained Logistic Regression model.
    """
    diff    = strength_a - strength_b
    ratio   = strength_a / (strength_b + 1e-5)
    X       = np.array([[diff, ratio, strength_a, strength_b]])
    prob_a  = win_model.predict_proba(X)[0][1]
    return round(float(prob_a), 3)


# ─── 7. MATCH SIMULATION ──────────────────────────────────────────────────────

def simulate_match(strength_a: float,
                   strength_b: float,
                   win_prob_a: float,
                   team_a: str,
                   team_b: str,
                   seed: int = None) -> dict:
    """
    Simulate a T20 match score based on team strength scores.
    Adds controlled randomness for realism (±15% variance).
    Returns team scores, winner, and margin.
    """
    rng = np.random.default_rng(seed)

    # Base score mapped from strength (calibrated to realistic T20 ranges 130–220)
    def strength_to_score(s):
        # Sigmoid-like mapping: strength 100→145, 200→175, 350→210
        base = 140 + (s - 100) * 0.25
        base = np.clip(base, 120, 230)
        variance = rng.normal(0, base * 0.12)
        return int(np.clip(base + variance, 90, 270))

    score_a = strength_to_score(strength_a)
    score_b = strength_to_score(strength_b)

    # Determine winner based on win_prob and actual scores
    if score_a > score_b:
        winner = team_a
        margin = f"{score_a - score_b} runs"
    elif score_b > score_a:
        winner = team_b
        margin = f"{score_b - score_a} runs"
    else:
        score_a += 1  # super over tiebreak
        winner = team_a
        margin = "Super Over"

    return {
        "score_a":   score_a,
        "score_b":   score_b,
        "winner":    winner,
        "margin":    margin,
        "win_prob_a": win_prob_a,
        "win_prob_b": round(1 - win_prob_a, 3),
    }


# ─── 8. PLAYER COMPARISON ────────────────────────────────────────────────────

def compare_players(p1: pd.Series,
                    p2: pd.Series,
                    batting_model,
                    bowling_model) -> dict:
    """
    Compare two players across key metrics.
    Returns comparison dict and a verdict string.
    """
    pred1 = predict_player_performance(p1, batting_model, bowling_model)
    pred2 = predict_player_performance(p2, batting_model, bowling_model)

    metrics = {
        "Batting Avg":      (p1["batting_avg"],       p2["batting_avg"]),
        "Strike Rate":      (p1["strike_rate"],        p2["strike_rate"]),
        "Economy Rate":     (10 - p1["economy"],       10 - p2["economy"]),   # inverted: lower economy = higher score
        "Wickets/Match":    (p1["bowling_avg"] / 10,   p2["bowling_avg"] / 10),
        "Predicted Runs":   (pred1["predicted_runs"],  pred2["predicted_runs"]),
        "Pred. Wickets":    (pred1["predicted_wickets"], pred2["predicted_wickets"]),
        "Perf. Score":      (p1["performance_score"],  p2["performance_score"]),
        "Value Score":      (p1["value_score"],        p2["value_score"]),
    }

    score1 = pred1["player_score"]
    score2 = pred2["player_score"]

    if score1 > score2 * 1.05:
        verdict = f"🏆 **{p1['name']}** is the stronger player (Score: {score1:.1f} vs {score2:.1f})"
    elif score2 > score1 * 1.05:
        verdict = f"🏆 **{p2['name']}** is the stronger player (Score: {score2:.1f} vs {score1:.1f})"
    else:
        verdict = f"⚖️ **{p1['name']}** and **{p2['name']}** are closely matched! (Score: {score1:.1f} vs {score2:.1f})"

    return {
        "metrics":  metrics,
        "score1":   score1,
        "score2":   score2,
        "pred1":    pred1,
        "pred2":    pred2,
        "verdict":  verdict,
    }


# ─── 9. AI INSIGHTS ───────────────────────────────────────────────────────────

def generate_insights(team_name: str,
                      team_result: dict,
                      opp_name: str,
                      opp_result: dict,
                      match_result: dict) -> list:
    """
    Generate human-readable AI insights based on predicted statistics.
    Returns a list of insight strings.
    """
    insights = []
    bat  = team_result["batting_strength"]
    bowl = team_result["bowling_strength"]
    ovr  = team_result["overall_strength"]

    # ── Batting insight ──────────────────────────────────────────────────────
    if bat > 200:
        insights.append(f"🔥 **{team_name}** has an exceptional batting lineup — projected to post big totals consistently.")
    elif bat > 140:
        insights.append(f"✅ **{team_name}** has a solid batting core with good depth in the middle order.")
    else:
        insights.append(f"⚠️ **{team_name}'s** batting lineup is thin — they may struggle to post competitive totals.")

    # ── Bowling insight ──────────────────────────────────────────────────────
    if bowl > 180:
        insights.append(f"💪 **{team_name}** boasts a destructive bowling attack — expect them to defend any target.")
    elif bowl > 100:
        insights.append(f"✅ **{team_name}** has a capable bowling department, but relies on key wicket-takers.")
    else:
        insights.append(f"❌ **{team_name}** lacks bowling strength — opposition batsmen could dominate.")

    # ── Balance insight ─────────────────────────────────────────────────────
    ratio = bat / (bowl + 1e-5)
    if ratio > 1.6:
        insights.append(f"⚠️ **{team_name}** is batting-heavy. If they don't defend well, they're vulnerable to chasing sides.")
    elif ratio < 0.7:
        insights.append(f"⚠️ **{team_name}** is bowling-heavy. They need improvisational batting to make the most of it.")
    else:
        insights.append(f"⚖️ **{team_name}** is a well-balanced side — a genuine all-conditions threat.")

    # ── Head-to-head insight ─────────────────────────────────────────────────
    wp = match_result["win_prob_a"] if match_result["winner"] == team_name else match_result["win_prob_b"]
    if wp > 0.65:
        insights.append(f"📊 AI gives **{team_name}** a dominant {wp*100:.0f}% win probability in this matchup.")
    elif wp > 0.5:
        insights.append(f"📊 **{team_name}** edges this contest at {wp*100:.0f}% — expect a competitive game.")
    else:
        insights.append(f"📊 **{team_name}** is the underdog at {wp*100:.0f}% but an upset is always possible in T20s!")

    # ── Player highlight ────────────────────────────────────────────────────
    players = team_result["players"]
    if len(players) > 0:
        top = players.sort_values("player_score", ascending=False).iloc[0]
        insights.append(
            f"⭐ **{top['name']}** is the standout performer for {team_name} "
            f"(AI Score: {top['player_score']:.1f}) — a genuine match-winner."
        )
        # High-value player
        value_top = players.sort_values("value_score", ascending=False).iloc[0]
        if value_top["value_score"] > 15:
            insights.append(
                f"💎 **{value_top['name']}** is a high-value pick for {team_name} "
                f"delivering exceptional output for their price (Value Score: {value_top['value_score']:.1f})."
            )

    return insights
