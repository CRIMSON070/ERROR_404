"""
components/powerups.py
═══════════════════════════════════════════════════════════
Power-up selection panel for BiasBreaker.
Renders Bias Shield, Lucky Charm, Second Look with
animated status chips and usage buttons.
═══════════════════════════════════════════════════════════
"""

import streamlit as st


_PU_DETAILS = {
    "bias_shield": {
        "icon": "🛡️",
        "name": "Bias Shield",
        "desc": "Block 1 bias penalty",
        "active_key": "bias_shield_active",
        "color": "#38bdf8",
    },
    "lucky_charm": {
        "icon": "🍀",
        "name": "Lucky Charm",
        "desc": "Double reward if AI agrees",
        "active_key": "lucky_charm_active",
        "color": "#22c55e",
    },
    "second_look": {
        "icon": "🔍",
        "name": "Second Look",
        "desc": "Reveal AI hint instantly",
        "active_key": "second_look_used",
        "color": "#f5c518",
    },
}


def render_powerup_panel() -> str | None:
    """
    Render the power-up selection row.
    Returns the key of the activated power-up, or None.
    """
    pu = st.session_state.powerups
    activated = None

    # Styled header
    st.markdown(
        '<div style="font-family:\'Share Tech Mono\',monospace;font-size:9px;'
        'letter-spacing:3px;color:#6b6b8a;text-transform:uppercase;margin-bottom:6px;">'
        '⚡ Power-Ups</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(3)

    for col, (key, meta) in zip(cols, _PU_DETAILS.items()):
        count     = pu.get(key, 0)
        is_active = st.session_state.get(meta["active_key"], False)
        is_used   = (count == 0 and not is_active)
        color     = meta["color"]

        if is_active:
            state_label = "ACTIVE"
            border_style = f"border-color:{color};box-shadow:0 0 12px {color}40;"
            opacity = "1"
        elif is_used:
            state_label = "USED"
            border_style = "border-color:#2a2a3a;filter:grayscale(1);"
            opacity = "0.4"
        else:
            state_label = "READY"
            border_style = f"border-color:{color}60;"
            opacity = "1"

        with col:
            st.markdown(f"""
            <div style="
                background:rgba(255,255,255,0.03);
                border:1px solid {color}60;
                border-radius:12px;
                padding:10px 8px;
                text-align:center;
                opacity:{opacity};
                transition:all 0.2s ease;
                {border_style}
            ">
              <div style="font-size:22px;margin-bottom:4px">{meta['icon']}</div>
              <div style="font-size:11px;font-weight:700;color:#e8e8f0">{meta['name']}</div>
              <div style="font-size:9px;color:#6b6b8a;letter-spacing:1px;
                          font-family:'Share Tech Mono',monospace;margin-top:2px">{meta['desc']}</div>
              <div style="font-size:8px;color:{color};letter-spacing:2px;
                          font-family:'Share Tech Mono',monospace;margin-top:4px;
                          font-weight:700">{state_label}</div>
            </div>
            """, unsafe_allow_html=True)

            if count > 0 and not is_active:
                if st.button(
                    f"{meta['icon']} Activate",
                    key=f"pu_btn_{key}",
                    use_container_width=True,
                ):
                    activated = key
            else:
                st.button(
                    f"{meta['icon']} {'Active' if is_active else 'Used'}",
                    key=f"pu_btn_dis_{key}",
                    disabled=True,
                    use_container_width=True,
                )

    return activated
