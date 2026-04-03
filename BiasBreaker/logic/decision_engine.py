"""
logic/decision_engine.py
═══════════════════════════════════════════════════════════
Modular Decision Engine for BiasBreaker.
Handles scoring, health, XP, streak multipliers, bias detection,
power-up resolution, and narrative story generation.
═══════════════════════════════════════════════════════════
"""

import random

# ── Scoring constants ──────────────────────────────────────────────────────────
SCORE = {
    "correct_hire":    10,
    "correct_reject":  10,
    "wrong_hire":      -5,
    "wrong_reject":    -15,
    "ai_follow_bonus": 20,
    "bias_penalty":    -10,
    "skip_penalty":    -3,
    "streak_bonus":    5,      # per consecutive correct after 3rd
    "clash_penalty":   -10,    # for clashing with high-confidence AI
}

# ── Narrative story pools ──────────────────────────────────────────────────────
_HIRE_WIN_STORIES = [
    "🌟 Outstanding move! The candidate joined the team and tripled productivity in Q1.",
    "✨ Excellent Hire! Within 90 days they shipped a feature that delighted 50k users.",
    "💪 Strong call! The candidate's unique background bridged a critical skill gap.",
    "🚀 Your hire became a rising star — now leading their own project team!",
    "🎯 Precision hiring! Competitors tried to poach them within 6 months.",
]

_HIRE_LOSE_STORIES = [
    "🚨 Bad Hire — the candidate left after 2 months, creating a costly re-hiring cycle.",
    "💸 Mis-hire! Culture fit issues surfaced week one; the team morale took a hit.",
    "⚠️ Red flag missed: the candidate struggled badly, pulling the whole team down.",
    "🔻 The hire left mid-project; a competitor finished first and captured the market.",
    "😬 Poor call — onboarding costs wasted, and the role is open again already.",
]

_REJECT_WIN_STORIES = [
    "🎯 Sharp rejection — the candidate would have slowed the team in 2 months.",
    "🧠 Smart pass — the candidate's references revealed serious reliability issues.",
    "🔍 Instinct confirmed: the candidate's next employer reported performance issues.",
    "✅ Clean cut — your team moved on with a better match and saved 3 months of drag.",
    "🛡️ Bullet dodged — the candidate's skill gaps would have exposed a critical system.",
]

_REJECT_LOSE_STORIES = [
    "📉 Missed talent! A competitor swooped in; they became that company's top performer.",
    "😱 Your rival hired them — 6 months later they're being featured in Forbes 30 Under 30.",
    "💔 Opportunity lost — the candidate's gap was a sabbatical to build exactly what you needed.",
    "🏆 Rejected and regretted: they won a major industry award last quarter.",
    "🌍 The candidate you passed on just landed a $5M contract with your closest competitor.",
]


def _pick_narrative(hired: bool, correct: bool, gap_years: float = 0,
                    gap_reason: str = "", is_boss: bool = False) -> str:
    """Return a context-aware narrative story for the decision."""
    rng = random.Random(hash((hired, correct, gap_reason)) % 9999)

    if hired and correct:
        story = rng.choice(_HIRE_WIN_STORIES)
    elif hired and not correct:
        story = rng.choice(_HIRE_LOSE_STORIES)
    elif not hired and correct:
        story = rng.choice(_REJECT_WIN_STORIES)
    else:  # rejected a good candidate
        story = rng.choice(_REJECT_LOSE_STORIES)
        if gap_years > 1.0 and gap_reason:
            story += f" (The gap was: {gap_reason})"

    if is_boss and correct:
        story = "👑 BOSS ROUND MASTERED! " + story
    elif is_boss and not correct:
        story = "💀 BOSS ROUND FAILED! " + story

    return story


