import streamlit as st

def render_vs_panel(ai_decision, player_decision):
    if player_decision is None:
        st.markdown(
            '<div style="margin:12px 0;padding:12px;border:1px solid #444;border-radius:12px;' 
            'background:rgba(255,255,255,0.03);text-align:center;color:#ccc;">'
            '🤖 AI vs 🧑 Player decisions will appear here after your choice.</div>',
            unsafe_allow_html=True,
        )
        return

    match = (ai_decision == player_decision)
    glow = "box-shadow: 0 0 16px rgba(34, 197, 94, .65);" if match else "box-shadow: 0 0 14px rgba(239, 68, 68, .65);"
    label = "✅ SYNCED DECISION" if match else "⚡ DECISION CLASH"
    color = "#22c55e" if match else "#ef4444"

    st.markdown(f"""
    <div style="border:1px solid #444;border-radius:14px;padding:12px;background:rgba(7,7,12,.7);{glow};transition:all .3s ease;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;font-size:13px;">
        <span style="color:#a78bfa;font-weight:700;">🤖 AI: {ai_decision.upper()}</span>
        <span style="color:{color};font-size:12px;font-weight:700;">{label}</span>
        <span style="color:#38bdf8;font-weight:700;">🧑 YOU: {player_decision.upper()}</span>
      </div>
      <div style="height:6px;background:#23232b;border-radius:6px;overflow:hidden;">
        <div style="width:100%;height:100%;background:linear-gradient(90deg,#4f46e5,#22d3ee);animation:pulse-vs 1.3s ease-in-out infinite;"></div>
      </div>
    </div>
    <style>@keyframes pulse-vs {{0%,100%{{transform:translateX(-2%)}}50%{{transform:translateX(2%)}}}}</style>
    """ , unsafe_allow_html=True)
