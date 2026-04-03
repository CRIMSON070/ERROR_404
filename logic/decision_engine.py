import random

SCORE_RULES = {
    "correct": 10,
    "wrong_reject": -15,
    "wrong_hire": -5,
    "ai_bonus": 20,
    "skip_penalty": -3,
    "bias_penalty": -10,
    "clash_penalty": -5,
    "health_min": 0,
}

def process_decision(user_choice, candidate, game_state, ai_prediction, ai_confidence):
    if user_choice not in {"hire", "reject", "skip"}:
        raise ValueError("Invalid user_choice")

    outcome = int(candidate.get("outcome", 0))
    is_boss = bool(candidate.get("is_boss", False))
    gap_years = float(candidate.get("gap_years", 0.0))

    has_shield = game_state.get("bias_shield_active", False)
    has_charm = game_state.get("lucky_charm_active", False)
    second_look = game_state.get("second_look_used", False)

    # base score and correctness
    if user_choice == "skip":
        delta = SCORE_RULES["skip_penalty"]
        correct = False
        message = f"Skipped ({SCORE_RULES['skip_penalty']} pts)."
    else:
        hired = (user_choice == "hire")
        correct = (hired and outcome == 1) or (not hired and outcome == 0)
        if correct:
            delta = SCORE_RULES["correct"]
            if hired:
                message = "✅ Correct hire — boosted team performance."
            else:
                message = "✅ Correct reject — bad fit avoided."
        elif hired and outcome == 0:
            delta = SCORE_RULES["wrong_hire"]
            message = "❌ Wrong hire — candidate left in 2 months."
        else:
            delta = SCORE_RULES["wrong_reject"]
            message = "❌ Wrong reject — competitor hired them."

    # AI agreement check
    followed_ai = False
    if user_choice != "skip":
        followed_ai = (user_choice == "hire") == (ai_prediction == 1)
        # AI bonus for using hint and following
        if game_state.get("_hint_used_this_round", False) and followed_ai:
            delta += SCORE_RULES["ai_bonus"]
            message += f" + AI bonus {SCORE_RULES['ai_bonus']}"

    # power-ups
    if has_charm and followed_ai and user_choice != "skip":
        delta += 10
        message += " + Lucky Charm +10"

    # bias shield + bias penalty
    bias_flag = False
    if user_choice == "reject" and outcome == 1 and gap_years < 1.0:
        # this is a conservative gap bias scenario
        bias_flag = True
        if has_shield:
            message += " | 🛡️ Bias Shield blocked bias penalty"
        else:
            delta += SCORE_RULES["bias_penalty"]
            message += f" | ⚠️ Bias penalty {SCORE_RULES['bias_penalty']}"

    # AI clash
    clash_flag = False
    if user_choice != "skip" and ((user_choice == "hire") != (ai_prediction == 1)):
        clash_flag = True
        if ai_confidence >= 0.7:
            delta += SCORE_RULES["clash_penalty"]
            message += f" | ⚡ Decision clash penalty {SCORE_RULES['clash_penalty']}"

    # boss double points
    if is_boss and correct and user_choice != "skip":
        delta *= 2
        message += " | 👑 Final boss x2"

    # health changes
    if user_choice == "skip":
        health_change = 0
    elif correct:
        health_change = 5
    else:
        health_change = -random.randint(10, 25)
        if clash_flag:
            health_change -= 5

    new_health = game_state.get("health", 100) + health_change
    new_health = max(SCORE_RULES["health_min"], min(100, new_health))

    # streak/xp
    if user_choice != "skip" and correct:
        new_streak = game_state.get("streak", 0) + 1
    else:
        new_streak = 0

    xp_gain = 2 + max(0, new_streak - 1) * 2 if correct else 1
    if has_charm and followed_ai and user_choice != "skip":
        xp_gain += 5

    new_xp = game_state.get("xp", 0) + xp_gain

    # ai agreement score and bias score
    ai_agreement_score = game_state.get("ai_agreement_score", 0) + (1 if followed_ai else -1 if user_choice != "skip" else 0)
    bias_score = game_state.get("bias_score", 0.0)
    if not followed_ai and ai_confidence >= 0.7 and user_choice != "skip":
        bias_score += ai_confidence * 2.0

    # life update
    lives = game_state.get("lives", 3)
    if user_choice != "skip" and not correct:
        lives = max(0, lives - 1)

    # history entry
    entry = {
        "candidate": {
            "experience": candidate.get("experience"),
            "skills_count": candidate.get("skills_count"),
            "gap_years": candidate.get("gap_years"),
            "education_level": candidate.get("education_level"),
            "gap_reason": candidate.get("gap_reason"),
            "is_boss": is_boss,
        },
        "user_choice": user_choice,
        "ai_choice": "hire" if ai_prediction == 1 else "reject",
        "outcome": outcome,
        "correct": correct,
        "followed_ai": followed_ai,
        "clash": clash_flag,
        "bias_flag": bias_flag,
        "ai_confidence": ai_confidence,
        "delta": delta,
        "health_change": health_change,
        "xp_gain": xp_gain,
        "message": message,
    }

    # apply updates
    game_state.update({
        "score": game_state.get("score", 0) + delta,
        "lives": lives,
        "health": new_health,
        "xp": new_xp,
        "streak": new_streak,
        "ai_agreement_score": ai_agreement_score,
        "bias_score": bias_score,
        "history": game_state.get("history", []) + [entry],
    })

    # consume temporary powerups and flags
    if has_shield:
        game_state["bias_shield_active"] = False
    if has_charm:
        game_state["lucky_charm_active"] = False
    if second_look:
        game_state["second_look_used"] = False

    return {
        "result": "correct" if correct else "wrong" if user_choice != "skip" else "skipped",
        "bias_flag": bias_flag,
        "health_change": health_change,
        "xp_gain": xp_gain,
        "message": message,
        "followed_ai": followed_ai,
        "clash": clash_flag,
        "delta": delta,
        "lives": lives,
        "is_boss": is_boss,
        "action": user_choice,
    }