def process_decision(
    user_choice: str,
    candidate: dict,
    game_state,
    ai_prediction: int,
    ai_confidence: float,
) -> dict:
    """
    Processes a single hiring decision end-to-end.

    Args:
        user_choice   (str):   'hire' | 'reject' | 'skip'
        candidate     (dict):  Candidate feature row
        game_state    (obj):   st.session_state (or dict-like)
        ai_prediction (int):   1 = Hire, 0 = Reject
        ai_confidence (float): Model probability [0, 1]

    Returns:
        dict with keys:
            result        (str):   'correct' | 'wrong' | 'skipped'
            bias_flag     (bool)
            health_change (int)
            xp_gain       (int)
            score_delta   (int)
            message       (str)
            ai_synced     (bool)
    """
    # ── Unpack candidate ────────────────────────────────────────────────────────
    outcome    = int(candidate.get("outcome", 0))
    is_boss    = candidate.get("is_boss", False)
    gap_years  = candidate.get("gap_years", 0.0)
    gap_reason = candidate.get("gap_reason", "")

    # ── Read power-up flags ─────────────────────────────────────────────────────
    shield = game_state.get("bias_shield_active", False)
    charm  = game_state.get("lucky_charm_active", False)

    # ── Read current streak for XP multiplier ──────────────────────────────────
    current_streak = game_state.get("streak", 0)

    # ══════════════════════════════════════════════════════════
    #  SKIP PATH
    # ══════════════════════════════════════════════════════════
    if user_choice == "skip":
        return {
            "result":        "skipped",
            "bias_flag":     False,
            "health_change": 0,
            "xp_gain":       5,
            "score_delta":   SCORE["skip_penalty"],
            "message":       "⏭ Decision Deferred — the seat stays empty while competitors move fast.",
            "ai_synced":     False,
        }

    # ══════════════════════════════════════════════════════════
    #  CORE DECISION LOGIC
    # ══════════════════════════════════════════════════════════
    hired   = (user_choice == "hire")
    correct = (hired and outcome == 1) or (not hired and outcome == 0)

    result        = "correct" if correct else "wrong"
    bias_flag     = False
    health_change = 0
    xp_gain       = 0
    score_delta   = 0
    messages      = []

    # ── Base score ──────────────────────────────────────────────────────────────
    if hired and outcome == 1:
        score_delta += SCORE["correct_hire"]
        messages.append(f"✅ Correct Hire +{SCORE['correct_hire']}")
        health_change += 5
    elif not hired and outcome == 0:
        score_delta += SCORE["correct_reject"]
        messages.append(f"✅ Correct Reject +{SCORE['correct_reject']}")
        health_change += 3
    elif hired and outcome == 0:
        score_delta += SCORE["wrong_hire"]
        messages.append(f"❌ Wrong Hire {SCORE['wrong_hire']}")
        health_change += -15
    else:  # wrong reject
        score_delta += SCORE["wrong_reject"]
        messages.append(f"❌ Wrong Reject {SCORE['wrong_reject']}")
        health_change += -25

    # ── XP (base + streak multiplier) ─────────────────────────────────────────
    streak_mult = max(1, current_streak)
    if correct:
        xp_gain = 50 * streak_mult
    else:
        xp_gain = 5  # consolation XP

    # ── Streak bonus score ─────────────────────────────────────────────────────
    if correct and current_streak >= 3:
        bonus = SCORE["streak_bonus"] * (current_streak - 2)
        score_delta += bonus
        messages.append(f"🔥 Streak x{current_streak - 2} +{bonus}")

    # ── Boss round double ─────────────────────────────────────────────────────
    if is_boss and correct:
        score_delta *= 2
        messages.append("👑 BOSS ROUND — Double Points!")
        xp_gain *= 2

    # ══════════════════════════════════════════════════════════
    #  AI SYNERGY / CLASH
    # ══════════════════════════════════════════════════════════
    ai_synced   = (hired == (ai_prediction == 1))
    hint_used   = game_state.get("_hint_used_this_round", False)

    if ai_synced:
        if hint_used:
            score_delta += SCORE["ai_follow_bonus"]
            messages.append(f"🤖 Followed AI Hint +{SCORE['ai_follow_bonus']}")
        else:
            score_delta += 5
            messages.append("🤖 Aligned with AI +5")
        xp_gain += 25
    else:
        if ai_confidence > 0.8:
            health_change += SCORE["clash_penalty"]
            messages.append("⚡ Clashed with High-Confidence AI — health penalty!")

    # ══════════════════════════════════════════════════════════
    #  POWER-UP: LUCKY CHARM
    # ══════════════════════════════════════════════════════════
    if charm and ai_synced:
        score_delta += 15
        xp_gain = int(xp_gain * 2)
        messages.append("🍀 Lucky Charm — Rewards Doubled!")

    # ══════════════════════════════════════════════════════════
    #  BIAS DETECTION
    # ══════════════════════════════════════════════════════════
    # Gap Bias: rejecting a good candidate with a career gap
    if not hired and gap_years > 1.0 and outcome == 1:
        bias_flag = True
        if shield:
            messages.append("🛡️ Bias Shield absorbed the penalty!")
        else:
            health_change += -15
            score_delta   += SCORE["bias_penalty"]
            messages.append(f"⚠️ BIAS DETECTED — Gap Penalty {SCORE['bias_penalty']}")

    # Education Bias: rejecting a high-potential low-education candidate
    if not hired and candidate.get("education", 3) <= 2 and outcome == 1:
        bias_flag = True
        if not shield:
            messages.append("⚠️ EDUCATION BIAS — Strong candidate rejected over degree.")

    # ══════════════════════════════════════════════════════════
    #  NARRATIVE MESSAGE
    # ══════════════════════════════════════════════════════════
    narrative = _pick_narrative(hired, correct, gap_years, gap_reason, is_boss)
    extra_msgs = " | ".join(messages)
    final_message = f"{narrative}\n\n_{extra_msgs}_"

    return {
        "result":        result,
        "bias_flag":     bias_flag,
        "health_change": health_change,
        "xp_gain":       xp_gain,
        "score_delta":   score_delta,
        "message":       final_message,
        "ai_synced":     ai_synced,
    }
