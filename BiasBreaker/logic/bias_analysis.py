"""
logic/bias_analysis.py
═══════════════════════════════════════════════════════════
Advanced bias detection engine for BiasBreaker.
Detects Gap Bias, Education Bias, and Experience Bias.
Weights disagreements by AI confidence for accuracy.
═══════════════════════════════════════════════════════════
"""


# ── Bias type labels and descriptions ─────────────────────────────────────────
BIAS_META = {
    "Gap Bias": {
        "icon": "⏳",
        "description": "Penalizing candidates with career breaks",
        "tip": "Career gaps often reflect growth (parental leave, education, freelancing). Focus on skills and experience instead.",
    },
    "Education Bias": {
        "icon": "🎓",
        "description": "Requiring degrees over demonstrated skills",
        "tip": "Many top performers are self-taught or non-traditional. Skill breadth is a stronger predictor of success.",
    },
    "Experience Bias": {
        "icon": "📅",
        "description": "Dismissing junior candidates with high potential",
        "tip": "Years of experience don't always equal impact. High-skill juniors often outperform low-skill veterans.",
    },
    "None": {
        "icon": "✅",
        "description": "No significant bias detected",
        "tip": "Keep it up — you're evaluating candidates on merit!",
    },
}


def calculate_bias(history: list, resumes: list) -> dict:
    """
    Analyzes decision history for three bias types.
    Weights each flagged decision by AI confidence when available.

    Args:
        history (list): List of decision records from session_state.history
        resumes (list): Full list of resume dicts

    Returns:
        dict: {
            "bias_score":  float (0–100),
            "bias_level":  "Fair" | "Moderate" | "High",
            "bias_type":   str,
            "breakdown":   dict of per-type rates,
            "meta":        dict with icon, description, tip,
        }
    """
    if len(history) < 2:
        return {
            "bias_score": 0,
            "bias_level": "Fair",
            "bias_type":  "None",
            "breakdown":  {"gap": 0.0, "education": 0.0, "experience": 0.0},
            "meta":       BIAS_META["None"],
        }

    gap_total,  gap_wrong  = 0, 0.0
    edu_total,  edu_wrong  = 0, 0.0
    exp_total,  exp_wrong  = 0, 0.0

    for h in history:
        if h.get("action") == "skip":
            continue

        idx     = h.get("round", 0)
        # Guard: resumes might be shorter than round index if mid-game
        if idx >= len(resumes):
            continue

        row     = resumes[idx]
        action  = h.get("action", "skip")
        outcome = int(h.get("outcome", row.get("outcome", 0)))
        # Use AI confidence if stored, default 0.5 for uniform weighting
        confidence_weight = float(h.get("ai_confidence", 0.5))

        rejected = (action == "reject")
        bad_reject = rejected and (outcome == 1)  # rejected a good candidate

        # 1. Gap Bias — rejecting good candidates who have career gaps
        if row.get("gap_years", 0) > 1.0:
            gap_total += 1
            if bad_reject:
                gap_wrong += confidence_weight

        # 2. Education Bias — rejecting good candidates with lower formal education
        if int(row.get("education", 3)) < 3:
            edu_total += 1
            if bad_reject:
                edu_wrong += confidence_weight

        # 3. Experience Bias — rejecting good candidates with < 5 years experience
        if float(row.get("experience", 10)) < 5:
            exp_total += 1
            if bad_reject:
                exp_wrong += confidence_weight

    # ── Rate calculation ────────────────────────────────────────────────────────
    gap_rate = (gap_wrong / gap_total)  if gap_total > 0 else 0.0
    edu_rate = (edu_wrong / edu_total)  if edu_total > 0 else 0.0
    exp_rate = (exp_wrong / exp_total)  if exp_total > 0 else 0.0

    # ── Dominant bias ───────────────────────────────────────────────────────────
    rates = {"Gap Bias": gap_rate, "Education Bias": edu_rate, "Experience Bias": exp_rate}
    max_type = max(rates, key=rates.get)
    max_rate = rates[max_type]

    bias_score = round(min(100.0, max_rate * 100), 1)
    bias_type  = max_type if bias_score > 0 else "None"

    if bias_score > 30:
        bias_level = "High"
    elif bias_score > 15:
        bias_level = "Moderate"
    else:
        bias_level = "Fair"

    return {
        "bias_score": bias_score,
        "bias_level": bias_level,
        "bias_type":  bias_type,
        "breakdown":  {
            "gap":        round(gap_rate * 100, 1),
            "education":  round(edu_rate * 100, 1),
            "experience": round(exp_rate * 100, 1),
        },
        "meta": BIAS_META.get(bias_type, BIAS_META["None"]),
    }


def get_bias_feedback_message(bias_type: str, candidate: dict) -> str:
    """
    Generate a specific learning message for a biased decision.

    Args:
        bias_type (str): The identified bias type
        candidate (dict): The candidate row that triggered bias

    Returns:
        str: Human-readable bias warning with context
    """
    gap  = candidate.get("gap_years", 0)
    gap_r = candidate.get("gap_reason", "unknown reason")
    exp  = candidate.get("experience", 0)
    edu  = candidate.get("education", 3)

    if bias_type == "Gap Bias":
        return (
            f"⚠️ You showed **GAP BIAS** — you rejected a strong candidate "
            f"who had a {gap:.1f}-year gap ({gap_r}). "
            f"Many career breaks reflect intentional growth, not failure."
        )
    elif bias_type == "Education Bias":
        from data_engine import EDUCATION_MAP
        edu_label = EDUCATION_MAP.get(int(edu), "lower degree")
        return (
            f"⚠️ You showed **EDUCATION BIAS** — this candidate only had a "
            f"*{edu_label}* but had strong experience ({exp:.0f} yrs). "
            f"Degree level is a weaker signal than skills + experience."
        )
    elif bias_type == "Experience Bias":
        return (
            f"⚠️ You showed **EXPERIENCE BIAS** — this candidate had only "
            f"{exp:.1f} years of experience but high-quality skill breadth. "
            f"Junior high-performers often exceed long-tenured mediocre hires."
        )
    return ""
