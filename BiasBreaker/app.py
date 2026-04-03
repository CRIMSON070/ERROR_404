"""
app.py  —  BiasBreaker: The Hiring Game
Run:  streamlit run app.py
"""

import streamlit as st
import streamlit.components.v1 as components
import random

from data_engine import (
    pick_name, pick_skills, EDUCATION_MAP, POSITIVE_GAPS, generate_resumes, make_boss_resume
)
from ml_engine import train_model, predict, build_whisper, retrain_with_decisions
from ollama_client import get_ai_whisper_llm, ollama_available, ollama_feedback, ollama_career_coach
from game_state import (
    init_state, start_game, compute_score,
    save_leaderboard, load_leaderboard, analyze_bias, evaluate_skill_gaps
)

# ══════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="BiasBreaker: The Hiring Game",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════
#  GLOBAL STYLES  (dark cyberpunk/fantasy theme)
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;900&family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&display=swap');

:root {
  --bg:       #06060f;
  --bg2:      #0c0c1e;
  --card:     #10101f;
  --card2:    #14142a;
  --border:   #1e1e3a;
  --gold:     #f5c518;
  --gold2:    #ffd700;
  --purple:   #a855f7;
  --purple2:  #7c3aed;
  --blue:     #38bdf8;
  --blue2:    #0ea5e9;
  --red:      #ef4444;
  --green:    #22c55e;
  --orange:   #f97316;
  --text:     #e8e8f0;
  --muted:    #6b6b8a;
  --hire-glow: 0 0 30px rgba(34,197,94,0.5), 0 0 60px rgba(34,197,94,0.2);
  --reject-glow: 0 0 30px rgba(239,68,68,0.5), 0 0 60px rgba(239,68,68,0.2);
  --ai-glow:  0 0 30px rgba(168,85,247,0.5), 0 0 60px rgba(168,85,247,0.2);
  --boss-glow: 0 0 40px rgba(249,115,22,0.6), 0 0 80px rgba(249,115,22,0.25);
  --gold-glow: 0 0 40px rgba(245,197,24,0.6);
}

html, body, [data-testid="stApp"] {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Rajdhani', sans-serif !important;
}
#MainMenu, footer, header { visibility: hidden !important; }
[data-testid="stToolbar"] { display: none !important; }
.block-container { padding: 1rem 0.8rem 4rem; max-width: 820px; }

/* ── Scrollbar ─────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--purple2); border-radius: 3px; }

/* ── Animations ─────────────────────────────────────────── */
@keyframes floatIn {
  from { opacity:0; transform: translateY(30px) scale(0.95); }
  to   { opacity:1; transform: translateY(0)    scale(1); }
}
@keyframes hireGlow {
  0%,100% { box-shadow: 0 0 0 rgba(34,197,94,0); }
  50%      { box-shadow: var(--hire-glow); }
}
@keyframes rejectShake {
  0%,100%{ transform:translateX(0); }
  20%    { transform:translateX(-8px) rotate(-1deg); }
  40%    { transform:translateX(8px)  rotate(1deg); }
  60%    { transform:translateX(-6px); }
  80%    { transform:translateX(6px); }
}
@keyframes aiPulse {
  0%,100% { box-shadow: 0 0 0 rgba(168,85,247,0); }
  50%      { box-shadow: var(--ai-glow); }
}
@keyframes bossPulse {
  0%,100% { box-shadow: var(--boss-glow); }
  50%      { box-shadow: 0 0 20px rgba(249,115,22,0.3); }
}
@keyframes goldShimmer {
  0%   { background-position: -100% 0; }
  100% { background-position: 200% 0; }
}
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fadeSlideIn {
  from { opacity:0; transform:translateX(20px); }
  to   { opacity:1; transform:translateX(0); }
}
@keyframes streakPop {
  0%   { transform: scale(1); }
  50%  { transform: scale(1.3); }
  100% { transform: scale(1); }
}
@keyframes titleGlow {
  0%,100% { text-shadow: 0 0 20px rgba(245,197,24,0.4); }
  50%      { text-shadow: 0 0 50px rgba(245,197,24,0.9), 0 0 80px rgba(168,85,247,0.4); }
}

/* ── HUD ────────────────────────────────────────────────── */
.hud-bar {
  display: flex; justify-content: space-between; align-items: center;
  background: linear-gradient(135deg, var(--card), var(--card2));
  border: 1px solid var(--border);
  border-radius: 14px; padding: 10px 18px; margin-bottom: 10px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.4);
  animation: floatIn 0.4s ease;
}
.hud-item { text-align: center; flex: 1; }
.hud-sep  { width: 1px; background: var(--border); align-self:stretch; margin: 0 6px; }
.hud-label { font-size: 9px; letter-spacing: 3px; color: var(--muted); text-transform:uppercase; font-family:'Share Tech Mono',monospace; }
.hud-value { font-size: 22px; font-weight: 700; font-family: 'Cinzel', serif; }
.hud-score { color: var(--gold); text-shadow: 0 0 15px rgba(245,197,24,0.4); }
.hud-lives { color: var(--red); }
.hud-round { color: var(--blue); }
.hud-ai    { color: var(--purple); }

.prog-wrap { background: var(--card); border-radius: 8px; height: 6px; margin: 6px 0 12px; overflow:hidden; }
.prog-fill { height:100%; border-radius:8px; background: linear-gradient(90deg, var(--purple2), var(--gold)); transition: width 0.6s ease; }

