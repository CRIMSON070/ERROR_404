"""
components/candidate_card.py
═══════════════════════════════════════════════════════════
Standalone candidate card renderer.
Exported for optional direct use outside app.py.
═══════════════════════════════════════════════════════════
"""

import streamlit as st
from data_engine import pick_name, pick_skills, EDUCATION_MAP


def edu_armor(level: int) -> int:
    return {1: 10, 2: 20, 3: 40, 4: 70, 5: 90}.get(level, 30)


def hp_color(pct: float) -> str:
    if pct >= 0.7: return "#22c55e"
    if pct >= 0.4: return "#f5c518"
    return "#ef4444"


def render_candidate_card(row: dict, idx: int, blind: bool = False):
    """
    Renders the full candidate monster card.

    Args:
        row   (dict): Candidate feature dict
        idx   (int):  Round index (used for name seed)
        blind (bool): If True, hide education and name
    """
    is_boss = row.get("is_boss", False)

    name    = "???" if blind else pick_name(idx)
    edu_lv  = int(row["education"])
    edu_str = "???" if blind else EDUCATION_MAP.get(edu_lv, "Bachelor's Degree")

    skills  = pick_skills(int(row["skills_count"]), idx)
    exp     = row["experience"]
    gap     = row["gap_years"]
    gap_r   = row.get("gap_reason", "No Gap")
    gap_str = f"{gap:.1f} yrs — {gap_r}" if gap >= 0.1 else "None"

    hp_pct    = min(exp / 20, 1.0)
    atk_pct   = min(int(row["skills_count"]) / 10, 1.0)
    armor_pct = edu_armor(edu_lv) / 100
    risk_pct  = min(gap / 5, 1.0)

    hp_col    = hp_color(hp_pct)
    atk_col   = "#38bdf8"
    armor_col = "#a855f7"
    risk_col  = "#f97316" if risk_pct > 0.4 else "#22c55e"

    tags     = "".join(f'<span class="skill-tag">{s}</span>' for s in skills)
    card_cls = "monster-card boss-card" if is_boss else "monster-card glass-container"
    card_type = "👹 BOSS CANDIDATE" if is_boss else "⚔️ CANDIDATE CARD"

    st.markdown(f"""
    <div class="{card_cls} {'neon-border-gold' if is_boss else ''}">
      <div class="card-header">
        <div class="card-banner"></div>
        <div class="card-type">{card_type} · #{idx+1}</div>
        <div class="candidate-name">{name}</div>
        <div class="candidate-sub">{'🕶️ BLIND MODE — Name & Education Hidden' if blind else 'Resume Review · Round ' + str(idx+1)}</div>
      </div>

      <div class="card-stats">
        <div class="stat-box">
          <div class="stat-icon">❤️</div>
          <div class="stat-label">Experience · HP</div>
          <div class="stat-value">{exp:.1f} years</div>
          <div class="stat-bar-wrap">
            <div class="stat-bar-fill" style="width:{int(hp_pct*100)}%;background:{hp_col}"></div>
          </div>
        </div>
        <div class="stat-box">
          <div class="stat-icon">⚔️</div>
          <div class="stat-label">Skills · Attack</div>
          <div class="stat-value">{int(row['skills_count'])} skills</div>
          <div class="stat-bar-wrap">
            <div class="stat-bar-fill" style="width:{int(atk_pct*100)}%;background:{atk_col}"></div>
          </div>
        </div>
        <div class="stat-box">
          <div class="stat-icon">🛡️</div>
          <div class="stat-label">Education · Armor</div>
          <div class="stat-value">{edu_str}</div>
          <div class="stat-bar-wrap">
            <div class="stat-bar-fill" style="width:{int(armor_pct*100) if not blind else 0}%;background:{armor_col}"></div>
          </div>
        </div>
        <div class="stat-box">
          <div class="stat-icon">⚠️</div>
          <div class="stat-label">Career Gap · Risk</div>
          <div class="stat-value" style="font-size:12px">{gap_str}</div>
          <div class="stat-bar-wrap">
            <div class="stat-bar-fill" style="width:{int(risk_pct*100)}%;background:{risk_col}"></div>
          </div>
        </div>
      </div>

      <div class="card-skills">
        <div class="skills-label">⚡ Skill Arsenal</div>
        <div>{tags}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    bs = row.get("backstory", "")
    if bs and not blind:
        with st.expander("📖 Candidate Backstory"):
            st.markdown(
                f'<div style="font-size:13px;color:#b0b0c8;line-height:1.9;'
                f'font-family:Rajdhani,sans-serif">{bs}</div>',
                unsafe_allow_html=True,
            )
