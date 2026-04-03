"""
game_state.py
Session state initialization and game scoring logic for BiasBreaker.
"""

import streamlit as st
import random
import csv
import os
from data_engine import generate_resumes, make_boss_resume

LEADERBOARD_FILE = os.path.join(os.path.dirname(__file__), "leaderboard.csv")

# ── Scoring constants ─────────────────────────────────────────────────────────
SCORE = {
    "correct_hire":   10,
    "correct_reject": 10,
    "wrong_hire":     -5,
    "wrong_reject":   -15,
    "ai_hint_cost":   -3,
    "ai_follow_bonus": 20,
    "bias_penalty":   -10,
    "skip_penalty":   -3,
    "streak_bonus":   5,      # per consecutive correct after 3
}


def init_state():
    """Initializes all required session state keys if they don't exist."""
    defaults = {
        # --- Game States ---
        "game_started":  False,
        "round_idx":     0,
        "score":         0,
        "lives":         3,
        "health":        100,
        "xp":            0,
        "streak":        0,
        "best_streak":   0,
        "game_over":     False,
        "resumes":       [],
        "awaiting_next": False,
        "last_result":   None,
        "history":       [],
        "decision_log":  [],
        "skips_used":    0,
        "ai_uses":       3,
        "hint_shown":    False,
        "_hint_used_this_round": False,
        "_pred_round":   -1,
        "_prob":         0.5,
        "_ai_pred":      0,
        "_whisper":      {},
        "_llm_whisper":  None,
        
        # --- New Metrics ---
        "bias_score":    0,
        "ai_agreement_score": 0,
        "rank":          "Beginner",
        
        "bias_shield_active": False,
        "lucky_charm_active": False,
        "second_look_used":   False,
        "blind_mode":         False,
        
        "round_complete_anim": False,
        "player_name": "Challenger",
        "achievements": [],
        "difficulty": "normal",
    }
    
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # --- Powerup Status ---
    if "powerups" not in st.session_state:
        st.session_state.powerups = {
            "bias_shield": 1,
            "lucky_charm": 1,
            "second_look": 1,
        }
    else:
        # Ensure all keys exist in current dict
        for p_key in ["bias_shield", "lucky_charm", "second_look"]:
            if p_key not in st.session_state.powerups:
                st.session_state.powerups[p_key] = 1


def start_game(player_name: str = "Challenger", difficulty: str = "normal"):
    base = generate_resumes(300, seed=random.randint(0, 9999), difficulty=difficulty)
    sample = base.sample(9, random_state=random.randint(0, 9999)).reset_index(drop=True)
    boss = make_boss_resume(seed=random.randint(0, 999))
    st.session_state.resumes = sample.to_dict("records") + [boss]
    st.session_state.game_started = True
    st.session_state.player_name = player_name or "Challenger"


def compute_score(action: str, outcome: int, ai_pred: int, row: dict,
                  shield: bool = False, charm: bool = False, is_boss: bool = False):
    """Returns (delta, message, correct)"""
    if action == "skip":
        st.session_state.streak = 0
        return SCORE["skip_penalty"], f"⏭ Skipped ({SCORE['skip_penalty']} pts)", False

    hired = action == "hire"
    correct = (hired and outcome == 1) or (not hired and outcome == 0)

    delta = 0
    msgs  = []

    if hired and outcome == 1:
        delta += SCORE["correct_hire"]
        msgs.append(f"✅ Correct Hire +{SCORE['correct_hire']}")
    elif not hired and outcome == 0:
        delta += SCORE["correct_reject"]
        msgs.append(f"✅ Correct Reject +{SCORE['correct_reject']}")
    elif hired and outcome == 0:
        delta += SCORE["wrong_hire"]
        msgs.append(f"❌ Wrong Hire {SCORE['wrong_hire']}")
    else:
        delta += SCORE["wrong_reject"]
        msgs.append(f"❌ Wrong Reject {SCORE['wrong_reject']}")

    # AI follow bonus
    followed_ai = (hired == (ai_pred == 1))
    hint_used   = st.session_state.get("_hint_used_this_round", False)
    if hint_used and followed_ai:
        delta += SCORE["ai_follow_bonus"]
        msgs.append(f"🤖 Followed AI +{SCORE['ai_follow_bonus']}")

    # Lucky charm bonus
    if charm and followed_ai:
        delta += 10
        msgs.append("🍀 Lucky Charm +10")

    # Bias penalty: rejecting a good candidate with tiny gap
    if not hired and row.get("gap_years", 0) < 1.0 and outcome == 1:
        if shield:
            msgs.append("🛡️ Bias Shield blocked penalty!")
        else:
            delta += SCORE["bias_penalty"]
            msgs.append(f"⚠️ Bias Penalty {SCORE['bias_penalty']}")

    # Streak bonus
    if correct:
        st.session_state.streak += 1
        if st.session_state.streak > st.session_state.best_streak:
            st.session_state.best_streak = st.session_state.streak
        if st.session_state.streak >= 3:
            bonus = SCORE["streak_bonus"] * (st.session_state.streak - 2)
            delta += bonus
            msgs.append(f"🔥 Streak x{st.session_state.streak-2} +{bonus}")
    else:
        st.session_state.streak = 0

    # Boss double
    if is_boss and correct:
        delta *= 2
        msgs.append("👹 BOSS x2!")

    return delta, " | ".join(msgs), correct