/* ── MONSTER CARD ───────────────────────────────────────── */
.monster-card {
  background: linear-gradient(145deg, var(--card), var(--card2));
  border: 2px solid var(--border);
  border-radius: 20px; padding: 0; margin-bottom: 14px;
  position: relative; overflow: hidden;
  box-shadow: 0 8px 32px rgba(0,0,0,0.5);
  animation: floatIn 0.5s cubic-bezier(0.23,1,0.32,1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  perspective: 1200px;
  transform-style: preserve-3d;
}
.monster-card:hover {
  transform: perspective(1200px) rotateX(4deg) rotateY(-4deg) scale(1.02) translateY(-6px);
  box-shadow: 0 16px 50px rgba(0,0,0,0.6), 0 0 30px rgba(168,85,247,0.3), inset 0 0 15px rgba(255, 255, 255, 0.05);
}
.monster-card.boss-card {
  border-color: var(--orange);
  animation: floatIn 0.5s ease, bossPulse 2s ease-in-out infinite;
}
.monster-card.hired-anim { animation: hireGlow 1s ease-in-out; border-color: var(--green); }
.monster-card.reject-anim { animation: rejectShake 0.5s ease; }

.card-header {
  background: linear-gradient(135deg, #1a1a35, #0e0e25);
  border-bottom: 1px solid var(--border);
  padding: 18px 22px 14px;
  position: relative;
}
.card-banner {
  position: absolute; top: 0; left: 0; right: 0; height: 4px;
  background: linear-gradient(90deg, var(--purple2), var(--gold), var(--blue));
  background-size: 200% 100%;
  animation: goldShimmer 3s linear infinite;
}
.boss-card .card-banner {
  background: linear-gradient(90deg, var(--orange), var(--gold), var(--red));
  background-size: 200% 100%;
}
.card-type {
  font-family: 'Share Tech Mono', monospace;
  font-size: 9px; letter-spacing: 4px; color: var(--purple);
  text-transform: uppercase; margin-bottom: 6px;
}
.boss-card .card-type { color: var(--orange); }
.candidate-name {
  font-family: 'Cinzel', serif;
  font-size: 26px; font-weight: 900; color: var(--text);
  letter-spacing: 1px; line-height: 1.1;
}
.boss-card .candidate-name { color: var(--orange); text-shadow: 0 0 20px rgba(249,115,22,0.4); }
.candidate-sub {
  font-size: 11px; color: var(--muted); letter-spacing: 3px;
  text-transform: uppercase; margin-top: 4px;
  font-family: 'Share Tech Mono', monospace;
}

/* Stats grid */
.card-stats {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 10px; padding: 16px 20px 6px;
}
.stat-box {
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border);
  border-radius: 12px; padding: 12px 14px;
  transition: all 0.2s ease;
}
.stat-box:hover {
  border-color: var(--purple2);
  background: rgba(168,85,247,0.05);
}
.stat-icon { font-size: 18px; margin-bottom: 4px; }
.stat-label { font-size: 8px; letter-spacing: 3px; color: var(--muted); text-transform: uppercase; font-family:'Share Tech Mono',monospace; }
.stat-value { font-size: 15px; font-weight: 700; color: var(--text); margin-top: 2px; }
.stat-bar-wrap { background: rgba(255,255,255,0.05); border-radius:4px; height:4px; margin-top:6px; overflow:hidden; }
.stat-bar-fill { height:100%; border-radius:4px; transition: width 0.8s ease; }

/* Skills row */
.card-skills { padding: 4px 20px 16px; }
.skills-label { font-size: 9px; letter-spacing: 3px; color: var(--muted); text-transform:uppercase; margin-bottom:8px; font-family:'Share Tech Mono',monospace; }
.skill-tag {
  display: inline-block;
  background: rgba(168,85,247,0.12); color: var(--blue);
  border: 1px solid rgba(168,85,247,0.25);
  border-radius: 6px; font-size: 10px; padding: 3px 9px; margin: 2px 3px 2px 0;
  font-family: 'Share Tech Mono', monospace;
  transition: all 0.2s ease;
}
.skill-tag:hover { background: rgba(168,85,247,0.25); border-color: var(--purple); }
.boss-card .skill-tag { color: var(--orange); border-color: rgba(249,115,22,0.3); background: rgba(249,115,22,0.08); }

/* ── BOSS BANNER ─────────────────────────────────────────── */
.boss-banner {
  background: linear-gradient(135deg, #1a0800, #200e00);
  border: 2px solid var(--orange);
  border-radius: 12px; padding: 14px 22px;
  text-align: center; margin-bottom: 12px;
  animation: bossPulse 1.5s ease-in-out infinite;
  font-family: 'Cinzel', serif;
}
.boss-banner-title { font-size: 22px; font-weight: 900; color: var(--orange); letter-spacing: 3px; }
.boss-banner-sub   { font-size: 11px; color: rgba(249,115,22,0.6); letter-spacing: 2px; margin-top: 4px; }

/* ── AI MENTOR PANEL ─────────────────────────────────────── */
.ai-panel {
  background: linear-gradient(135deg, #0e0920, #140d28);
  border: 1px solid rgba(168,85,247,0.4);
  border-left: 4px solid var(--purple);
  border-radius: 14px; padding: 18px 20px; margin-bottom: 14px;
  animation: fadeSlideIn 0.5s ease, aiPulse 2s ease-in-out 0.5s;
  box-shadow: var(--ai-glow);
}
.ai-panel.warn {
  background: linear-gradient(135deg, #150810, #1c0a14);
  border-color: rgba(239,68,68,0.4);
  border-left-color: var(--red);
  box-shadow: 0 0 20px rgba(239,68,68,0.2);
}
.ai-mentor-header {
  display:flex; align-items:center; gap: 10px; margin-bottom: 12px;
}
.ai-avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: linear-gradient(135deg, var(--purple2), var(--blue2));
  display: flex; align-items:center; justify-content:center;
  font-size: 18px; box-shadow: 0 0 15px rgba(168,85,247,0.4);
  animation: spin 8s linear infinite;
}
.ai-mentor-name { font-family:'Cinzel',serif; font-size: 13px; font-weight:700; color: var(--purple); }
.ai-mentor-sub  { font-size: 9px; letter-spacing: 2px; color: var(--muted); text-transform:uppercase; font-family:'Share Tech Mono',monospace; }
.ai-rec {
  font-family: 'Cinzel', serif; font-size: 16px; font-weight: 700;
  color: var(--gold); margin-bottom: 8px;
}
.ai-line { font-size: 13px; color: #c0b8e0; line-height: 1.8; padding: 2px 0; }
.ai-confidence {
  margin-top: 10px; font-size: 10px; letter-spacing: 2px;
  color: var(--muted); font-family:'Share Tech Mono',monospace;
}
.prob-bar-bg { background: rgba(255,255,255,0.06); border-radius:6px; height:8px; margin:10px 0 4px; overflow:hidden; }
.prob-bar-fill { height:100%; border-radius:6px; transition: width 1s ease; }
.prob-label { font-size: 11px; font-family:'Share Tech Mono',monospace; color: var(--muted); }

/* AI locked placeholder */
.ai-locked {
  background: rgba(168,85,247,0.05);
  border: 1px dashed rgba(168,85,247,0.2);
  border-radius: 12px; padding: 16px; text-align:center;
  color: var(--muted); font-size: 12px; letter-spacing: 1px;
  font-family: 'Share Tech Mono', monospace; margin-bottom: 14px;
}

/* ── RESULT BOX ──────────────────────────────────────────── */
.result-box {
  border-radius: 14px; padding: 16px 20px; margin: 12px 0;
  font-family: 'Cinzel', serif; font-size: 15px; font-weight: 700;
  text-align: center; line-height: 1.7;
  animation: floatIn 0.4s ease;
}
.result-win   { background:rgba(34,197,94,0.1);  border:2px solid var(--green);  color:var(--green);  box-shadow:var(--hire-glow); }
.result-lose  { background:rgba(239,68,68,0.1);  border:2px solid var(--red);    color:var(--red);    box-shadow:var(--reject-glow); }
.result-skip  { background:rgba(245,197,24,0.08);border:2px solid var(--gold);   color:var(--gold); }
.result-boss  { background:rgba(249,115,22,0.1); border:2px solid var(--orange); color:var(--orange); box-shadow:var(--boss-glow); }

.actual-outcome { text-align:center; font-size:12px; color:var(--muted); margin-top:6px; font-family:'Share Tech Mono',monospace; }

/* ── POWER-UPS ───────────────────────────────────────────── */
.powerup-row {
  display: flex; gap: 10px; margin-bottom: 14px;
}
.pu-chip {
  flex: 1; background: rgba(255,255,255,0.03);
  border: 1px solid var(--border); border-radius: 12px;
  padding: 10px 8px; text-align: center;
  transition: all 0.2s ease; cursor: pointer;
}
.pu-chip.active { border-color: var(--gold); background: rgba(245,197,24,0.06); }
.pu-chip.used   { opacity: 0.3; }
.pu-icon-big    { font-size: 20px; display:block; margin-bottom:4px; }
.pu-name        { font-size: 10px; font-weight: 700; color: var(--text); }
.pu-status      { font-size: 8px;  color: var(--muted); letter-spacing:1px; font-family:'Share Tech Mono',monospace; }

/* ── STREAK DISPLAY ─────────────────────────────────────── */
.streak-badge {
  display: inline-flex; align-items:center; gap:6px;
  background: rgba(249,115,22,0.15); border: 1px solid rgba(249,115,22,0.3);
  border-radius: 20px; padding: 4px 12px; font-size:13px; font-weight:700;
  color: var(--orange); animation: streakPop 0.3s ease;
  font-family: 'Cinzel', serif;
}

/* ── BACKSTORY EXPANDER ──────────────────────────────────── */
[data-testid="stExpander"] {
  background: rgba(255,255,255,0.02) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important; margin-bottom: 10px !important;
}
[data-testid="stExpander"] summary {
  font-family: 'Rajdhani', sans-serif !important;
  font-size: 13px !important; color: var(--muted) !important;
}

/* ── SPLASH / GAME OVER ──────────────────────────────────── */
.splash-title {
  font-family: 'Cinzel', serif; font-size: 52px; font-weight: 900;
  text-align: center; letter-spacing: 2px;
  background: linear-gradient(135deg, var(--gold), var(--purple), var(--blue));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  animation: titleGlow 3s ease-in-out infinite;
  line-height: 1.1; margin-bottom: 8px;
}
.splash-sub {
  text-align: center; font-size: 11px; letter-spacing: 5px;
  color: var(--muted); text-transform: uppercase;
  font-family: 'Share Tech Mono', monospace; margin-bottom: 28px;
}
.info-box {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 16px; padding: 22px 26px; margin-bottom: 18px;
  font-size: 13px; line-height: 2; color: #b0a8cc;
}
.info-box b { color: var(--gold); font-family:'Cinzel',serif; }

.gameover-screen { text-align:center; padding: 30px 0; }
.gameover-emoji  { font-size: 64px; }
.gameover-title  { font-family:'Cinzel',serif; font-size:42px; font-weight:900; margin:8px 0; }
.gameover-score  {
  font-family:'Cinzel',serif; font-size: 82px; font-weight:900;
  color: var(--gold); text-shadow: 0 0 40px rgba(245,197,24,0.5);
  animation: goldShimmer 3s linear infinite;
  background: linear-gradient(90deg, var(--gold), #fff, var(--gold));
  background-size: 200%; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.gameover-label { font-size:11px; letter-spacing:4px; color:var(--muted); font-family:'Share Tech Mono',monospace; }

/* ── LEADERBOARD ─────────────────────────────────────────── */
.lb-row {
  display:flex; align-items:center; justify-content:space-between;
  background: rgba(255,255,255,0.03); border: 1px solid var(--border);
  border-radius: 10px; padding: 10px 16px; margin-bottom: 6px;
  font-family: 'Rajdhani', sans-serif;
  transition: all 0.2s ease;
}
.lb-row:hover { border-color: var(--purple2); }
.lb-rank  { font-family:'Cinzel',serif; font-size:18px; font-weight:900; color:var(--muted); min-width:36px; }
.lb-rank.gold   { color: var(--gold); text-shadow: 0 0 15px rgba(245,197,24,0.5); }
.lb-rank.silver { color: #d1d5db; }
.lb-rank.bronze { color: var(--orange); }
.lb-name  { flex:1; font-size:15px; font-weight:700; color:var(--text); padding-left:10px; }
.lb-score { font-family:'Cinzel',serif; font-size:18px; font-weight:900; color:var(--gold); }

/* ── STAT ROWS (game over breakdown) ────────────────────── */
.stat-row-go {
  display:flex; justify-content:space-between; padding:7px 0;
  border-bottom: 1px solid var(--border); font-size:14px;
}
.stat-row-go:last-child { border-bottom:none; }
.srow-key   { color: var(--muted); font-family:'Share Tech Mono',monospace; font-size:12px; }
.srow-good  { color: var(--green); font-weight:700; font-family:'Cinzel',serif; }
.srow-bad   { color: var(--red);   font-weight:700; font-family:'Cinzel',serif; }
.srow-neu   { color: var(--text);  font-weight:700; font-family:'Cinzel',serif; }

/* ── BUTTONS ─────────────────────────────────────────────── */
.stButton > button {
  width: 100% !important;
  background: linear-gradient(135deg, #0e0e1f, #14142a) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  border-radius: 12px !important;
  font-family: 'Rajdhani', sans-serif !important;
  font-size: 15px !important; font-weight: 700 !important;
  padding: 12px !important; letter-spacing: 1px !important;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
  position: relative !important;
  overflow: hidden !important;
  z-index: 1 !important;
}
.stButton > button::before {
  content: "";
  position: absolute !important;
  top: 0 !important;
  left: -100% !important;
  width: 100% !important;
  height: 100% !important;
  background: linear-gradient(120deg, transparent, rgba(255,255,255,0.15), transparent) !important;
  transition: all 0.5s ease !important;
  z-index: -1 !important;
}
.stButton > button:hover::before {
  left: 100% !important;
}
.stButton > button:hover {
  border-color: var(--gold) !important;
  color: var(--gold) !important;
  box-shadow: 0 0 25px rgba(245,197,24,0.3), inset 0 0 10px rgba(245,197,24,0.1) !important;
  transform: translateY(-3px) scale(1.02) !important;
}
[data-testid="stTextInput"] input {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-family: 'Rajdhani', sans-serif !important;
  font-size: 15px !important;
}
[data-testid="stSelectbox"] > div {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
}
.divider { border:none; border-top: 1px solid var(--border); margin: 14px 0; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════
def hp_color(pct: float) -> str:
    if pct >= 0.7: return "#22c55e"
    if pct >= 0.4: return "#f5c518"
    return "#ef4444"


def edu_armor(level: int) -> int:
    return {1: 10, 2: 20, 3: 40, 4: 70, 5: 90}.get(level, 30)


def render_hud():
    lives_icons = "❤️" * st.session_state.lives + "🖤" * (3 - st.session_state.lives)
    ai_left = st.session_state.ai_uses
    ai_str  = "🤖" * ai_left + "⬜" * (3 - ai_left)
    total   = len(st.session_state.resumes)
    curr    = st.session_state.round_idx + 1
    pct     = int(st.session_state.round_idx / total * 100) if total else 0

    # Streak badge
    streak = st.session_state.get("streak", 0)
    streak_html = (
        f'<div class="streak-badge" style="float:right">🔥 Streak {streak}</div>'
        if streak >= 3 else ""
    )
    
    # Bias Report Feature
    bias_res = analyze_bias(st.session_state.history, st.session_state.resumes)
    bias_color = "var(--red)" if bias_res["score"] > 30 else ("var(--orange)" if bias_res["score"] > 15 else "var(--green)")

    st.markdown(f"""
    {streak_html}
    <div style="font-size: 11px; text-align: right; margin-bottom: 5px; color: {bias_color}; font-family: 'Share Tech Mono', monospace;">
      BIAS RADAR: {bias_res['status']}
    </div>
    <div class="hud-bar">
      <div class="hud-item">
        <div class="hud-label">Score</div>
        <div class="hud-value hud-score">{st.session_state.score}</div>
      </div>
      <div class="hud-sep"></div>
      <div class="hud-item">
        <div class="hud-label">Lives</div>
        <div class="hud-value hud-lives" style="font-size:18px">{lives_icons}</div>
      </div>
      <div class="hud-sep"></div>
      <div class="hud-item">
        <div class="hud-label">Round</div>
        <div class="hud-value hud-round">{curr} / {total}</div>
      </div>
      <div class="hud-sep"></div>
      <div class="hud-item">
        <div class="hud-label">AI Hints</div>
        <div class="hud-value hud-ai" style="font-size:18px">{ai_str}</div>
      </div>
    </div>
    <div class="prog-wrap"><div class="prog-fill" style="width:{pct}%"></div></div>
    """, unsafe_allow_html=True)


def render_monster_card(row: dict, idx: int):
    is_boss = row.get("is_boss", False)
    name    = pick_name(idx)
    skills  = pick_skills(int(row["skills_count"]), idx)
    edu_lv  = int(row["education"])
    edu_str = EDUCATION_MAP.get(edu_lv, "Bachelor's Degree")
    exp     = row["experience"]
    gap     = row["gap_years"]
    gap_r   = row.get("gap_reason", "No Gap")
    gap_str = f"{gap:.1f} yrs — {gap_r}" if gap >= 0.1 else "None"

    # Card stat percentages (for bar fills)
    hp_pct      = min(exp / 20, 1.0)
    atk_pct     = min(int(row["skills_count"]) / 10, 1.0)
    armor_pct   = edu_armor(edu_lv) / 100
    risk_pct    = min(gap / 5, 1.0)

    hp_col      = hp_color(hp_pct)
    atk_col     = "#38bdf8"
    armor_col   = "#a855f7"
    risk_col    = "#f97316" if risk_pct > 0.4 else "#22c55e"

    tags = "".join(f'<span class="skill-tag">{s}</span>' for s in skills)
    card_cls = "monster-card boss-card" if is_boss else "monster-card"
    card_type = "👹 BOSS CANDIDATE" if is_boss else "⚔️ CANDIDATE CARD"

    st.markdown(f"""
    <div class="{card_cls}">
      <div class="card-header">
        <div class="card-banner"></div>
        <div class="card-type">{card_type} · #{idx+1}</div>
        <div class="candidate-name">{name}</div>
        <div class="candidate-sub">Resume Review · Round {idx+1}</div>
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
            <div class="stat-bar-fill" style="width:{int(armor_pct*100)}%;background:{armor_col}"></div>
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
    if bs:
        with st.expander("📖 Candidate Backstory"):
            st.markdown(
                f'<div style="font-size:13px;color:#b0b0c8;line-height:1.9;'
                f'font-family:Rajdhani,sans-serif">{bs}</div>',
                unsafe_allow_html=True,
            )


def render_ai_panel(whisper: dict, llm_text: str | None = None):
    prob  = whisper.get("prob", 0.5)
    pred  = whisper.get("pred", 0)
    lines = whisper.get("lines", [])
    rec   = whisper.get("recommendation", "⛔ REJECT")
    conf  = whisper.get("confidence", "")

    pct = int(prob * 100)
    col = "#22c55e" if prob >= 0.55 else "#ef4444" if prob < 0.45 else "#a855f7"
    panel_cls = "ai-panel" if pred == 1 else "ai-panel warn"

    body_html = ""
    if llm_text:
        body_html = f'<div class="ai-line" style="color:#e0d8f0;font-style:italic">"{llm_text}"</div><br>'
    for ln in lines:
        body_html += f'<div class="ai-line">{ln}</div>'

    st.markdown(f"""
    <div class="{panel_cls}">
      <div class="ai-mentor-header">
        <div class="ai-avatar">🤖</div>
        <div>
          <div class="ai-mentor-name">AI Mentor</div>
          <div class="ai-mentor-sub">SHAP · XGBoost · {('Ollama Active' if llm_text else 'SHAP Mode')}</div>
        </div>
      </div>
      <div class="ai-rec">{rec}</div>
      {body_html}
      <div class="prob-bar-bg">
        <div class="prob-bar-fill" style="width:{pct}%;background:{col}"></div>
      </div>
      <div class="prob-label">HIRE PROBABILITY: <strong style="color:{col}">{pct}%</strong></div>
      <div class="ai-confidence">· {conf} ·</div>
    </div>
    """, unsafe_allow_html=True)


def render_powerup_panel() -> str | None:
    pu = st.session_state.powerups
    activated = None
    PU = {
        "bias_shield": ("🛡️", "Bias Shield",  "Block bias penalty"),
        "lucky_charm": ("🍀", "Lucky Charm",   "+10 if follow AI" ),
        "second_look": ("🔍", "Second Look",   "Free AI reveal"   ),
    }
    cols = st.columns(3)
    for col, (key, (icon, name, desc)) in zip(cols, PU.items()):
        count = pu.get(key, 0)
        cls   = "used" if count == 0 else "active" if st.session_state.get(f"{key}_active") else ""
        with col:
            st.markdown(f"""
            <div class="pu-chip {cls}">
              <span class="pu-icon-big">{icon}</span>
              <div class="pu-name">{name}</div>
              <div class="pu-status">{'AVAILABLE' if count > 0 else 'USED'}</div>
            </div>""", unsafe_allow_html=True)
            if count > 0:
                if st.button(f"{icon} Use", key=f"pu_{key}", use_container_width=True):
                    activated = key
    return activated


def render_result(res: dict, row: dict):
    is_boss = res.get("is_boss") and res.get("correct")
    if is_boss:
        cls = "result-box result-boss"
    elif res["delta"] > 0:
        cls = "result-box result-win"
    elif res["action"] == "skip":
        cls = "result-box result-skip"
    else:
        cls = "result-box result-lose"

    msg_h = res["msg"].replace("\n", "<br>")
    actual = "✅ Good Hire" if res["outcome"] == 1 else "❌ Bad Hire"

    st.markdown(f"""
    <div class="{cls}">{msg_h}</div>
    <div class="actual-outcome">Actual outcome: <strong style="color:#e8e8f0">{actual}</strong></div>
    """, unsafe_allow_html=True)

    # Lazy-load Ollama feedback AFTER result is on screen.
    # Only fetches once (guarded by _llm_loaded flag).
    if not res.get("_llm_loaded") and ollama_available() and res["action"] != "skip":
        fb = ollama_feedback(row, res["action"])
        res["llm_feedback"] = fb
        res["_llm_loaded"]  = True
        st.session_state.last_result = res  # persist back

    llm_feedback = res.get("llm_feedback") or ""
    if llm_feedback:
        st.markdown(
            f'<div style="margin-top:8px;font-size:13px;color:#b0a8cc;'
            f'font-style:italic;font-family:Rajdhani,sans-serif">🤖 {llm_feedback}</div>',
            unsafe_allow_html=True,
        )


def render_leaderboard():
    rows = load_leaderboard()
    rank_cls = {1: "gold", 2: "silver", 3: "bronze"}
    medals   = {1: "🥇", 2: "🥈", 3: "🥉"}
    st.markdown("### 🏆 Hall of Fame")
    if not rows:
        st.markdown('<div style="color:var(--muted);font-size:13px;text-align:center;padding:20px">No entries yet — be the first!</div>', unsafe_allow_html=True)
        return
    for i, r in enumerate(rows, 1):
        rc  = rank_cls.get(i, "")
        med = medals.get(i, f"#{i}")
        st.markdown(f"""
        <div class="lb-row">
          <div class="lb-rank {rc}">{med}</div>
          <div class="lb-name">{r['name']}</div>
          <div class="lb-score">{r['score']}</div>
        </div>""", unsafe_allow_html=True)


def render_game_over():
    s     = st.session_state
    score = s.score
    hist  = s.history
    n_correct = sum(1 for h in hist if h.get("correct"))
    ai_used   = 3 - s.ai_uses
    ai_follow = sum(1 for h in hist if h.get("followed_ai"))

    if   score >= 250: title, emoji = "LEGENDARY HR!",  "🏆"
    elif score >= 150: title, emoji = "GREAT HIRING!",  "🎯"
    elif score >= 60:  title, emoji = "DECENT RUN",     "👔"
    else:              title, emoji = "NEEDS WORK",     "💀"

    st.markdown(f"""
    <div class="gameover-screen">
      <div class="gameover-emoji">{emoji}</div>
      <div class="gameover-title" style="color:{'#f5c518' if score>=150 else '#ef4444'}">🎯 LEVEL COMPLETE REPORT</div>
      <div class="gameover-score">{score}</div>
      <div class="gameover-label" style="font-size:14px; color:var(--gold);">FINAL SCORE: {title}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── LEARNING & SELF-IMPROVEMENT ──
    gaps = evaluate_skill_gaps(hist, s.resumes)
    bias_res = analyze_bias(hist, s.resumes)

    # Lazy-load AI Coach
    if ollama_available() and "career_coach_fb" not in s:
        s.career_coach_fb = ollama_career_coach(
            strengths=gaps["strengths"],
            weaknesses=gaps["weaknesses"],
            bias_status=bias_res["status"],
            score=score
        )
        
    ai_coach_html = ""
    if s.get("career_coach_fb"):
        ai_coach_html = f"""
        <div style="background:rgba(168,85,247,0.1); border:1px solid var(--purple); border-radius:12px; padding:15px; margin-top:15px;">
            <div style="color:var(--purple); font-weight:bold; font-family:'Cinzel',serif; margin-bottom:5px;">🤖 AI CAREER COACH</div>
            <div style="font-size:13px; font-style:italic; line-height:1.6; color:#e0d8f0;">"{s.career_coach_fb}"</div>
        </div>
        """

    missions_html = "".join([f'<div style="color:var(--blue); font-size:14px; margin-bottom:4px;">{m}</div>' for m in gaps['missions']])

    st.markdown(f"""
    <div style="display:flex; gap:15px; margin-bottom:15px;">
        <div style="flex:1; background:var(--card); border:1px solid var(--green); padding:15px; border-radius:12px;">
            <div style="color:var(--green); font-family:'Cinzel',serif; font-weight:bold;">💪 STRENGTHS</div>
            <div style="font-size:13px; color:var(--text); margin-top:5px;">{gaps['strengths']}</div>
        </div>
        <div style="flex:1; background:var(--card); border:1px solid var(--red); padding:15px; border-radius:12px;">
            <div style="color:var(--red); font-family:'Cinzel',serif; font-weight:bold;">⚠️ WEAKNESSES</div>
            <div style="font-size:13px; color:var(--text); margin-top:5px;">{gaps['weaknesses']}</div>
        </div>
    </div>
    
    <div style="background:var(--card); border:1px dashed var(--blue); padding:15px; border-radius:12px; margin-bottom:15px;">
        <div style="color:var(--blue); font-family:'Cinzel',serif; font-weight:bold; margin-bottom:8px;">🎯 NEXT ROUND MISSIONS</div>
        {missions_html}
    </div>
    
    {ai_coach_html}
    <hr class="divider">
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-family:Cinzel,serif;font-size:16px;margin-bottom:10px;color:#f5c518">📊 Session Breakdown</div>', unsafe_allow_html=True)

    breakdown = [
        ("Bias Radar",        bias_res["status"],        "neu"),
        ("Correct Decisions", n_correct,                 "good"),
        ("Wrong Decisions",   len(hist) - n_correct,     "bad"),
        ("AI Hints Used",     ai_used,                   "neu"),
        ("Times Followed AI", ai_follow,                 "good"),
        ("Best Streak",       s.get("best_streak", 0),   "neu"),
    ]
    for label, val, cls in breakdown:
        st.markdown(f'<div class="stat-row-go"><span class="srow-key">{label}</span><span class="srow-{cls}">{val}</span></div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Save score
    save_leaderboard(s.player_name, score, n_correct, len(hist))
    render_leaderboard()
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    _, c, _ = st.columns([1, 2, 1])
    with c:
        # Adaptive gameplay logic
        next_diff = "hard" if score > 100 else ("normal" if score > 30 else "easy")
        if st.button(f"🔄  Start Next Round ({next_diff.upper()})", use_container_width=True):
            p_name = s.player_name
            # Clear state but keep some keys
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            # Restart with adaptive difficulty
            start_game(p_name, next_diff)
            st.rerun()


def render_splash(acc: float):
    st.markdown("""
    <div style="text-align:center;padding:30px 0 4px">
      <div style="font-size:56px;margin-bottom:8px">⚔️</div>
      <div class="splash-title">BiasBreaker</div>
      <div class="splash-sub">The Hiring Game · AI-Powered · v3.0</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="info-box">
      <b>⚔️ HOW TO PLAY</b><br><br>
      Review 10 <b>Monster Resumes</b> — each is a fantasy candidate card with RPG stats.<br><br>
      🛡️ <b>Hire</b> · ⚔️ <b>Reject</b> · ⏭ <b>Skip</b> . Make the right call to earn points.<br><br>
      🤖 <b>AI Hints (3 per game):</b> Costs –3 pts, reveals XGBoost + SHAP analysis.
         Follow AI → earn <b>+20 bonus</b>!<br><br>
      ⚡ <b>Power-Ups:</b> 🛡️ Bias Shield · 🍀 Lucky Charm · 🔍 Second Look<br>
      👹 <b>Round 10 = Boss Round:</b> double points on correct decision!<br>
      🔥 <b>Streak System:</b> 3+ correct in a row = bonus points each round!<br><br>
      <b>Scoring:</b> Correct ±10 · Wrong Hire –5 · Wrong Reject –15<br>
      Follow AI +20 · Bias Penalty –10 · Skip –3<br><br>
      <span style="font-size:11px;color:#555">XGBoost accuracy: {int(acc*100)}%
      {'· Ollama LLM: Active ✅' if ollama_available() else '· Ollama: Offline (SHAP-only mode)'}</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("🧑 Your Name", placeholder="Enter your name…", value="Challenger")
    with col2:
        difficulty = st.selectbox("⚡ Difficulty", ["normal", "easy", "hard"])

    _, c, _ = st.columns([1, 2, 1])
    with c:
        if st.button("▶  START GAME", use_container_width=True):
            start_game(name or "Challenger", difficulty)
            st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    render_leaderboard()


# ══════════════════════════════════════════════════════════
#  MAIN GAME LOOP
# ══════════════════════════════════════════════════════════
def run_game(model, explainer):
    resumes   = st.session_state.resumes
    round_idx = st.session_state.round_idx

    if round_idx >= len(resumes):
        st.session_state.game_over = True
        st.rerun()

    row     = resumes[round_idx]
    is_boss = row.get("is_boss", False)

    if is_boss:
        st.markdown("""
        <div class="boss-banner">
          <div class="boss-banner-title">👹 FINAL BOSS ROUND 👹</div>
          <div class="boss-banner-sub">CORRECT DECISION = DOUBLE POINTS</div>
        </div>
        """, unsafe_allow_html=True)

    render_hud()
    render_monster_card(row, round_idx)

    # Pre-compute prediction once per round
    if st.session_state.get("_pred_round") != round_idx:
        prob, ai_pred, shap_vals = predict(model, explainer, row)
        whisper = build_whisper(prob, ai_pred, shap_vals, row)
        st.session_state.update({
            "_prob": prob, "_ai_pred": ai_pred, "_whisper": whisper,
            "_pred_round": round_idx,
            "hint_shown": False,
            "_hint_used_this_round": False,
            "bias_shield_active": False,
            "lucky_charm_active": False,
        })
    else:
        prob    = st.session_state["_prob"]
        ai_pred = st.session_state["_ai_pred"]
        whisper = st.session_state["_whisper"]

    # ── Show result and Next button ──────────────────────
    if st.session_state.awaiting_next and st.session_state.last_result:
        render_result(st.session_state.last_result, row)
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        if st.button("→  Next Candidate", use_container_width=True):
            st.session_state.awaiting_next = False
            st.session_state.last_result   = None
            st.session_state.round_idx    += 1
            if st.session_state.round_idx >= len(resumes):
                st.session_state.game_over = True
            st.rerun()
        return

    # ── AI Hint section ──────────────────────────────────
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    if st.session_state.hint_shown:
        llm_txt = st.session_state.get("_llm_whisper")
        render_ai_panel(whisper, llm_txt)
    else:
        ai_left = st.session_state.ai_uses
        if ai_left > 0:
            if st.button(
                f"🤖  Use AI Hint  ({ai_left} remaining · costs –3 pts)",
                use_container_width=True,
            ):
                st.session_state.ai_uses -= 1
                st.session_state.score   += -3
                st.session_state.hint_shown = True
                st.session_state["_hint_used_this_round"] = True
                # Try Ollama
                if ollama_available():
                    llm_txt = get_ai_whisper_llm(row, whisper.get("lines", []))
                    st.session_state["_llm_whisper"] = llm_txt
                else:
                    st.session_state["_llm_whisper"] = None
                st.rerun()
        else:
            st.markdown(
                '<div class="ai-locked">🔒 No AI Hints remaining — trust your instincts!</div>',
                unsafe_allow_html=True,
            )

    # ── Power-Ups ────────────────────────────────────────
    activated = render_powerup_panel()
    if activated == "second_look":
        st.session_state.powerups["second_look"]     = 0
        st.session_state.hint_shown                  = True
        st.session_state["_hint_used_this_round"]    = True
        st.session_state["_llm_whisper"]             = None
        st.rerun()
    if activated == "bias_shield":
        st.session_state.powerups["bias_shield"] = 0
        st.session_state.bias_shield_active      = True
        st.toast("🛡️ Bias Shield active!", icon="🛡️")
        st.rerun()
    if activated == "lucky_charm":
        st.session_state.powerups["lucky_charm"] = 0
        st.session_state.lucky_charm_active      = True
        st.toast("🍀 Lucky Charm active — follow AI for +10!", icon="🍀")
        st.rerun()

    # ── Action buttons ───────────────────────────────────
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    action = None
    with c1:
        if st.button("🛡️  HIRE",   use_container_width=True): action = "hire"
    with c2:
        if st.button("⚔️  REJECT", use_container_width=True): action = "reject"
    with c3:
        if st.button("⏭  SKIP",   use_container_width=True): action = "skip"

    if action:
        outcome = int(row["outcome"])
        delta, msg, correct = compute_score(
            action, outcome, ai_pred, row,
            shield=st.session_state.bias_shield_active,
            charm=st.session_state.lucky_charm_active,
            is_boss=is_boss,
        )
        if is_boss and correct:
            st.session_state["boss_correct"] = True
            msg = "👹 BOSS DEFEATED — Double Points! 🏆\n" + msg

        st.session_state.score += delta
        if action != "skip" and not correct:
            st.session_state.lives -= 1
        if action == "skip":
            st.session_state.skips_used += 1

        followed_ai = (action == "hire") == (ai_pred == 1) if action != "skip" else False

        # Update decision log for active learning
        st.session_state.decision_log.append({
            **row, "outcome": outcome
        })
        
        # Trigger Active Learning Retrain (lazy loading on next round)
        st.session_state["_needs_retrain"] = True

        st.session_state.history.append({
            "round": round_idx, "action": action,
            "outcome": outcome, "correct": correct,
            "followed_ai": followed_ai, "delta": delta,
        })
        st.session_state.last_result = {
            "action": action, "delta": delta, "msg": msg,
            "outcome": outcome, "correct": correct,
            "is_boss": is_boss,
            "llm_feedback": None,   # filled lazily on result screen
            "_llm_loaded": False,
        }
        st.session_state.awaiting_next = True
        if st.session_state.lives <= 0:
            st.session_state.game_over = True
        st.rerun()


# ══════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════
def main():
    # --- CURSOR TRAIL & 3D JS INJECTION ---
    components.html("""
    <script>
        const targetDoc = window.parent.document;
        if (!targetDoc.getElementById("cursor-trail-script")) {
            const script = targetDoc.createElement("script");
            script.id = "cursor-trail-script";
            script.innerHTML = `
                const trailContainer = document.createElement("div");
                trailContainer.style.position = "fixed";
                trailContainer.style.pointerEvents = "none";
                trailContainer.style.zIndex = "999999";
                trailContainer.style.top = "0";
                trailContainer.style.left = "0";
                trailContainer.style.width = "100%";
                trailContainer.style.height = "100%";
                document.body.appendChild(trailContainer);

                const dots = [];
                for (let i = 0; i < 20; i++) {
                    let dot = document.createElement("div");
                    dot.style.position = "absolute";
                    let size = (20 - i);
                    dot.style.width = size + "px";
                    dot.style.height = size + "px";
                    dot.style.background = i < 5 ? "radial-gradient(circle, rgba(245,197,24,0.9) 0%, rgba(245,197,24,0) 70%)" : "radial-gradient(circle, rgba(168,85,247,0.7) 0%, rgba(56,189,248,0) 80%)";
                    dot.style.borderRadius = "50%";
                    dot.style.transform = "translate(-50%, -50%)";
                    dot.style.mixBlendMode = "screen";
                    
                    // Box shadow for extra glow
                    if (i === 0) dot.style.boxShadow = "0 0 10px rgba(245,197,24,1), 0 0 20px rgba(168,85,247,1)";
                    
                    trailContainer.appendChild(dot);
                    dots.push({ x: window.innerWidth/2, y: window.innerHeight/2, el: dot });
                }

                let msX = window.innerWidth / 2;
                let msY = window.innerHeight / 2;

                document.addEventListener("mousemove", (e) => {
                    msX = e.clientX;
                    msY = e.clientY;
                });

                function animate() {
                    let x = msX;
                    let y = msY;
                    dots.forEach((dot, index) => {
                        let nextDot = dots[index + 1] || dots[0];
                        dot.x = x;
                        dot.y = y;
                        dot.el.style.left = dot.x + "px";
                        dot.el.style.top = dot.y + "px";
                        x += (nextDot.x - dot.x) * (0.45);
                        y += (nextDot.y - dot.y) * (0.45);
                    });
                    requestAnimationFrame(animate);
                }
                animate();
            `;
            targetDoc.body.appendChild(script);
        }
    </script>
    """, height=0, width=0)

    init_state()
    model, explainer, acc = train_model()

    if st.session_state.game_over:
        render_game_over()
        return
    if not st.session_state.game_started:
        render_splash(acc)
        return
        
    # Active learning check before round starts
    if st.session_state.get("_needs_retrain", False) and len(st.session_state.decision_log) >= 3:
        st.toast("🧠 AI is learning from your decisions!", icon="🧠")
        # Retrain model using decisions log + small slice of base dataframe if possible, but here we just use the decisions + synthetic
        res = retrain_with_decisions(st.session_state.decision_log)
        if res:
            st.session_state["active_model"] = res[0]
            st.session_state["active_explainer"] = res[1]
        st.session_state["_needs_retrain"] = False
        
    # Use active learning model if available
    active_m = st.session_state.get("active_model", model)
    active_e = st.session_state.get("active_explainer", explainer)

    run_game(active_m, active_e)


if __name__ == "__main__":
    main()
