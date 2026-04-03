"""
╔══════════════════════════════════════════════════════════════════════╗
║         HIRE OR FIRE — AI-Powered Hiring Simulator  v2.0            ║
║  Boss Battles · Power-Ups · Limited AI · Dynamic Difficulty · SHAP  ║
╚══════════════════════════════════════════════════════════════════════╝
Run:  streamlit run app.py
Deps: pip install streamlit xgboost shap scikit-learn pandas numpy
"""

import streamlit as st
import numpy as np
import pandas as pd
import random
import shap
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# ═══════════════════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Hire or Fire",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ═══════════════════════════════════════════════════════════
#  GLOBAL STYLES
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Space+Mono:wght@400;700&display=swap');

:root {
    --bg: #0d0d0d;
    --card: #161616;
    --border: #2a2a2a;
    --accent: #f5c518;
    --accent2: #e05c5c;
    --accent3: #4ecdc4;
    --text: #f0f0f0;
    --muted: #888;
    --hire: #22c55e;
    --reject: #ef4444;
    --skip: #f59e0b;
    --boss: #ff6b35;
    --ai: #a78bfa;
}
html, body, [data-testid="stApp"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Space Mono', monospace;
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
.block-container { padding: 1.5rem 1rem 4rem; max-width: 780px; }

/* HUD */
.hud {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 12px;
    font-family: 'Syne', sans-serif;
}
.hud-item { text-align: center; flex: 1; }
.hud-sep  { width: 1px; background: var(--border); align-self: stretch; margin: 0 4px; }
.hud-label { font-size: 9px; letter-spacing: 2px; color: var(--muted); text-transform: uppercase; }
.hud-value { font-size: 20px; font-weight: 800; }
.score-val { color: var(--accent); }
.lives-val { color: var(--accent2); }
.round-val { color: var(--accent3); }
.ai-val    { color: var(--ai); }

/* Progress bar */
.prog-wrap { background: #1e1e1e; border-radius: 6px; height: 5px; margin-bottom: 16px; overflow: hidden; }
.prog-fill { height: 100%; border-radius: 6px; background: linear-gradient(90deg, var(--accent3), var(--accent)); }

/* Boss banner */
.boss-banner {
    background: linear-gradient(135deg, #1a0800, #2d1200);
    border: 2px solid var(--boss);
    border-radius: 10px;
    padding: 11px 20px;
    margin-bottom: 12px;
    text-align: center;
    font-family: 'Syne', sans-serif;
    font-size: 17px;
    font-weight: 800;
    color: var(--boss);
    letter-spacing: 2px;
    animation: bpulse 1.5s ease-in-out infinite;
}
@keyframes bpulse {
    0%,100% { box-shadow: 0 0 18px rgba(255,107,53,.25); }
    50%      { box-shadow: 0 0 38px rgba(255,107,53,.55); }
}

/* Resume card */
.resume-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px 26px;
    margin-bottom: 12px;
    position: relative;
    overflow: hidden;
}
.resume-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--accent3));
}
.resume-card.boss-card {
    border: 2px solid var(--boss) !important;
    background: linear-gradient(160deg, #180d00, #161616) !important;
}
.resume-card.boss-card::before {
    background: linear-gradient(90deg, var(--boss), var(--accent)) !important;
    height: 4px;
}
.candidate-name { font-family: 'Syne', sans-serif; font-size: 23px; font-weight: 800; color: var(--text); margin: 0 0 3px; }
.candidate-title { font-size: 10px; letter-spacing: 3px; color: var(--muted); text-transform: uppercase; margin-bottom: 18px; }
.resume-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 11px; }
.resume-field { background: #1e1e1e; border-radius: 8px; padding: 10px 12px; }
.field-label { font-size: 9px; letter-spacing: 2px; color: var(--muted); text-transform: uppercase; margin-bottom: 3px; }
.field-value { font-size: 14px; font-weight: 700; color: var(--text); }
.skills-box { background: #1e1e1e; border-radius: 8px; padding: 10px 12px; grid-column: span 2; }
.skill-tag {
    display: inline-block;
    background: #2a2a2a; color: var(--accent3);
    border-radius: 4px; font-size: 10px; padding: 2px 7px;
    margin: 2px 2px 2px 0; font-family: 'Space Mono', monospace;
}

/* AI locked placeholder */
.ai-locked {
    background: #12101a; border: 1px dashed #3d3560; border-radius: 10px;
    padding: 13px 16px; margin-bottom: 12px; text-align: center;
    color: #665c99; font-size: 12px; letter-spacing: 1px;
}

/* AI whisper box */
.whisper-box {
    background: #110f1a; border: 1px solid #3d3560;
    border-left: 4px solid var(--ai);
    border-radius: 10px; padding: 15px 18px; margin-bottom: 12px;
}
.whisper-box.warn {
    background: #1a0f11; border: 1px solid #5a2a3a;
    border-left: 4px solid var(--accent2);
}
.whisper-header { font-size: 10px; letter-spacing: 2px; color: var(--muted); text-transform: uppercase; margin-bottom: 7px; }
.whisper-text { font-size: 13px; line-height: 1.7; color: #ccc; }
.prob-bar-bg  { background: #2a2a2a; border-radius: 4px; height: 7px; margin: 9px 0 3px; overflow: hidden; }
.prob-bar-fill { height: 100%; border-radius: 4px; }
.ai-cost-badge {
    display: inline-block; background: #1e1833; border: 1px solid #3d3560;
    color: var(--ai); border-radius: 20px; font-size: 10px;
    padding: 2px 9px; margin-left: 7px; letter-spacing: 1px;
}

/* Power-up panel */
.powerup-panel {
    background: #131313; border: 1px solid #252525;
    border-radius: 12px; padding: 13px 16px; margin-bottom: 12px;
}
.powerup-title { font-size: 9px; letter-spacing: 2px; color: var(--muted); text-transform: uppercase; margin-bottom: 11px; }
.powerup-chip {
    background: #1e1e1e; border: 1px solid #333; border-radius: 8px;
    padding: 7px 10px; font-size: 11px; color: #bbb; text-align: center;
}
.powerup-chip.used { border-color: #222; color: #444; text-decoration: line-through; }
.pu-icon  { font-size: 17px; display: block; margin-bottom: 3px; }
.pu-count { font-size: 9px; letter-spacing: 1px; color: var(--muted); }

/* Result flash */
.result-box {
    border-radius: 10px; padding: 13px 18px; margin-top: 11px;
    font-family: 'Syne', sans-serif; font-size: 15px; font-weight: 700;
    text-align: center; line-height: 1.6;
}
.result-win  { background: #0d2a1a; border: 1px solid var(--hire); color: var(--hire); }
.result-lose { background: #2a0d0d; border: 1px solid var(--reject); color: var(--reject); }
.result-skip { background: #2a200d; border: 1px solid var(--skip); color: var(--skip); }
.result-boss { background: #1a0800; border: 2px solid var(--boss); color: var(--boss); }

/* Game over */
.gameover { text-align: center; padding: 34px 20px; font-family: 'Syne', sans-serif; }
.gameover-title { font-size: 46px; font-weight: 800; line-height: 1; }
.gameover-score { font-size: 72px; font-weight: 800; color: var(--accent); margin: 8px 0; }
.gameover-sub   { font-size: 13px; color: var(--muted); letter-spacing: 2px; }

/* Streamlit buttons */
.stButton > button {
    width: 100%; background: #1e1e1e !important;
    border: 1px solid var(--border) !important; color: var(--text) !important;
    border-radius: 8px !important; font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important; font-size: 12.5px !important; padding: 10px !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover { border-color: var(--accent) !important; color: var(--accent) !important; }

.stat-row { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid var(--border); font-size: 12px; }
.stat-row:last-child { border-bottom: none; }
.stat-key  { color: var(--muted); }
.stat-good { color: var(--hire); font-weight: 700; }
.stat-bad  { color: var(--accent2); font-weight: 700; }
.divider   { border: none; border-top: 1px solid var(--border); margin: 14px 0; }

[data-testid="stExpander"] {
    background: #131313 !important; border: 1px solid #252525 !important;
    border-radius: 8px !important; margin-bottom: 9px !important;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════════
EDUCATION_MAP = {1: "High School", 2: "Associate's", 3: "Bachelor's", 4: "Master's", 5: "PhD"}

SKILL_POOL = [
    "Python","SQL","Machine Learning","Project Management","Data Analysis",
    "JavaScript","Leadership","Communication","Agile/Scrum","Cloud (AWS)",
    "Java","Excel","Tableau","Docker","Negotiation","UX Research",
    "Financial Modeling","R","TensorFlow","Public Speaking",
    "C++","Stakeholder Mgmt","Cybersecurity","Product Strategy","Lean Six Sigma",
]
FIRST_NAMES = ["Alex","Jordan","Morgan","Taylor","Casey","Riley","Avery","Quinn",
               "Skyler","Drew","Blake","Reese","Hayden","Cameron","Peyton",
               "Kendall","Sage","Rowan","Elliot","Jamie"]
LAST_NAMES  = ["Chen","Patel","Williams","Johnson","Rodriguez","Kim","Okafor",
               "Singh","Martinez","Thompson","Nguyen","Brown","Davis","Flores",
               "Andersen","Müller","Santos","Ali","Nakamura","Ivanova"]

SCORE_RULES = {
    "correct":      10,
    "wrong_reject": -15,
    "wrong_hire":   -5,
    "ai_bonus":     20,
    "skip_penalty": -3,
    "bias_penalty": -10,
    "ai_hint_cost": -3,   # ← NEW: deducted when AI hint is used
}

# Backstory templates per gap reason
BACKSTORY_TEMPLATES = {
    "No gap": [
        "Maintained an unbroken career trajectory, taking on progressively larger roles.",
        "Fully employed throughout; known for reliability and consistent output.",
    ],
    "Parental leave": [
        "Took {gap:.1f} year(s) of parental leave; used the time to earn an online certification.",
        "Stepped back for {gap:.1f} year(s) to care for a newborn; returned more organised and motivated.",
    ],
    "Health break": [
        "A health challenge required {gap:.1f} year(s) away; now fully recovered with clearance to work.",
        "Managed a personal health issue for {gap:.1f} year(s); strong references available.",
    ],
    "Skill decay / unemployment": [
        "Laid off during a sector downturn, struggled with {gap:.1f} year(s) of unemployment.",
        "Company closure led to {gap:.1f} year(s) out of work; upskilling attempted with mixed results.",
    ],
    "Career change / travel": [
        "Left a corporate role to travel for {gap:.1f} year(s); returns with cross-cultural perspective.",
        "Deliberate career break of {gap:.1f} year(s) to pivot industries; brings fresh thinking.",
    ],
    "Further education": [
        "Enrolled full-time for {gap:.1f} year(s) to complete a graduate degree; graduated with distinction.",
        "Stepped out of the workforce for {gap:.1f} year(s) to earn an industry-recognised qualification.",
    ],
}
POSITIVE_GAP_REASONS = {"Parental leave", "Further education", "Career change / travel"}

# ═══════════════════════════════════════════════════════════
#  DATA GENERATION
# ═══════════════════════════════════════════════════════════
def _backstory(gap_reason: str, gap_years: float, rng: random.Random) -> str:
    pool = BACKSTORY_TEMPLATES.get(gap_reason, BACKSTORY_TEMPLATES["No gap"])
    return rng.choice(pool).format(gap=gap_years)


def generate_synthetic_data(n: int = 300, seed: int = 42, difficulty: str = "normal") -> pd.DataFrame:
    np.random.seed(seed)
    rng = random.Random(seed)

    if difficulty == "hard":
        skills_count  = np.random.randint(2, 6, n)
        gap_years     = np.random.uniform(2, 5, n)
        reason_pool   = ["Skill decay / unemployment"] * 3 + ["Career change / travel"]
    elif difficulty == "easy":
        skills_count  = np.random.randint(6, 11, n)
        gap_years     = np.random.uniform(0, 1, n)
        reason_pool   = ["Parental leave", "Further education", "No gap", "No gap"]
    else:
        skills_count  = np.random.randint(1, 11, n)
        gap_years     = np.random.uniform(0, 5, n)
        reason_pool   = ["Parental leave","Health break","Skill decay / unemployment",
                         "Career change / travel","Further education"]

    experience      = np.random.uniform(0, 20, n)
    education_level = np.random.choice([1,2,3,4,5], n)

    gap_reasons, backstories = [], []
    for i, g in enumerate(gap_years):
        reason = "No gap" if g < 0.1 else rng.choice(reason_pool)
        gap_reasons.append(reason)
        backstories.append(_backstory(reason, g, rng))

    logit   = 0.08*experience + 0.15*skills_count - 0.12*gap_years + 0.2*education_level - 1.5
    prob    = 1 / (1 + np.exp(-logit))
    outcome = (prob > 0.5).astype(int)
    noise   = np.random.random(n) < 0.1
    outcome[noise] = 1 - outcome[noise]

    return pd.DataFrame({
        "experience": experience, "skills_count": skills_count,
        "gap_years": gap_years,   "gap_reason": gap_reasons,
        "education_level": education_level, "outcome": outcome,
        "backstory": backstories,
    })


def make_boss_resume(seed: int = 99) -> dict:
    """High exp + big gap + medium skills → ambiguous 45-55 % confidence."""
    rng = random.Random(seed)
    return {
        "experience":      float(rng.uniform(12, 16)),
        "skills_count":    rng.randint(4, 6),
        "gap_years":       float(rng.uniform(3.2, 4.5)),
        "gap_reason":      "Career change / travel",
        "education_level": 3,
        "outcome":         rng.choice([0, 1]),
        "backstory": (
            "Left a senior role after 12 years to consult independently and travel. "
            "The 3+ year gap includes paid freelance work and a startup that did not scale. "
            "Returns with broad perspective but some erosion in fast-moving tech skills."
        ),
        "is_boss": True,
    }

# ═══════════════════════════════════════════════════════════
#  MODEL TRAINING  (cached once)
# ═══════════════════════════════════════════════════════════
FEATURE_COLS = ["experience","skills_count","gap_years","education_level"]

@st.cache_resource
def train_model():
    df   = generate_synthetic_data(300)
    X, y = df[FEATURE_COLS], df["outcome"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    model = xgb.XGBClassifier(
        n_estimators=150, max_depth=4, learning_rate=0.1,
        subsample=0.8, use_label_encoder=False,
        eval_metric="logloss", random_state=42,
    )
    model.fit(Xtr, ytr)
    acc       = accuracy_score(yte, model.predict(Xte))
    explainer = shap.TreeExplainer(model)
    return model, explainer, round(acc, 3)

# ═══════════════════════════════════════════════════════════
#  PREDICTION  +  SHAP WHISPER
# ═══════════════════════════════════════════════════════════
def predict_candidate(model, explainer, row: dict):
    X         = pd.DataFrame([{c: row[c] for c in FEATURE_COLS}])
    prob      = float(model.predict_proba(X)[0][1])
    pred      = int(model.predict(X)[0])
    shap_vals = explainer.shap_values(X)[0]
    return prob, pred, shap_vals


def build_whisper(prob: float, pred: int, shap_vals, row: dict) -> str:
    feat_names = {
        "experience": "years of experience", "skills_count": "skill breadth",
        "gap_years":  "career gap",          "education_level": "education level",
    }
    pairs = sorted(zip(FEATURE_COLS, shap_vals), key=lambda x: abs(x[1]), reverse=True)
    parts = []
    for feat, sv in pairs[:3]:
        if abs(sv) < 0.05:
            continue
        parts.append(
            f"Strong {feat_names[feat]} boosts hire probability." if sv > 0
            else f"Weak {feat_names[feat]} lowers hire probability."
        )
    if row.get("gap_reason","") in POSITIVE_GAP_REASONS:
        parts.append("The model detects high motivation from the candidate's backstory.")
    rec  = "✅ Recommended: HIRE" if pred == 1 else "⛔ Recommended: REJECT"
    conf = "High confidence." if abs(prob - 0.5) > 0.25 else "Borderline case — trust your gut."
    body = " ".join(parts) if parts else "Mixed signals across all factors."
    return f"{rec}  {conf}\n\n{body}"

# ═══════════════════════════════════════════════════════════
#  RESUME CARD
# ═══════════════════════════════════════════════════════════
def make_name(i: int) -> str:
    rng = random.Random(i + 7)
    return f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"

def pick_skills(n: int, i: int) -> list:
    rng = random.Random(i + 1000)
    return rng.sample(SKILL_POOL, min(int(n), len(SKILL_POOL)))

def render_resume_card(row: dict, idx: int):
    is_boss  = row.get("is_boss", False)
    name     = make_name(idx)
    skills   = pick_skills(int(row["skills_count"]), idx)
    edu      = EDUCATION_MAP[int(row["education_level"])]
    exp_str  = f"{row['experience']:.1f} years"
    gap      = (f"{row['gap_years']:.1f} yrs ({row['gap_reason']})"
                if row["gap_years"] >= 0.1 else "None")
    tags     = "".join(f'<span class="skill-tag">{s}</span>' for s in skills)
    cls      = "resume-card boss-card" if is_boss else "resume-card"

    st.markdown(f"""
    <div class="{cls}">
      <div class="candidate-name">{name}</div>
      <div class="candidate-title">Candidate #{idx+1} · Resume Review</div>
      <div class="resume-grid">
        <div class="resume-field"><div class="field-label">Experience</div>
          <div class="field-value">{exp_str}</div></div>
        <div class="resume-field"><div class="field-label">Education</div>
          <div class="field-value">{edu}</div></div>
        <div class="resume-field"><div class="field-label">Career Gap</div>
          <div class="field-value" style="font-size:12px">{gap}</div></div>
        <div class="resume-field"><div class="field-label">Skills</div>
          <div class="field-value">{int(row['skills_count'])}</div></div>
        <div class="skills-box"><div class="field-label">Skill Set</div>
          <div style="margin-top:5px">{tags}</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Backstory expander (NEW)
    bs = row.get("backstory","")
    if bs:
        with st.expander("📖 Read candidate's story"):
            st.markdown(f'<div style="font-size:13px;color:#ccc;line-height:1.8">{bs}</div>',
                        unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
#  WHISPER RENDER
# ═══════════════════════════════════════════════════════════
def render_whisper(prob: float, pred: int, whisper: str):
    pct     = int(prob * 100)
    col     = "#a78bfa" if abs(prob-.5)<.05 else ("#22c55e" if prob>=.5 else "#ef4444")
    box_cls = "whisper-box" if pred == 1 else "whisper-box warn"
    hw      = whisper.replace("\n\n","<br><br>").replace("\n","<br>")
    st.markdown(f"""
    <div class="{box_cls}">
      <div class="whisper-header">🤖 &nbsp;AI WHISPER
        <span class="ai-cost-badge">–3 pts used</span>
      </div>
      <div class="whisper-text">{hw}</div>
      <div class="prob-bar-bg">
        <div class="prob-bar-fill" style="width:{pct}%;background:{col}"></div>
      </div>
      <div style="font-size:11px;color:var(--muted);letter-spacing:1px;">
        HIRE PROBABILITY: <strong style="color:{col}">{pct}%</strong>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
#  HUD  (now includes AI Hints counter)
# ═══════════════════════════════════════════════════════════
def render_hud():
    lives_icons = "❤️" * st.session_state.lives + "🖤" * (3 - st.session_state.lives)
    ai_left     = st.session_state.ai_uses
    ai_icons    = "🤖" * ai_left + "⬜" * (3 - ai_left)
    ai_col      = "var(--ai)" if ai_left > 0 else "var(--muted)"
    total       = len(st.session_state.resumes)
    curr        = st.session_state.round_idx + 1
    pct         = int((st.session_state.round_idx / total) * 100)

    st.markdown(f"""
    <div class="hud">
      <div class="hud-item">
        <div class="hud-label">Score</div>
        <div class="hud-value score-val">{st.session_state.score}</div>
      </div>
      <div class="hud-sep"></div>
      <div class="hud-item">
        <div class="hud-label">Lives</div>
        <div class="hud-value lives-val" style="font-size:16px">{lives_icons}</div>
      </div>
      <div class="hud-sep"></div>
      <div class="hud-item">
        <div class="hud-label">Round</div>
        <div class="hud-value round-val">{curr}/{total}</div>
      </div>
      <div class="hud-sep"></div>
      <div class="hud-item">
        <div class="hud-label">AI Hints</div>
        <div class="hud-value" style="color:{ai_col};font-size:16px">{ai_icons}</div>
      </div>
    </div>
    <div class="prog-wrap"><div class="prog-fill" style="width:{pct}%"></div></div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
#  POWER-UPS  (NEW)
# ═══════════════════════════════════════════════════════════
_PU_META = {
    "second_look": ("🔍", "Second Look", "Re-reveal AI whisper"),
    "bias_shield": ("🛡️", "Bias Shield",  "Block next bias penalty"),
    "lucky_charm": ("🍀", "Lucky Charm",  "+10 if you follow AI"),
}

def render_powerup_panel() -> str | None:
    """Renders power-up chips + use buttons. Returns activated key or None."""
    pu        = st.session_state.powerups
    activated = None

    st.markdown('<div class="powerup-panel">'
                '<div class="powerup-title">⚡ Power-Ups</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for col, (key, (icon, name, desc)) in zip(cols, _PU_META.items()):
        count = pu[key]
        with col:
            chip_cls = "used" if count == 0 else ""
            st.markdown(f"""
            <div class="powerup-chip {chip_cls}">
              <span class="pu-icon">{icon}</span>
              <b>{name}</b><br>
              <span class="pu-count">{'Available' if count>0 else 'Used'}</span>
            </div>
            """, unsafe_allow_html=True)
            if count > 0:
                if st.button(f"{icon} Use", key=f"pu_{key}", use_container_width=True):
                    activated = key
    st.markdown('</div>', unsafe_allow_html=True)
    return activated

# ═══════════════════════════════════════════════════════════
#  SCORING ENGINE  (updated for shield / charm / boss)
# ═══════════════════════════════════════════════════════════
def compute_score_delta(
    action: str, outcome: int, ai_pred: int, row: dict,
    shield: bool = False, charm: bool = False, is_boss: bool = False,
) -> tuple[int, str, bool]:
    """Returns (delta, message_string, correct_bool)."""
    delta, msgs = 0, []

    if action == "skip":
        delta += SCORE_RULES["skip_penalty"]
        return delta, f"Skipped ({SCORE_RULES['skip_penalty']} pts)", False

    hired   = action == "hire"
    correct = (hired and outcome==1) or (not hired and outcome==0)

    # Base
    if hired and outcome==1:
        delta += SCORE_RULES["correct"];      msgs.append(f"✅ Correct Hire +{SCORE_RULES['correct']}")
    elif not hired and outcome==0:
        delta += SCORE_RULES["correct"];      msgs.append(f"✅ Correct Reject +{SCORE_RULES['correct']}")
    elif hired and outcome==0:
        delta += SCORE_RULES["wrong_hire"];   msgs.append(f"❌ Wrong Hire {SCORE_RULES['wrong_hire']}")
    else:
        delta += SCORE_RULES["wrong_reject"]; msgs.append(f"❌ Wrong Reject {SCORE_RULES['wrong_reject']}")

    # AI bonus — only when hint was used this round AND player followed AI
    followed_ai = (hired == (ai_pred == 1))
    if st.session_state.get("_hint_used_this_round", False) and followed_ai:
        delta += SCORE_RULES["ai_bonus"]
        msgs.append(f"🤖 Followed AI +{SCORE_RULES['ai_bonus']}")

    # Lucky Charm: +10 if followed AI regardless of correctness
    if charm and followed_ai:
        delta += 10
        msgs.append("🍀 Lucky Charm +10")

    # Bias penalty
    if not hired and row.get("gap_years",0) < 1.0 and outcome == 1:
        if shield:
            msgs.append("🛡️ Bias Shield blocked penalty!")
        else:
            delta += SCORE_RULES["bias_penalty"]
            msgs.append(f"⚠️ Bias Penalty {SCORE_RULES['bias_penalty']}")

    # Boss: double points on correct decision
    if is_boss and correct:
        delta *= 2
        msgs.append("🔥 BOSS x2!")

    return delta, " | ".join(msgs), correct

# ═══════════════════════════════════════════════════════════
#  SESSION STATE INIT
# ═══════════════════════════════════════════════════════════
def init_state():
    if "game_started" not in st.session_state:
        st.session_state.update({
            "game_started":  False,
            "round_idx":     0,
            "score":         0,
            "lives":         3,
            "game_over":     False,
            "resumes":       [],
            "awaiting_next": False,
            "last_result":   None,
            "history":       [],
            "skips_used":    0,
            # ── NEW: limited AI hints ──────────────────────
            "ai_uses":       3,
            "hint_shown":    False,
            "_hint_used_this_round": False,
            # ── NEW: power-ups ────────────────────────────
            "powerups": {"second_look": 1, "bias_shield": 1, "lucky_charm": 1},
            "bias_shield_active": False,
            "lucky_charm_active": False,
            # ── NEW: achievement flags ─────────────────────
            "ach_guru":     False,
            "ach_flawless": False,
            "boss_correct": False,
        })

# ═══════════════════════════════════════════════════════════
#  DYNAMIC DIFFICULTY  (NEW)
# ═══════════════════════════════════════════════════════════
def maybe_adjust_difficulty():
    """After round 5 completes, replace resumes 6-9 based on score. Boss (index 9) unchanged."""
    if st.session_state.round_idx != 5:
        return
    score = st.session_state.score
    if score > 100:
        diff = "hard"
    elif score < 20:
        diff = "easy"
    else:
        return  # normal — no change
    new_df  = generate_synthetic_data(60, seed=random.randint(0, 9999), difficulty=diff)
    new_rows = new_df.sample(4, random_state=random.randint(0,9999)).to_dict("records")
    resumes  = st.session_state.resumes
    resumes[5:9] = new_rows
    st.session_state.resumes = resumes
    label = "harder" if diff == "hard" else "easier"
    st.toast(f"📈 Difficulty adjusted! Remaining resumes are {label}.", icon="⚡")

# ═══════════════════════════════════════════════════════════
#  ACHIEVEMENT CHECKS  (NEW)
# ═══════════════════════════════════════════════════════════
def check_achievements():
    if st.session_state.score >= 200 and not st.session_state.ach_guru:
        st.session_state.ach_guru = True
        st.toast("🏆 Achievement Unlocked: Hiring Guru!", icon="🏆")
    if (st.session_state.boss_correct and st.session_state.lives == 3
            and not st.session_state.ach_flawless):
        st.session_state.ach_flawless = True
        st.toast("⚡ Flawless Victory! Beat the boss with full health!", icon="⚡")

# ═══════════════════════════════════════════════════════════
#  GAME OVER SCREEN
# ═══════════════════════════════════════════════════════════
def render_game_over():
    score       = st.session_state.score
    hist        = st.session_state.history
    correct_ct  = sum(1 for h in hist if h.get("correct"))
    ai_followed = sum(1 for h in hist if h.get("followed_ai"))
    ai_used     = 3 - st.session_state.ai_uses

    if   score >= 250: title, emoji = "LEGENDARY HR!",  "🏆"
    elif score >= 150: title, emoji = "GREAT HIRING!",  "🎯"
    elif score >= 60:  title, emoji = "DECENT RUN",     "👔"
    else:              title, emoji = "NEEDS WORK",     "💼"

    st.markdown(f"""
    <div class="gameover">
      <div style="font-size:52px">{emoji}</div>
      <div class="gameover-title">{title}</div>
      <div class="gameover-score">{score}</div>
      <div class="gameover-sub">FINAL SCORE</div>
    </div>
    """, unsafe_allow_html=True)

    badges = []
    if st.session_state.ach_guru:     badges.append("🏆 Hiring Guru")
    if st.session_state.ach_flawless: badges.append("⚡ Flawless Victory")
    if badges:
        st.markdown(
            f'<div style="text-align:center;font-size:13px;color:#f5c518;margin-bottom:10px;">'
            + "  ·  ".join(badges) + "</div>",
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("**📊 Session Breakdown**")
    for label, val, cls in [
        ("Rounds played",     len(hist),         ""),
        ("Correct decisions", correct_ct,         "good"),
        ("Wrong decisions",   len(hist)-correct_ct, "bad"),
        ("AI hints used",     ai_used,            ""),
        ("Times followed AI", ai_followed,        "good"),
        ("Skips used",        st.session_state.skips_used, ""),
    ]:
        ch = f'class="stat-{cls}"' if cls else ""
        st.markdown(
            f'<div class="stat-row"><span class="stat-key">{label}</span>'
            f'<span {ch}>{val}</span></div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    if st.button("🔄  Play Again", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ═══════════════════════════════════════════════════════════
#  SPLASH SCREEN
# ═══════════════════════════════════════════════════════════
def render_splash(acc: float):
    st.markdown("""
    <div style="text-align:center;padding:26px 0 8px;font-family:'Syne',sans-serif;">
      <div style="font-size:56px">🎯</div>
      <div style="font-size:40px;font-weight:800;letter-spacing:-1px;">HIRE OR FIRE</div>
      <div style="font-size:10px;letter-spacing:4px;color:#888;margin:5px 0 20px;">
        AI-POWERED HIRING SIMULATOR · v2.0
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#161616;border:1px solid #2a2a2a;border-radius:12px;
                padding:17px 21px;margin-bottom:16px;font-size:12.5px;line-height:1.9;color:#ccc;">
      <b style="color:#f5c518;font-family:'Syne',sans-serif;">HOW TO PLAY</b><br><br>
      Review 10 resumes. Choose: <b>Hire · Reject · Skip</b>.<br><br>
      🤖 <b>AI Hints are scarce — only 3 per game.</b> Each use costs –3 pts but reveals
         SHAP-powered advice and unlocks the +20 AI-follow bonus.<br><br>
      ⚡ <b>Power-Ups (one-time each):</b> 🔍 Second Look · 🛡️ Bias Shield · 🍀 Lucky Charm<br>
      🔥 <b>Round 10 is the BOSS</b> — correct decision earns double points!<br>
      📈 <b>Difficulty adjusts</b> after round 5 based on your score.<br><br>
      <b>Score rules:</b> Correct ±10 · Wrong hire –5 · Wrong reject –15<br>
      Follow AI +20 · Bias penalty –10 · Skip –3 · AI hint –3<br><br>
      ❤️ 3 lives · Wrong decision costs a life · 0 lives = Game Over<br><br>
      <span style="font-size:11px;color:#555;">XGBoost model accuracy on test set: {int(acc*100)}%</span>
    </div>
    """, unsafe_allow_html=True)

    _, c, _ = st.columns([1,2,1])
    with c:
        if st.button("▶  START GAME", use_container_width=True):
            base    = generate_synthetic_data(300, seed=random.randint(0,9999))
            sampled = base.sample(9, random_state=random.randint(0,9999)).reset_index(drop=True)
            boss    = make_boss_resume(seed=random.randint(0,999))
            st.session_state.resumes      = sampled.to_dict("records") + [boss]
            st.session_state.game_started = True
            st.rerun()

# ═══════════════════════════════════════════════════════════
#  MAIN GAME LOOP
# ═══════════════════════════════════════════════════════════
def run_game(model, explainer):
    resumes   = st.session_state.resumes
    round_idx = st.session_state.round_idx

    if round_idx >= len(resumes):
        st.session_state.game_over = True
        st.rerun()

    row     = resumes[round_idx]
    is_boss = row.get("is_boss", False)

    # Boss banner
    if is_boss:
        st.markdown('<div class="boss-banner">🔥 FINAL BOSS RESUME 🔥</div>', unsafe_allow_html=True)

    render_hud()
    render_resume_card(row, round_idx)

    # Pre-compute prediction once per round (keyed by round index)
    if st.session_state.get("_pred_round") != round_idx:
        prob, ai_pred, shap_vals = predict_candidate(model, explainer, row)
        whisper = build_whisper(prob, ai_pred, shap_vals, row)
        st.session_state.update({
            "_prob": prob, "_ai_pred": ai_pred, "_whisper": whisper,
            "_pred_round": round_idx,
            # reset per-round flags
            "hint_shown": False,
            "_hint_used_this_round": False,
            "bias_shield_active": False,
            "lucky_charm_active": False,
        })
    else:
        prob    = st.session_state["_prob"]
        ai_pred = st.session_state["_ai_pred"]
        whisper = st.session_state["_whisper"]

    # ── Post-action result (awaiting "next" click) ────────
    if st.session_state.awaiting_next and st.session_state.last_result:
        res = st.session_state.last_result
        bos = res.get("is_boss") and res.get("correct")
        box = ("result-box result-boss" if bos
               else "result-box result-win"  if res["delta"] > 0
               else "result-box result-skip" if res["action"]=="skip"
               else "result-box result-lose")
        msg_h = res["msg"].replace("\n","<br>")
        st.markdown(f'<div class="{box}">{msg_h}</div>', unsafe_allow_html=True)
        actual = "✅ Good Hire" if res["outcome"]==1 else "❌ Bad Hire"
        st.markdown(
            f'<div style="text-align:center;color:#888;font-size:12px;margin-top:7px;">'
            f'Actual outcome: <b style="color:#f0f0f0">{actual}</b></div>',
            unsafe_allow_html=True)

        check_achievements()

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        if st.button("→  Next Candidate", use_container_width=True):
            st.session_state.awaiting_next = False
            st.session_state.last_result   = None
            st.session_state.round_idx    += 1
            maybe_adjust_difficulty()
            if st.session_state.round_idx >= len(resumes):
                st.session_state.game_over = True
            st.rerun()
        return

    # ════════════════════════════════════════════════════════
    #  ★ AI HINT SECTION (NEW — limited strategic resource) ★
    # ════════════════════════════════════════════════════════
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    if st.session_state.hint_shown:
        # Whisper already unlocked this round — display it
        render_whisper(prob, ai_pred, whisper)
    else:
        ai_left = st.session_state.ai_uses
        if ai_left > 0:
            # Show the USE AI HINT button
            if st.button(
                f"🤖  Use AI Hint  ({ai_left} remaining  ·  costs –3 pts)",
                use_container_width=True,
            ):
                # ── Deduct cost + consume one use ────────
                st.session_state.ai_uses              -= 1
                st.session_state.score                += SCORE_RULES["ai_hint_cost"]
                st.session_state.hint_shown            = True
                st.session_state["_hint_used_this_round"] = True
                st.rerun()
        else:
            # All hints exhausted
            st.markdown(
                '<div class="ai-locked">'
                '🔒 No AI hints remaining — trust your instincts!'
                '</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    #  ★ POWER-UPS PANEL (NEW) ★
    # ════════════════════════════════════════════════════════
    activated = render_powerup_panel()

    if activated == "second_look":
        # Force-reveal whisper (counts as hint-used for AI bonus)
        st.session_state.powerups["second_look"]      = 0
        st.session_state.hint_shown                   = True
        st.session_state["_hint_used_this_round"]     = True
        st.rerun()

    if activated == "bias_shield":
        st.session_state.powerups["bias_shield"]      = 0
        st.session_state.bias_shield_active           = True
        st.toast("🛡️ Bias Shield active for this resume!", icon="🛡️")
        st.rerun()

    if activated == "lucky_charm":
        st.session_state.powerups["lucky_charm"]      = 0
        st.session_state.lucky_charm_active           = True
        st.toast("🍀 Lucky Charm active — follow AI for +10!", icon="🍀")
        st.rerun()

    # ════════════════════════════════════════════════════════
    #  ACTION BUTTONS
    # ════════════════════════════════════════════════════════
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    action = None
    with c1:
        if st.button("✅  HIRE",   use_container_width=True): action = "hire"
    with c2:
        if st.button("❌  REJECT", use_container_width=True): action = "reject"
    with c3:
        if st.button("⏭  SKIP",   use_container_width=True): action = "skip"

    if action:
        outcome = int(row["outcome"])
        delta, msg, correct = compute_score_delta(
            action, outcome, ai_pred, row,
            shield=st.session_state.bias_shield_active,
            charm=st.session_state.lucky_charm_active,
            is_boss=is_boss,
        )

        # Boss-specific result message
        if is_boss and correct:
            st.session_state.boss_correct = True
            msg = "BOSS DEFEATED! Double Points! 🔥\n" + msg

        st.session_state.score += delta

        # Life loss on incorrect non-skip decision
        if action != "skip" and not correct:
            st.session_state.lives -= 1

        if action == "skip":
            st.session_state.skips_used += 1

        followed_ai = (action == "hire") == (ai_pred == 1) if action != "skip" else False

        st.session_state.history.append({
            "round":       round_idx,
            "action":      action,
            "outcome":     outcome,
            "correct":     correct,
            "followed_ai": followed_ai,
            "delta":       delta,
        })

        st.session_state.last_result = {
            "action":  action,
            "delta":   delta,
            "msg":     msg,
            "outcome": outcome,
            "correct": correct,
            "is_boss": is_boss,
        }
        st.session_state.awaiting_next = True

        if st.session_state.lives <= 0:
            st.session_state.game_over = True

        st.rerun()

# ═══════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════
def main():
    init_state()
    model, explainer, acc = train_model()

    if st.session_state.game_over:
        render_game_over()
        return
    if not st.session_state.game_started:
        render_splash(acc)
        return

    run_game(model, explainer)


if __name__ == "__main__":
    main()