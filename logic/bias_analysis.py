def calculate_bias(history, ai_confidence_threshold=0.6):
    if not history:
        return {"bias_score": 0.0, "bias_level": "Fair", "bias_type": "None"}

    total_weight = 0.0
    weighted_disagree = 0.0
    gap_bias = 0
    education_bias = 0
    experience_bias = 0
    types = []

    for item in history:
        ai_c = item.get("ai_confidence", 0.0)
        disagree = item.get("followed_ai") is False and item.get("action") != "skip"

        total_weight += 1.0
        if disagree and ai_c >= ai_confidence_threshold:
            weighted_disagree += ai_c

        candidate = item.get("candidate", {})
        gap = candidate.get("gap_years", 0.0)
        edu = candidate.get("education_level", 0)
        exp = candidate.get("experience", 0.0)

        # detect weak patterns across errors
        if item.get("action") == "reject" and item.get("outcome") == 1:
            if gap > 2.0:
                gap_bias += 1
            if edu <= 2:
                education_bias += 1
            if exp < 3.0:
                experience_bias += 1

    bias_score = round((weighted_disagree / max(1.0, total_weight)) * 100.0, 1)

    if bias_score < 15:
        bias_level = "Fair"
    elif bias_score < 35:
        bias_level = "Moderate"
    else:
        bias_level = "High"

    # pick dominant bias type
    counters = {
        "Gap Bias": gap_bias,
        "Education Bias": education_bias,
        "Experience Bias": experience_bias,
    }
    dominant = max(counters, key=counters.get)
    if counters[dominant] == 0:
        dominant = "None"

    return {
        "bias_score": bias_score,
        "bias_level": bias_level,
        "bias_type": dominant,
    }
