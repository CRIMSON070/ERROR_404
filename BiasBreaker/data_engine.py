"""
data_engine.py
Generates synthetic resume data for BiasBreaker.
Each resume has:
  experience  → HP ❤️
  skills      → Attack ⚔️
  education   → Armor 🛡️
  career_gap  → Risk Spike ⚠️
"""

import random
import numpy as np
import pandas as pd

# ── Name pools (diverse, gender-neutral) ──────────────────────────────────────
FIRST_NAMES = [
    "Alex", "Jordan", "Morgan", "Taylor", "Casey", "Riley", "Avery", "Quinn",
    "Skyler", "Drew", "Blake", "Reese", "Hayden", "Cameron", "Peyton",
    "Kendall", "Sage", "Rowan", "Elliot", "Jamie", "Priya", "Aisha",
    "Kenji", "Fatima", "Dmitri", "Zara", "Tariq", "Mei", "Luka", "Nadia",
]
LAST_NAMES = [
    "Chen", "Patel", "Williams", "Johnson", "Rodriguez", "Kim", "Okafor",
    "Singh", "Martinez", "Thompson", "Nguyen", "Brown", "Davis", "Flores",
    "Andersen", "Müller", "Santos", "Ali", "Nakamura", "Ivanova",
    "Osei", "Gupta", "Ferreira", "Larsson", "Hassan",
]

SKILL_POOL = [
    "Python", "SQL", "Machine Learning", "Project Management", "Data Analysis",
    "JavaScript", "Leadership", "Communication", "Agile/Scrum", "Cloud (AWS)",
    "Java", "Excel", "Tableau", "Docker", "Negotiation", "UX Research",
    "Financial Modeling", "R", "TensorFlow", "Public Speaking",
    "C++", "Stakeholder Mgmt", "Cybersecurity", "Product Strategy", "Lean Six Sigma",
    "Kubernetes", "React", "FastAPI", "Spark", "NLP",
]

EDUCATION_MAP = {
    1: "High School",
    2: "Associate's Degree",
    3: "Bachelor's Degree",
    4: "Master's Degree",
    5: "PhD",
}

GAP_REASONS = [
    "Parental Leave",
    "Health Recovery",
    "Further Education",
    "Career Change / Travel",
    "Laid Off / Unemployment",
    "Freelance / Consulting",
]

# Low-risk gap reasons (positive framing)
POSITIVE_GAPS = {"Parental Leave", "Further Education", "Freelance / Consulting"}

BACKSTORY_TEMPLATES = {
    "Parental Leave": [
        "Took {gap:.1f} yr(s) off for parental leave — returned with an online cert in hand.",
        "Primary caregiver for {gap:.1f} yr(s). Kept skills sharp via remote coursework.",
    ],
    "Health Recovery": [
        "Managed a health challenge for {gap:.1f} yr(s); fully cleared with strong references.",
        "Medical leave of {gap:.1f} yr(s). Now back at full capacity.",
    ],
    "Further Education": [
        "Left work for {gap:.1f} yr(s) to earn a graduate degree — graduated top of class.",
        "Full-time study for {gap:.1f} yr(s); earned an industry-recognised certification.",
    ],
    "Career Change / Travel": [
        "Deliberate {gap:.1f}-yr break to pivot industries and gain cross-cultural perspective.",
        "Left corporate life for {gap:.1f} yr(s) of travel and creative projects.",
    ],
    "Laid Off / Unemployment": [
        "Company downsized; {gap:.1f} yr(s) of unemployment — upskilling attempted with mixed results.",
        "Sector downturn led to {gap:.1f} yr(s) out of work.",
    ],
    "Freelance / Consulting": [
        "Ran independent consulting for {gap:.1f} yr(s) — delivered 5 projects across 3 industries.",
        "{gap:.1f} yr(s) of freelance work; strong portfolio available.",
    ],
}


def pick_name(seed: int) -> str:
    rng = random.Random(seed + 7)
    return f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"


def pick_skills(n: int, seed: int) -> list[str]:
    rng = random.Random(seed + 1000)
    return rng.sample(SKILL_POOL, min(int(n), len(SKILL_POOL)))


def _backstory(gap_reason: str, gap_years: float, rng: random.Random) -> str:
    pool = BACKSTORY_TEMPLATES.get(gap_reason, ["No significant gap in career history."])
    return rng.choice(pool).format(gap=gap_years)


def generate_resumes(n: int = 300, seed: int = 42, difficulty: str = "normal") -> pd.DataFrame:
    np.random.seed(seed)
    rng = random.Random(seed)

    experience = np.random.uniform(0, 20, n)
    education  = np.random.choice([1, 2, 3, 4, 5], n)

    if difficulty == "hard":
        skills_count = np.random.randint(2, 6, n)
        gap_years    = np.random.uniform(2, 5, n)
        gap_pool     = ["Laid Off / Unemployment"] * 3 + ["Career Change / Travel"]
    elif difficulty == "easy":
        skills_count = np.random.randint(6, 11, n)
        gap_years    = np.random.uniform(0, 1, n)
        gap_pool     = ["Parental Leave", "Further Education", "Freelance / Consulting"]
    else:
        skills_count = np.random.randint(1, 11, n)
        gap_years    = np.random.uniform(0, 5, n)
        gap_pool     = GAP_REASONS

    gap_reasons, backstories = [], []
    for i, g in enumerate(gap_years):
        reason = "No Gap" if g < 0.1 else rng.choice(gap_pool)
        gap_reasons.append(reason)
        backstories.append(_backstory(reason, g, rng))

    # Merit-based ground truth (NOT biased by name/gender)
    logit   = 0.08 * experience + 0.15 * skills_count - 0.12 * gap_years + 0.2 * education - 1.5
    prob    = 1 / (1 + np.exp(-logit))
    outcome = (prob > 0.5).astype(int)
    noise   = np.random.random(n) < 0.08
    outcome[noise] = 1 - outcome[noise]

    return pd.DataFrame({
        "experience":    experience,
        "skills_count":  skills_count,
        "education":     education,
        "gap_years":     gap_years,
        "gap_reason":    gap_reasons,
        "outcome":       outcome,
        "backstory":     backstories,
        "is_boss":       False,
    })


def make_boss_resume(seed: int = 99) -> dict:
    """Ambiguous boss — high exp, big gap, medium skills. Correct = 2x points."""
    rng = random.Random(seed)
    gap = round(rng.uniform(3.2, 4.5), 1)
    return {
        "experience":   float(rng.uniform(12, 16)),
        "skills_count": rng.randint(4, 6),
        "education":    3,
        "gap_years":    gap,
        "gap_reason":   "Career Change / Travel",
        "outcome":      rng.choice([0, 1]),
        "backstory": (
            f"Left a senior director role after 12 years to consult independently and travel. "
            f"The {gap:.1f}-year gap includes paid freelance work and a startup that didn't scale. "
            "Returns with broad perspective but some erosion in cutting-edge tech skills."
        ),
        "is_boss": True,
    }
