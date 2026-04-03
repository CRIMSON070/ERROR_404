"""
app.py  —  BiasBreaker: The Hiring Game
Run:  streamlit run app.py
"""

import streamlit as st
import streamlit.components.v1 as components
import random
import threading
import time

from data_engine import (
    pick_name, pick_skills, EDUCATION_MAP, POSITIVE_GAPS, generate_resumes, make_boss_resume
)
from ml_engine import train_model, predict, build_whisper, retrain_with_decisions
from ollama_client import get_ai_whisper_llm, ollama_available, ollama_feedback, ollama_career_coach
from game_state import (
    init_state, start_game, compute_score,
    save_leaderboard, load_leaderboard, analyze_bias, evaluate_skill_gaps
)
from logic.decision_engine import process_decision
from logic.bias_analysis import calculate_bias
from components.vs_panel import render_vs_panel
from components.powerups import render_powerup_panel as render_pu_panel

# ══════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="BiasBreaker: The Hiring Game",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="expanded",
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

/* ── NEON GLOWS & GLASSMORPHISM ── */
.glass-container {
    background: rgba(16, 16, 31, 0.4);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 20px;
}
.neon-border-blue { border: 2px solid var(--blue); box-shadow: 0 0 15px rgba(56, 189, 248, 0.5); }
.neon-border-gold { border: 2px solid var(--gold); box-shadow: 0 0 15px rgba(245, 197, 24, 0.5); }
.neon-border-purple { border: 2px solid var(--purple); box-shadow: 0 0 15px rgba(168, 85, 247, 0.5); }

.stat-v-box {
    text-align: center;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 10px;
    border: 1px solid var(--border);
}

.divider {
  border: none;
  border-top: 1px solid var(--border);
  margin: 14px 0;
}

