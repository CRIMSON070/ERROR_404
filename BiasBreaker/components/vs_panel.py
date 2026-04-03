"""
components/vs_panel.py
═══════════════════════════════════════════════════════════
AI vs Player decision comparison panel.
Animated neon glow, pulse effects, and decision clash UI.
═══════════════════════════════════════════════════════════
"""

import streamlit as st


def render_vs_panel(ai_choice: str, player_choice: str, ai_synced: bool):
    """
    Renders the animated AI vs Player decision panel.

    Args:
        ai_choice     (str):  'Hire' or 'Reject'
        player_choice (str):  'Hire' or 'Reject'
        ai_synced     (bool): True if both decisions match
    """
    green  = "#22c55e"
    red    = "#ef4444"
    border = green if ai_synced else red
    glow   = (
        f"0 0 30px rgba(34,197,94,0.55), 0 0 60px rgba(34,197,94,0.25)"
        if ai_synced
        else f"0 0 30px rgba(239,68,68,0.55), 0 0 60px rgba(239,68,68,0.25)"
    )
    status_text  = "✨ SYNCED DECISION ✨" if ai_synced else "⚡ DECISION CLASH ⚡"
    pulse_anim   = "" if ai_synced else "vsPulse 1.6s ease-in-out infinite"
    ai_icon      = "🟢" if ai_choice.lower() == "hire" else "🔴"
    pl_icon      = "🟢" if player_choice.lower() == "hire" else "🔴"

    ai_col = green if ai_choice.lower() == "hire" else red
    pl_col = green if player_choice.lower() == "hire" else red

    st.markdown(f"""
    <style>
    @keyframes vsPulse {{
        0%,100% {{ box-shadow: 0 0 0 rgba(239,68,68,0); }}
        50%      {{ box-shadow: {glow}; }}
    }}
    @keyframes vsSlideIn {{
        from {{ opacity:0; transform:translateY(20px); }}
        to   {{ opacity:1; transform:translateY(0); }}
    }}
    @keyframes vsGlow {{
        0%,100% {{ text-shadow: 0 0 8px currentColor; }}
        50%      {{ text-shadow: 0 0 25px currentColor, 0 0 50px currentColor; }}
    }}
    .vs-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(135deg, rgba(10,10,25,0.9), rgba(16,16,40,0.9));
        backdrop-filter: blur(14px);
        border: 2px solid {border};
        border-radius: 20px;
        padding: 22px 28px;
        margin: 18px 0 6px;
        box-shadow: {glow};
        animation: vsSlideIn 0.4s ease, {pulse_anim};
        position: relative;
        overflow: hidden;
    }}
    .vs-container::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, {border}, transparent, {border});
        animation: goldShimmer 2s linear infinite;
    }}
    .vs-side {{
        flex: 1;
        text-align: center;
    }}
    .vs-entity-label {{
        font-family: 'Share Tech Mono', monospace;
        font-size: 9px;
        letter-spacing: 3px;
        color: #6b6b8a;
        text-transform: uppercase;
        margin-bottom: 6px;
    }}
    .vs-decision-icon {{
        font-size: 36px;
        margin-bottom: 6px;
        line-height: 1;
    }}
    .vs-decision-text {{
        font-family: 'Cinzel', serif;
        font-size: 20px;
        font-weight: 900;
        letter-spacing: 3px;
        animation: vsGlow 2s ease-in-out infinite;
    }}
    .vs-divider {{
        font-family: 'Share Tech Mono', monospace;
        font-size: 26px;
        color: #3a3a5a;
        padding: 0 22px;
        font-weight: bold;
        letter-spacing: 2px;
    }}
    .vs-status {{
        text-align: center;
        padding: 8px 0 4px;
        font-family: 'Share Tech Mono', monospace;
        font-size: 13px;
        letter-spacing: 4px;
        font-weight: bold;
        color: {border};
        text-transform: uppercase;
        animation: vsGlow 2s ease-in-out infinite;
    }}
    </style>

    <div class="vs-container">
      <div class="vs-side">
        <div class="vs-entity-label">🤖 AI Decision</div>
        <div class="vs-decision-icon">{ai_icon}</div>
        <div class="vs-decision-text" style="color:{ai_col}">{ai_choice.upper()}</div>
      </div>
      <div class="vs-divider">VS</div>
      <div class="vs-side">
        <div class="vs-entity-label">🧑 Your Decision</div>
        <div class="vs-decision-icon">{pl_icon}</div>
        <div class="vs-decision-text" style="color:{pl_col}">{player_choice.upper()}</div>
      </div>
    </div>
    <div class="vs-status">{status_text}</div>
    """, unsafe_allow_html=True)