def save_leaderboard(name: str, score: int, correct: int, rounds: int):
    os.makedirs(os.path.dirname(LEADERBOARD_FILE), exist_ok=True)
    file_exists = os.path.isfile(LEADERBOARD_FILE)
    with open(LEADERBOARD_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not file_exists:
            w.writerow(["name", "score", "correct", "rounds"])
        w.writerow([name, score, correct, rounds])


def load_leaderboard():
    if not os.path.isfile(LEADERBOARD_FILE):
        return []
    rows = []
    with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rows.append({
                    "name":    row["name"],
                    "score":   int(row["score"]),
                    "correct": int(row["correct"]),
                    "rounds":  int(row["rounds"]),
                })
            except Exception:
                pass
    return sorted(rows, key=lambda x: x["score"], reverse=True)[:10]


def analyze_bias(history: list[dict], resumes: list[dict]) -> dict:
    """
    Analyzes player decisions to detect potential bias against career gaps.
    Returns a dict with 'status' (string) and 'score' (int percentage).
    """
    if len(history) < 3:
        return {"status": "Not enough data yet", "score": 0}

    gap_rejects = 0
    gap_total = 0
    no_gap_rejects = 0
    no_gap_total = 0

    for h in history:
        if h["action"] == "skip":
            continue
        
        idx = h["round"]
        row = resumes[idx]
        is_reject = h["action"] == "reject"
        
        if row.get("gap_years", 0) > 1.0:
            gap_total += 1
            if is_reject:
                gap_rejects += 1
        else:
            no_gap_total += 1
            if is_reject:
                no_gap_rejects += 1

    gap_reject_rate = (gap_rejects / gap_total) if gap_total > 0 else 0
    no_gap_reject_rate = (no_gap_rejects / no_gap_total) if no_gap_total > 0 else 0

    diff = gap_reject_rate - no_gap_reject_rate
    bias_score = int(max(0, min(100, diff * 100)))

    if bias_score > 30 and gap_total >= 2:
        status = "⚠️ High bias detected against career gaps"
    elif bias_score > 15:
        status = "⚠️ Slight gap bias detected"
    else:
        status = "✅ No strong bias detected"

    return {"status": status, "score": bias_score}


def evaluate_skill_gaps(history: list[dict], resumes: list[dict]) -> dict:
    """
    Analyzes what player might be over-valuing or under-valuing.
    Returns strings for strengths, weaknesses, and a list of missions.
    """
    if len(history) < 3:
        return {
            "strengths": "Need more data.",
            "weaknesses": "Play more rounds to reveal weaknesses.",
            "missions": ["Play 3 more rounds to unlock analysis."]
        }
    
    # We want to see what caused mistakes.
    # E.g. did they reject high-skill candidates (undervaluing skills)?
    # Did they hire low-education but high-exp candidates?
    
    rejected_high_skill = 0
    hired_low_skill = 0
    penalized_gaps = 0
    relied_on_ai = 0
    
    for h in history:
        r = h["round"]
        row = resumes[r]
        if h["action"] == "reject" and row.get("skills_count", 0) > 6 and row.get("outcome") == 1:
            rejected_high_skill += 1
        if h["action"] == "hire" and row.get("skills_count", 0) < 4 and row.get("outcome") == 0:
            hired_low_skill += 1
        if h["action"] == "reject" and row.get("gap_years", 0) > 1.0 and row.get("outcome") == 1:
            penalized_gaps += 1
        if h.get("followed_ai"):
            relied_on_ai += 1
            
    strengths = []
    weaknesses = []
    missions = []
    
    if relied_on_ai > len(history) * 0.5:
        strengths.append("High synergy with AI Mentor.")
    else:
        strengths.append("Independent decision maker.")
        
    if rejected_high_skill > 0:
        weaknesses.append("Under-values pure technical skills.")
        missions.append("🎯 Mission: Hire a candidate based purely on high Skill Attack.")
    
    if hired_low_skill > 0:
        weaknesses.append("Over-values experience over actual skills.")
        missions.append("🎯 Mission: Check Skill Attack before hiring experienced candidates.")
        
    if penalized_gaps > 0:
        weaknesses.append("High penalty applied to career gaps.")
        missions.append("🎯 Mission: Look past a career gap (Risk Spike) if Armor/HP is high.")
        
    if not weaknesses:
        strengths.append("Consistently objective evaluations.")
        weaknesses.append("None detected! Perfect run.")
        missions.append("🎯 Mission: Try beating the next rounds on Hard mode.")
        
    return {
        "strengths": " | ".join(strengths),
        "weaknesses": " | ".join(weaknesses),
        "missions": missions
    }