/* ── ADDITIONAL CYBERPUNK POLISH ── */
.stApp {
    background: radial-gradient(circle at top right, #1a1a2e 0%, #16213e 50%, #0f3460 100%) !important;
}

.pu-chip.active { box-shadow: 0 0 10px var(--blue); }
.pu-chip.used   { filter: grayscale(1); opacity: 0.5; }
.pu-chip.available { border-color: var(--blue); }

/* Glassmorphism for sidebar */
[data-testid="stSidebar"] {
    background-color: rgba(16, 16, 31, 0.8) !important;
    backdrop-filter: blur(10px);
    border-right: 1px solid var(--border);
}

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
    s     = st.session_state
    total = len(s.resumes)
    curr  = s.round_idx + 1
    pct   = int(s.round_idx / total * 100) if total else 0

    # ── Rank XP thresholds ──────────────────────────────────────
    rank_thresholds = {
        "Beginner":    (0,   200),
        "Analyst":     (200, 500),
        "Expert":      (500, 1000),
        "Bias Master": (1000, 1000),
    }
    xp_min, xp_max = rank_thresholds.get(s.rank, (0, 200))
    xp_pct = int(min(100, (s.xp - xp_min) / max(1, xp_max - xp_min) * 100))
    next_rank = {"Beginner": "Analyst", "Analyst": "Expert",
                 "Expert": "Bias Master", "Bias Master": "MAX"}.get(s.rank, "MAX")
    rank_colors = {"Beginner": "#6b6b8a", "Analyst": "#38bdf8",
                   "Expert": "#a855f7", "Bias Master": "#f5c518"}
    rank_col = rank_colors.get(s.rank, "#6b6b8a")

    # ── Health colour ───────────────────────────────────────────
    hp = s.health
    hp_col  = "#22c55e" if hp > 70 else ("#f5c518" if hp > 30 else "#ef4444")
    hp_icon = "❤️" if hp > 70 else ("🟡" if hp > 30 else "💀")

    # ── Bias Radar ──────────────────────────────────────────────
    bias_res   = calculate_bias(s.history, s.resumes)
    bias_score = bias_res["bias_score"]
    bias_col   = "#ef4444" if bias_score > 30 else ("#f97316" if bias_score > 15 else "#22c55e")
    bias_label = bias_res["bias_level"].upper()

    # ── Streak fire badge ───────────────────────────────────────
    streak     = s.streak
    streak_html = ""
    if streak >= 5:
        streak_html = f'<span style="background:rgba(249,115,22,0.2);border:1px solid #f97316;border-radius:20px;padding:2px 10px;font-size:12px;color:#f97316;font-family:\'Cinzel\',serif;font-weight:700;animation:streakPop 0.4s ease;">🔥 {streak}x INFERNO</span>'
    elif streak >= 3:
        streak_html = f'<span style="background:rgba(249,115,22,0.12);border:1px solid #f97316;border-radius:20px;padding:2px 10px;font-size:12px;color:#f97316;font-family:\'Cinzel\',serif;font-weight:700;">🔥 {streak}x STREAK</span>'
    else:
        streak_html = f'<span style="color:#6b6b8a;font-family:\'Share Tech Mono\',monospace;font-size:12px;">{streak}x</span>'

    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
      <div style="font-family:'Share Tech Mono',monospace;font-size:10px;color:#6b6b8a">
        RANK: <span style="color:{rank_col};font-weight:700">{s.rank.upper()}</span>
        &nbsp;·&nbsp; XP: <span style="color:#a855f7">{s.xp}</span>
        &nbsp;→&nbsp; <span style="color:#3a3a5a;font-size:9px">{next_rank}</span>
      </div>
      <div style="font-size:10px;color:{bias_col};font-family:'Share Tech Mono',monospace">
        ⚖️ BIAS: {bias_label} ({bias_res['bias_type']})
      </div>
    </div>

    <div class="hud-bar glass-container" style="border:1px solid var(--border);padding:14px 18px;">
      <div class="hud-item">
        <div class="hud-label">{hp_icon} Health</div>
        <div class="hud-value" style="color:{hp_col};font-size:20px">{hp}%</div>
        <div style="background:rgba(255,255,255,0.06);border-radius:4px;height:4px;margin-top:4px;overflow:hidden">
          <div style="height:100%;border-radius:4px;width:{hp}%;background:{hp_col};transition:width 0.6s ease"></div>
        </div>
      </div>
      <div class="hud-sep"></div>
      <div class="hud-item">
        <div class="hud-label">⭐ Score</div>
        <div class="hud-value hud-score" style="font-size:20px">{s.score}</div>
      </div>
      <div class="hud-sep"></div>
      <div class="hud-item">
        <div class="hud-label">🎯 Round</div>
        <div class="hud-value hud-round" style="font-size:20px">{curr}/{total}</div>
      </div>
      <div class="hud-sep"></div>
      <div class="hud-item">
        <div class="hud-label">⚡ Streak</div>
        <div style="margin-top:4px">{streak_html}</div>
      </div>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;margin-top:4px">
      <div>
        <div style="display:flex;justify-content:space-between;margin-bottom:2px">
          <span style="font-size:9px;color:#6b6b8a;font-family:'Share Tech Mono',monospace">XP TO {next_rank.upper()}</span>
          <span style="font-size:9px;color:{rank_col};font-family:'Share Tech Mono',monospace">{xp_pct}%</span>
        </div>
        <div style="background:rgba(255,255,255,0.06);border-radius:4px;height:5px;overflow:hidden">
          <div style="height:100%;border-radius:4px;width:{xp_pct}%;background:linear-gradient(90deg,{rank_col},{rank_col}88);transition:width 0.8s ease"></div>
        </div>
      </div>
      <div>
        <div style="display:flex;justify-content:space-between;margin-bottom:2px">
          <span style="font-size:9px;color:#6b6b8a;font-family:'Share Tech Mono',monospace">ROUND PROGRESS</span>
          <span style="font-size:9px;color:#38bdf8;font-family:'Share Tech Mono',monospace">{pct}%</span>
        </div>
        <div class="prog-wrap" style="margin:0">
          <div class="prog-fill" style="width:{pct}%"></div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Live Bias Warning (inline alert, not sidebar) ───────────
    if bias_score > 15 and len(s.history) >= 2:
        bias_type = bias_res["bias_type"]
        if bias_score > 30:
            st.markdown(f"""
            <div style="background:rgba(239,68,68,0.1);border:1px solid #ef4444;
                        border-left:4px solid #ef4444;border-radius:10px;
                        padding:10px 14px;margin:6px 0;font-size:12px;
                        font-family:'Share Tech Mono',monospace;color:#ef4444">
              🚨 HIGH BIAS ALERT — You're showing strong <b>{bias_type}</b>.
              <span style="color:#c0a0a0"> Recalibrate your decisions!</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:rgba(249,115,22,0.08);border:1px solid #f97316;
                        border-left:4px solid #f97316;border-radius:10px;
                        padding:8px 14px;margin:6px 0;font-size:11px;
                        font-family:'Share Tech Mono',monospace;color:#f97316">
              ⚠️ Bias building: <b>{bias_type}</b> — watch your next decision.
            </div>
            """, unsafe_allow_html=True)


def render_monster_card(row: dict, idx: int):
    s_state = st.session_state
    is_boss = row.get("is_boss", False)
    
    # Blind Mode check
    blind = s_state.get("blind_mode", False)
    name = "???" if blind else pick_name(idx)
    edu_lv = int(row["education"])
    edu_str = "???" if blind else EDUCATION_MAP.get(edu_lv, "Bachelor's Degree")
    
    skills = pick_skills(int(row["skills_count"]), idx)
    exp = row["experience"]
    gap = row["gap_years"]
    gap_r = row.get("gap_reason", "No Gap")
    gap_str = f"{gap:.1f} yrs — {gap_r}" if gap >= 0.1 else "None"

    # Card stat percentages
    hp_pct = min(exp / 20, 1.0)
    atk_pct = min(int(row["skills_count"]) / 10, 1.0)
    armor_pct = edu_armor(edu_lv) / 100
    risk_pct = min(gap / 5, 1.0)

    hp_col = hp_color(hp_pct)
    atk_col = "#38bdf8"
    armor_col = "#a855f7"
    risk_col = "#f97316" if risk_pct > 0.4 else "#22c55e"

    tags = "".join(f'<span class="skill-tag">{s}</span>' for s in skills)
    card_cls = "monster-card boss-card" if is_boss else "monster-card glass-container"
    card_type = "👹 BOSS CANDIDATE" if is_boss else "⚔️ CANDIDATE CARD"

    st.markdown(f"""
    <div class="{card_cls} {'neon-border-gold' if is_boss else ''}">
      <div class="card-header">
        <div class="card-banner"></div>
        <div class="card-type">{card_type} · #{idx+1}</div>
        <div class="candidate-name">{name}</div>
        <div class="candidate-sub">{'BLIND MODE ACTIVE' if blind else 'Resume Review · Round ' + str(idx+1)}</div>
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


def render_ai_panel(whisper: dict, llm_text: str | None = None):
    prob  = whisper.get("prob", 0.5)
    lines = whisper.get("lines", [])
    conf  = whisper.get("confidence", "")

    pct = int(prob * 100)
    col = "#22c55e" if prob >= 0.55 else "#ef4444" if prob < 0.45 else "#a855f7"

    body_html = ""
    if llm_text == "ANALYZING...":
        body_html = f'<div class="ai-line" style="color:var(--purple);font-style:italic;margin-bottom:10px;animation:pulse 1.5s infinite;">⚡ AI is channeling wisdom...</div>'
    elif llm_text:
        body_html = f'<div class="ai-line" style="color:#e0d8f0;font-style:italic;margin-bottom:10px;">" {llm_text} "</div>'
    for ln in lines:
        body_html += f'<div class="ai-line">{ln}</div>'

    st.markdown(f"""
    <div class="ai-panel glass-container" style="border-left: 4px solid {col};">
      <div class="ai-mentor-header">
        <div class="ai-avatar">🤖</div>
        <div>
          <div class="ai-mentor-name">AI Whisper</div>
          <div class="ai-mentor-sub">SHAP Reasoner · {conf}</div>
        </div>
      </div>
      {body_html}
      <div class="prob-bar-bg">
        <div class="prob-bar-fill" style="width:{pct}%;background:{col}"></div>
      </div>
      <div class="prob-label">HIRE PROBABILITY: <strong style="color:{col}">{pct}%</strong></div>
    </div>
    """, unsafe_allow_html=True)


def render_powerup_bar():
    # Helper to call the modular component
    return render_pu_panel()


# ══════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════
def render_sidebar():
    """Renders the game sidebar with missions, skill analysis, and blind mode toggle."""
    s = st.session_state
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:14px 0 6px">
          <div style="font-size:32px">⚔️</div>
          <div style="font-family:'Cinzel',serif;font-size:18px;font-weight:900;
                      background:linear-gradient(135deg,#f5c518,#a855f7);
                      -webkit-background-clip:text;-webkit-text-fill-color:transparent">
            BiasBreaker
          </div>
          <div style="font-size:9px;letter-spacing:3px;color:#6b6b8a;
                      font-family:'Share Tech Mono',monospace;margin-top:2px">
            AI HIRING SIMULATOR
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # ── Blind Mode Toggle ────────────────────────────────
        blind = st.toggle("🕶️ Blind Mode", value=s.get("blind_mode", False),
                          help="Hides name and education — judge on skills + experience only")
        if blind != s.get("blind_mode", False):
            st.session_state.blind_mode = blind
            st.rerun()

        st.markdown("---")

        # ── Session Stats ────────────────────────────────────
        if s.get("game_started", False):
            st.markdown(
                '<div style="font-family:\'Share Tech Mono\',monospace;font-size:9px;'
                'letter-spacing:3px;color:#6b6b8a;text-transform:uppercase;'
                'margin-bottom:8px">📊 Session Stats</div>',
                unsafe_allow_html=True)

            rank_colors = {
                "Beginner": "#6b6b8a", "Analyst": "#38bdf8",
                "Expert": "#a855f7", "Bias Master": "#f5c518"
            }
            rc = rank_colors.get(s.rank, "#6b6b8a")
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.03);border:1px solid #1e1e3a;
                        border-radius:10px;padding:12px;margin-bottom:8px">
              <div style="display:flex;justify-content:space-between;margin-bottom:6px">
                <span style="font-size:11px;color:#6b6b8a;font-family:'Share Tech Mono',monospace">RANK</span>
                <span style="font-size:12px;font-weight:700;color:{rc};font-family:'Cinzel',serif">{s.rank.upper()}</span>
              </div>
              <div style="display:flex;justify-content:space-between;margin-bottom:6px">
                <span style="font-size:11px;color:#6b6b8a;font-family:'Share Tech Mono',monospace">XP</span>
                <span style="font-size:12px;font-weight:700;color:#a855f7">{s.get('xp', 0)}</span>
              </div>
              <div style="display:flex;justify-content:space-between;margin-bottom:6px">
                <span style="font-size:11px;color:#6b6b8a;font-family:'Share Tech Mono',monospace">BEST STREAK</span>
                <span style="font-size:12px;font-weight:700;color:#f97316">{s.get('best_streak', 0)}x</span>
              </div>
              <div style="display:flex;justify-content:space-between">
                <span style="font-size:11px;color:#6b6b8a;font-family:'Share Tech Mono',monospace">HEALTH</span>
                <span style="font-size:12px;font-weight:700;color:{'#22c55e' if s.health > 70 else '#f5c518' if s.health > 30 else '#ef4444'}">{s.get('health', 100)}%</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Bias Meter ────────────────────────────────────
            bias_res = calculate_bias(s.history, s.resumes)
            bs_score = bias_res["bias_score"]
            bs_color = "#ef4444" if bs_score > 30 else ("#f5c518" if bs_score > 15 else "#22c55e")
            bs_label = "🚨 High Bias" if bs_score > 30 else ("⚠️ Moderate Bias" if bs_score > 15 else "✅ Fair Decision")
            bdown = bias_res.get("breakdown", {})

            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.03);border:1px solid #1e1e3a;
                        border-radius:10px;padding:12px;margin-bottom:8px">
              <div style="font-family:'Share Tech Mono',monospace;font-size:9px;
                          letter-spacing:2px;color:#6b6b8a;margin-bottom:8px">
                ⚖️ BIAS METER
              </div>
              <div style="background:rgba(255,255,255,0.05);border-radius:6px;
                          height:8px;overflow:hidden;margin-bottom:6px">
                <div style="height:100%;border-radius:6px;width:{min(100,bs_score)}%;
                            background:linear-gradient(90deg,{bs_color},{bs_color}aa);
                            transition:width 0.6s ease"></div>
              </div>
              <div style="font-size:11px;color:{bs_color};font-weight:700;margin-bottom:8px">
                {bs_label}
              </div>
              <div style="font-size:10px;color:#6b6b8a;font-family:'Share Tech Mono',monospace">
                Gap: {bdown.get('gap',0)}% · Edu: {bdown.get('education',0)}% · Exp: {bdown.get('experience',0)}%
              </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Dynamic Missions ──────────────────────────────
            from game_state import evaluate_skill_gaps
            skill_data = evaluate_skill_gaps(s.history, s.resumes)
            if skill_data["missions"]:
                st.markdown(
                    '<div style="font-family:\'Share Tech Mono\',monospace;font-size:9px;'
                    'letter-spacing:3px;color:#6b6b8a;text-transform:uppercase;'
                    'margin-bottom:6px">🎯 Active Missions</div>',
                    unsafe_allow_html=True)
                for m in skill_data["missions"][:2]:
                    st.markdown(
                        f'<div style="font-size:11px;color:#b0a8cc;margin-bottom:4px;'
                        f'line-height:1.5">{m}</div>',
                        unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(
            '<div style="font-size:10px;color:#3a3a5a;text-align:center;'
            'font-family:\'Share Tech Mono\',monospace">'
            'BiasBreaker v3.0 · AI Hiring Simulator</div>',
            unsafe_allow_html=True)


def render_result(res: dict, row: dict):
    """
    Renders the decision result with VS panel, What-If simulator,
    and the full student learning panel.
    """
    from logic.bias_analysis import get_bias_feedback_message

    is_boss       = res.get("is_boss", row.get("is_boss", False))
    ai_synced     = res.get("ai_synced", False)
    ai_choice     = "Hire" if st.session_state["_ai_pred"] == 1 else "Reject"
    player_choice = "Hire" if res.get("action", "") == "hire" else "Reject"

    # ── VS Panel ──────────────────────────────────────────────
    render_vs_panel(ai_choice, player_choice, ai_synced)

    # ── Narrative Result Box ───────────────────────────────────
    action = res.get("action", "skip")
    result = res.get("result", "skipped")
    cls = "result-box"
    if action == "skip":
        cls += " result-skip"
    elif result == "correct":
        cls += " result-boss" if is_boss else " result-win"
    else:
        cls += " result-lose"

    # Render message (supports multi-line with newline)
    msg_html = res.get("message", "").replace("\n", "<br>")
    st.markdown(f'<div class="{cls}">{msg_html}</div>', unsafe_allow_html=True)

    # ── XP & Health delta toast ───────────────────────────────
    xp   = res.get("xp_gain", 0)
    hp   = res.get("health_change", 0)
    sd   = res.get("score_delta", 0)
    delta_parts = []
    if sd != 0:  delta_parts.append(f"Score: {'+'if sd>0 else ''}{sd}")
    if xp != 0:  delta_parts.append(f"XP: +{xp}")
    if hp != 0:  delta_parts.append(f"Health: {'+'if hp>0 else ''}{hp}%")
    if delta_parts:
        dc = "#22c55e" if sd >= 0 else "#ef4444"
        st.markdown(
            f'<div style="text-align:center;font-size:12px;color:{dc};'
            f'font-family:\'Share Tech Mono\',monospace;letter-spacing:1px;margin-top:4px">'
            f'{" · ".join(delta_parts)}</div>',
            unsafe_allow_html=True)

    # ── What-If Simulator ─────────────────────────────────────
    with st.expander("🔮 What-If Simulator"):
        alt_action     = "Reject" if action == "hire" else "Hire"
        actual_outcome = "Good Hire" if res.get("outcome", 0) == 1 else "Bad Hire / Under-performer"
        alt_correct    = (alt_action == "Hire" and res.get("outcome", 0) == 1) or \
                         (alt_action == "Reject" and res.get("outcome", 0) == 0)
        alt_result_text = "✅ Correct" if alt_correct else "❌ Wrong"
        alt_color       = "#22c55e" if alt_correct else "#ef4444"
        whisper         = st.session_state.get("_whisper", {})
        prob_pct        = int(whisper.get("prob", 0.5) * 100)

        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.03);border:1px solid #1e1e3a;
                    border-radius:12px;padding:16px;font-size:13px;line-height:1.8">
          <div style="font-family:'Cinzel',serif;font-size:14px;color:#f5c518;
                      margin-bottom:10px">If you had chosen {alt_action.upper()}…</div>
          <div style="color:#b0a8cc">
            The candidate was actually: <b style="color:#e8e8f0">{actual_outcome}</b><br>
            That would have been: <b style="color:{alt_color}">{alt_result_text}</b><br>
            AI Hire Probability: <b style="color:#a855f7">{prob_pct}%</b>
          </div>
          <div style="margin-top:10px;font-size:11px;color:#6b6b8a;
                      font-family:'Share Tech Mono',monospace">
            Conclusion: Your original {action.upper()} was <b style="color:{'#22c55e' if result=='correct' else '#ef4444'}">{result.upper()}</b>.
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── 🎓 Student Learning Panel ─────────────────────────────
    with st.expander("🎓 Learn from this decision"):
        whisper = st.session_state.get("_whisper", {})
        prob    = whisper.get("prob", 0.5)
        conf    = whisper.get("confidence", "Unknown")
        rec     = whisper.get("recommendation", "N/A")
        lines   = whisper.get("lines", [])
        pct     = int(prob * 100)
        col     = "#22c55e" if prob >= 0.55 else "#ef4444" if prob < 0.45 else "#a855f7"

        # AI Explanation block
        st.markdown(f"""
        <div style="background:rgba(168,85,247,0.08);border:1px solid rgba(168,85,247,0.3);
                    border-left:4px solid #a855f7;border-radius:10px;padding:14px;
                    margin-bottom:12px">
          <div style="font-family:'Cinzel',serif;font-size:13px;color:#a855f7;
                      margin-bottom:8px">🤖 AI EXPLANATION</div>
          <div style="font-size:13px;color:#f5c518;font-weight:700;margin-bottom:6px">
            Recommendation: {rec}
          </div>
          <div style="font-size:11px;color:#6b6b8a;font-family:'Share Tech Mono',monospace;
                      margin-bottom:10px">
            Confidence: {conf} · Hire Probability: {pct}%
          </div>
          <div style="background:rgba(255,255,255,0.04);border-radius:6px;
                      height:6px;overflow:hidden;margin-bottom:10px">
            <div style="height:100%;border-radius:6px;width:{pct}%;
                        background:{col};transition:width 0.8s ease"></div>
          </div>
          <div style="font-size:12px;color:#b0a8cc">
            <b style="color:#e8e8f0">Top Feature Signals:</b>
          </div>
        """, unsafe_allow_html=True)

        for ln in lines:
            st.markdown(
                f'<div style="font-size:12px;color:#b0a8cc;margin:3px 0;">· {ln}</div>',
                unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Bias feedback block
        if res.get("bias_flag"):
            bias_type = calculate_bias(
                st.session_state.history, st.session_state.resumes
            ).get("bias_type", "Gap Bias")
            bias_msg = get_bias_feedback_message(bias_type, row)
            st.markdown(f"""
            <div style="margin-top:4px;padding:12px;background:rgba(239,68,68,0.1);
                        border:1px solid #ef4444;border-radius:8px">
              <span style="color:#ef4444;font-weight:bold;font-family:'Cinzel',serif">
                ⚠️ BIAS DETECTED
              </span><br>
              <span style="font-size:12px;color:#c0a8a8;line-height:1.6">{bias_msg}</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Ollama LLM Feedback (lazy-loaded) ────────────────────
    if not res.get("_llm_loaded") and ollama_available() and action != "skip":
        if res.get("llm_feedback") is None:
            res["llm_feedback"] = "ANALYZING..."
            
            def fetch_feedback():
                try:
                    fb = ollama_feedback(row, action)
                    res["llm_feedback"] = fb
                    res["_llm_loaded"]  = True
                except:
                    res["llm_feedback"] = None
            
            threading.Thread(target=fetch_feedback, daemon=True).start()

    llm_feedback = res.get("llm_feedback")
    if llm_feedback == "ANALYZING...":
        st.markdown(
            f'<div style="margin-top:8px;font-size:12px;color:var(--muted);'
            f'font-style:italic;animation:pulse 1.5s infinite;">🤖 AI is drafting feedback...</div>',
            unsafe_allow_html=True,
        )
    elif llm_feedback:
        st.markdown(
            f'<div style="margin-top:8px;font-size:13px;color:#b0a8cc;'
            f'font-style:italic;">🤖 {llm_feedback}</div>',
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
    s         = st.session_state
    score     = s.score
    hist      = s.history
    n_correct = sum(1 for h in hist if h.get("correct"))
    accuracy  = int(n_correct / len(hist) * 100) if hist else 0

    bias_res  = calculate_bias(hist, s.resumes)
    bdown     = bias_res.get("breakdown", {})
    bias_meta = bias_res.get("meta", {})

    # ── Hero Banner ───────────────────────────────────────────
    st.markdown(f"""
    <div class="gameover-screen glass-container neon-border-gold">
      <div class="gameover-emoji">{'🏆' if accuracy >= 70 else '🛡️' if accuracy >= 50 else '💀'}</div>
      <div class="gameover-title">{'LEVEL MASTERED' if accuracy >= 70 else 'ROUND COMPLETE'}</div>
      <div class="gameover-score">{score}</div>
      <div class="gameover-label">FINAL SCORE · RANK: {s.rank.upper()}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Top-line KPI cards ────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-v-box"><b>ACCURACY</b><br><h2 style="color:var(--blue)">{accuracy}%</h2></div>', unsafe_allow_html=True)
    with c2:
        bs_col = "var(--red)" if bias_res["bias_score"] > 30 else ("var(--orange)" if bias_res["bias_score"] > 15 else "var(--green)")
        st.markdown(f'<div class="stat-v-box"><b>BIAS SCORE</b><br><h2 style="color:{bs_col}">{bias_res["bias_score"]}</h2></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-v-box"><b>XP EARNED</b><br><h2 style="color:var(--purple)">{s.xp}</h2></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="stat-v-box"><b>BEST STREAK</b><br><h2 style="color:var(--orange)">{s.best_streak}x</h2></div>', unsafe_allow_html=True)

    # ── Bias Breakdown card ────────────────────────────────────
    st.markdown("### ⚖️ Bias Analysis Report")
    bi_icon = bias_meta.get("icon", "⚖️")
    bi_desc = bias_meta.get("description", "")
    bi_tip  = bias_meta.get("tip", "")
    bi_lvl  = bias_res["bias_level"]
    bi_type = bias_res["bias_type"]
    bi_col  = "#ef4444" if bi_lvl == "High" else ("#f5c518" if bi_lvl == "Moderate" else "#22c55e")

    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.03);border:1px solid #1e1e3a;
                border-radius:14px;padding:18px;margin-bottom:14px">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
        <span style="font-size:28px">{bi_icon}</span>
        <div>
          <div style="font-family:'Cinzel',serif;font-size:15px;color:{bi_col};font-weight:700">
            {bi_lvl} · {bi_type}
          </div>
          <div style="font-size:12px;color:#6b6b8a">{bi_desc}</div>
        </div>
      </div>
      <div style="font-size:12px;color:#b0a8cc;margin-bottom:12px">{bi_tip}</div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px">
        <div style="text-align:center;background:rgba(255,255,255,0.03);
                    border:1px solid #1e1e3a;border-radius:8px;padding:8px">
          <div style="font-size:9px;color:#6b6b8a;letter-spacing:2px;font-family:'Share Tech Mono',monospace">GAP BIAS</div>
          <div style="font-size:18px;font-weight:700;color:#38bdf8;font-family:'Cinzel',serif">{bdown.get('gap',0)}%</div>
        </div>
        <div style="text-align:center;background:rgba(255,255,255,0.03);
                    border:1px solid #1e1e3a;border-radius:8px;padding:8px">
          <div style="font-size:9px;color:#6b6b8a;letter-spacing:2px;font-family:'Share Tech Mono',monospace">EDU BIAS</div>
          <div style="font-size:18px;font-weight:700;color:#a855f7;font-family:'Cinzel',serif">{bdown.get('education',0)}%</div>
        </div>
        <div style="text-align:center;background:rgba(255,255,255,0.03);
                    border:1px solid #1e1e3a;border-radius:8px;padding:8px">
          <div style="font-size:9px;color:#6b6b8a;letter-spacing:2px;font-family:'Share Tech Mono',monospace">EXP BIAS</div>
          <div style="font-size:18px;font-weight:700;color:#f97316;font-family:'Cinzel',serif">{bdown.get('experience',0)}%</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── AI Coach Suggestion ────────────────────────────────────
    st.markdown("### 🤖 AI Coach Analysis")
    if bias_res["bias_score"] > 30:
        suggestion = f"You show a high tendency towards <b>{bi_type}</b>. {bi_tip}"
    elif accuracy < 50:
        suggestion = ("Your accuracy needs work. Use the <b>AI Whisper</b> hints more often — "
                      "follow the AI's recommendations to understand the ML model's logic.")
    elif s.best_streak < 3:
        suggestion = ("Work on building consecutive correct decisions to unlock streak bonuses. "
                      "Focus on skill breadth and experience over education level.")
    else:
        suggestion = ("Exceptional performance! You've balanced speed, objectivity, and "
                      "AI collaboration perfectly. You're a Bias Master in the making!")

    st.markdown(f"""
    <div style="background:rgba(168,85,247,0.1);border:1px solid var(--purple);
                border-radius:12px;padding:20px;margin-bottom:14px">
      <div style="font-family:'Cinzel',serif;font-size:14px;color:var(--purple);
                  margin-bottom:10px">💬 AI COACH FEEDBACK</div>
      <div style="font-size:14px;color:#c8c0e0;line-height:1.7">"{suggestion}"</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Session Breakdown table ────────────────────────────────
    st.markdown('<div style="font-family:Cinzel,serif;font-size:16px;margin-bottom:10px;color:#f5c518">📊 Session Breakdown</div>', unsafe_allow_html=True)
    breakdown = [
        ("Bias Level",        bi_lvl,                     "neu"),
        ("Primary Bias Type", bi_type,                     "bad" if bias_res["bias_score"] > 0 else "good"),
        ("Correct Decisions", f"{n_correct}/{len(hist)}",  "good"),
        ("Accuracy",          f"{accuracy}%",               "good" if accuracy >= 70 else "neu"),
        ("Best Streak",       f"{s.best_streak}x",          "good"),
        ("XP Earned",         s.xp,                        "good"),
        ("Rank Achieved",     s.rank,                      "good"),
        ("Final Health",      f"{s.health}%",               "good" if s.health > 50 else "bad"),
    ]
    for label, val, cls in breakdown:
        st.markdown(
            f'<div class="stat-row-go"><span class="srow-key">{label}</span>'
            f'<span class="srow-{cls}">{val}</span></div>',
            unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Save & Leaderboard
    save_leaderboard(s.player_name, score, n_correct, len(hist))
    render_leaderboard()
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    _, c, _ = st.columns([1, 2, 1])
    with c:
        next_diff = "hard" if score > 100 else ("normal" if score > 30 else "easy")
        if st.button(f"🔄  Start Next Round ({next_diff.upper()})", use_container_width=True):
            p_name = s.player_name
            for k in list(st.session_state.keys()):
                del st.session_state[k]
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
                # Non-blocking threaded Ollama call
                if ollama_available():
                    st.session_state["_llm_whisper"] = "ANALYZING..."
                    
                    def fetch_whisper():
                        try:
                            txt = get_ai_whisper_llm(row, whisper.get("lines", []))
                            st.session_state["_llm_whisper"] = txt
                        except:
                            st.session_state["_llm_whisper"] = None

                    threading.Thread(target=fetch_whisper, daemon=True).start()
                else:
                    st.session_state["_llm_whisper"] = None
                st.rerun()
        else:
            st.markdown(
                '<div class="ai-locked">🔒 No AI Hints remaining — trust your instincts!</div>',
                unsafe_allow_html=True,
            )

    # ── Power-Ups ────────────────────────────────────────
    activated = render_powerup_bar()
    if activated == "second_look":
        st.session_state.powerups["second_look"]     = 0
        st.session_state.hint_shown                  = True
        st.session_state["_hint_used_this_round"]    = True
        st.session_state.second_look_used            = True
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
        # Use modular decision engine
        res = process_decision(
            action, row, st.session_state, ai_pred, prob
        )
        
        # Update session state from engine results
        st.session_state.score += res["score_delta"]
        st.session_state.health += res["health_change"]
        st.session_state.xp += res["xp_gain"]
        
        # Clamp health
        st.session_state.health = max(0, min(100, st.session_state.health))
        
        # Rank Logic
        if st.session_state.xp > 1000: st.session_state.rank = "Bias Master"
        elif st.session_state.xp > 500: st.session_state.rank = "Expert"
        elif st.session_state.xp > 200: st.session_state.rank = "Analyst"
        
        if res["result"] == "correct":
            st.session_state.streak += 1
            if st.session_state.streak > st.session_state.best_streak:
                st.session_state.best_streak = st.session_state.streak
        elif action != "skip":
            st.session_state.streak = 0
            st.session_state.lives -= 1 # Keep lives for backward compatibility if needed, though health is primary now

        # Update decision log for active learning
        st.session_state.decision_log.append({
            **row, "outcome": int(row["outcome"])
        })
        
        st.session_state["_needs_retrain"] = True

        st.session_state.history.append({
            "round": round_idx, "action": action,
            "outcome": int(row["outcome"]), "correct": (res["result"] == "correct"),
            "followed_ai": res.get("ai_synced", False), "delta": res["score_delta"],
        })
        
        # Prepare result metadata for render_result
        st.session_state.last_result = {
            "action": action, 
            **res,
            "outcome": int(row["outcome"]),
            "llm_feedback": None,
            "_llm_loaded": False,
        }
        
        st.session_state.awaiting_next = True
        
        # Game Over checks
        if st.session_state.lives <= 0 or st.session_state.health <= 0:
            st.session_state.game_over = True
        st.rerun()


# ══════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════
def main():
    init_state()
    render_sidebar()
    model, explainer, acc = train_model()

    if st.session_state.game_over:
        render_game_over()
        return
    if not st.session_state.game_started:
        render_splash(acc)
        return
        
    # Active learning check before round starts
    if st.session_state.get("_needs_retrain", False) and len(st.session_state.decision_log) >= 3:
        with st.status("🧠 AI is learning from your decisions...", expanded=False) as status:
            time.sleep(0.5) # Narrative pause for effect
            res = retrain_with_decisions(st.session_state.decision_log)
            if res:
                st.session_state["active_model"] = res[0]
                st.session_state["active_explainer"] = res[1]
                status.update(label="🧠 AI Wisdom Upgraded!", state="complete")
            else:
                status.update(label="🧠 Internal Neural Drift detected", state="error")
        st.session_state["_needs_retrain"] = False
        
    # Use active learning model if available
    active_m = st.session_state.get("active_model", model)
    active_e = st.session_state.get("active_explainer", explainer)

    run_game(active_m, active_e)


if __name__ == "__main__":
    main()
