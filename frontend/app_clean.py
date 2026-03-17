"""
IPL Auction Strategy Platform - Clean Modern UI
Using Streamlit Native Components for Reliability
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import time
import os

# ==================== CONFIGURATION ====================

API_BASE_URL = "http://localhost:8000"
BUDGET_LIMIT = 120.0  # Crore
MAX_PLAYERS = 25

st.set_page_config(
    page_title="IPL Auction Strategy Platform",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme and animations
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Dark Theme Background */
    .stApp {
        background: linear-gradient(135deg, rgba(10,25,47,0.95) 0%, rgba(18,38,64,0.95) 100%);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0A192F 0%, #122640 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: #E6F1FF !important;
    }
    
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(26, 31, 46, 0.9) 0%, rgba(38, 46, 66, 0.9) 100%);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(100, 200, 255, 0.1);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    div[data-testid="stMetricValue"] {
        color: #667eea !important;
        font-size: 2.5em !important;
        font-weight: 700 !important;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-size: 0.9em !important;
        font-weight: 500 !important;
    }
    
    /* Info Boxes */
    div[data-testid="stInfo"], div[data-testid="stSuccess"], div[data-testid="stWarning"] {
        background: rgba(26, 31, 46, 0.9);
        border: 1px solid rgba(100, 200, 255, 0.2);
        border-radius: 8px;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #E6F1FF !important;
    }
    
    /* Player Cards */
    .player-card {
        background: linear-gradient(135deg, rgba(26, 31, 46, 0.95) 0%, rgba(38, 46, 66, 0.95) 100%);
        border-radius: 12px;
        padding: 16px;
        border-left: 4px solid #667eea;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
    
    .player-card:hover {
        transform: translateX(5px);
        border-left-color: #764ba2;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
    }
    
    /* Status Indicators */
    .status-overpriced {
        background: rgba(255, 107, 107, 0.15);
        border-left: 4px solid #ff6b6b;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    
    .status-undervalued {
        background: rgba(76, 175, 80, 0.15);
        border-left: 4px solid #4CAF50;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================

if 'page' not in st.session_state:
    st.session_state.page = "Home"

if 'selected_players' not in st.session_state:
    st.session_state.selected_players = []

if 'cached_suggestions' not in st.session_state:
    st.session_state.cached_suggestions = None

# ==================== HELPER FUNCTIONS ====================

def get_all_players():
    """Fetch all players from backend"""
    try:
        response = requests.get(f"{API_BASE_URL}/players?limit=1000", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        else:
            return []
    except Exception as e:
        st.error(f"Error fetching players: {e}")
        return []

def add_player_to_team(player_data):
    """Add player to selected team"""
    existing_names = [p['player_name'] for p in st.session_state.selected_players]
    
    if player_data['player_name'] not in existing_names:
        if len(st.session_state.selected_players) < MAX_PLAYERS:
            current_budget = sum([p.get('sold_price', 0) for p in st.session_state.selected_players])
            
            if current_budget + player_data.get('sold_price', 0) <= BUDGET_LIMIT:
                st.session_state.selected_players.append(player_data)
                return True, "Player added successfully!"
            else:
                return False, "Budget exceeded!"
        else:
            return False, f"Maximum {MAX_PLAYERS} players reached!"
    
    return False, "Player already in team!"

# ==================== SIDEBAR ====================

def render_sidebar():
    """Render sidebar navigation"""
    with st.sidebar:
        # Logo and Title
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("### 🏏")
        with col2:
            st.markdown("""
            <div style='margin-top: 10px;'>
                <h4 style='color: #E6F1FF; margin: 0;'>IPL AUCTION</h4>
                <p style='color: #667eea; margin: 0; font-size: 0.8em;'>STRATEGY PLATFORM</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        pages = [
            ("Home", "🏠"),
            ("Players", "👥"),
            ("Team Builder", "🛠️"),
            ("Analytics", "📊"),
            ("AI Suggestions", "🤖"),
            ("Best XI", "⭐"),
            ("Team Optimization AI", "🔥"),
            ("Auction Strategy", "💼")
        ]
        
        for page_name, icon in pages:
            if st.button(
                f"{icon} {page_name}",
                key=f"nav_{page_name}",
                use_container_width=True
            ):
                st.session_state.page = page_name
                st.rerun()
        
        st.markdown("---")
        
        # Budget Summary
        if 'selected_players' in st.session_state:
            budget_spent = sum([p.get('sold_price', 0) for p in st.session_state.selected_players])
            budget_remaining = 120 - budget_spent
            players_count = len(st.session_state.selected_players)
            
            st.markdown("### 💰 Budget Overview")
            st.metric("Budget Remaining", f"₹{budget_remaining:.1f} Cr", f"₹{budget_spent:.1f} Cr used")
            st.progress(budget_spent / 120)
            st.markdown(f"**👥 {players_count}/{MAX_PLAYERS}** Players Selected")

# ==================== HOME PAGE ====================

def render_home():
    """Render Home Page"""
    st.title("🏏 IPL AUCTION STRATEGY PLATFORM")
    st.markdown("### 🔥 Deep Learning Powered Team Optimization")
    st.markdown("---")
    
    # Quick Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 Total Players",
            value="623"
        )
    
    with col2:
        st.metric(
            label="🛡️ Your Squad",
            value=f"{len(st.session_state.selected_players)}/{MAX_PLAYERS}"
        )
    
    with col3:
        budget_spent = sum([p.get('sold_price', 0) for p in st.session_state.selected_players])
        st.metric(
            label="💰 Budget Used",
            value=f"₹{budget_spent:.1f} Cr",
            delta=f"{(budget_spent/120)*100:.1f}%"
        )
    
    with col4:
        st.metric(
            label="🤖 AI Models",
            value="4 Active"
        )
    
    st.markdown("---")
    
    # Features
    st.header("✨ KEY FEATURES")
    feat_col1, feat_col2, feat_col3 = st.columns(3)
    
    with feat_col1:
        st.info("**🧠 Multi-Task DNN**\n\nPredicts Player Value, Performance Score, and Risk Score using advanced deep learning.")
    
    with feat_col2:
        st.info("**⚡ Real-time Analysis**\n\nInstant AI-powered insights with overpriced/undervalued detection.")
    
    with feat_col3:
        st.info("**🎯 Smart Recommendations**\n\nPersonalized player suggestions based on embeddings.")
    
    # DL Models
    st.markdown("---")
    st.header("🔬 DEEP LEARNING MODELS")
    model_col1, model_col2 = st.columns(2)
    
    with model_col1:
        st.success("""
        **📊 Player Value Network**
        - Architecture: Multi-Task DNN (128→64→32)
        - Outputs: Value ₹, Performance (0-100), Risk (0-1)
        - Features: 50-dimensional embeddings
        """)
    
    with model_col2:
        st.success("""
        **🔄 Embedding Network**
        - Size: 32-dim L2-normalized
        - Similarity: Cosine similarity
        - Application: Player matching
        """)

# ==================== PLAYERS PAGE ====================

def render_players():
    """Render Players Page"""
    st.title("👥 PLAYER DATABASE")
    
    # Filters
    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        search = st.text_input("🔍 Search", placeholder="Search by name...")
    with col2:
        role_filter = st.selectbox("Role", ["All", "Batsman", "Bowler", "All-rounder", "Wicket-keeper"])
    with col3:
        team_filter = st.selectbox("Team", ["All"] + ["CSK", "MI", "RCB", "KKR", "SRH", "DC", "PBKS", "RR", "GT", "LSG"])
    
    # Load players
    with st.spinner("Loading players..."):
        all_players = get_all_players()
    
    if not all_players:
        st.error("Failed to load players. Make sure backend is running.")
        return
    
    # Filter
    filtered = all_players
    if search:
        filtered = [p for p in filtered if search.lower() in p.get('player_name', '').lower()]
    if role_filter != "All":
        filtered = [p for p in filtered if role_filter.lower() in p.get('role', '').lower()]
    if team_filter != "All":
        filtered = [p for p in filtered if p.get('team', '') == team_filter]
    
    st.success(f"**{len(filtered)}** players found")
    
    # Display
    cols = st.columns(3)
    for i, player in enumerate(filtered[:30]):
        with cols[i % 3]:
            in_team = any(p['player_name'] == player['player_name'] for p in st.session_state.selected_players)
            
            st.markdown(f"""
            <div class="player-card fade-in">
                <div style="font-size: 1.1em; font-weight: 600; color: #E6F1FF;">{player['player_name']}</div>
                <div style="color: #94A3B8; font-size: 0.9em;">{player['role']} • {player['team']}</div>
                <div style="margin-top: 8px;">
                    <span style="background: rgba(102, 126, 234, 0.15); padding: 4px 8px; border-radius: 6px; color: #667eea; font-size: 0.8em; font-weight: 600;">₹{player.get('sold_price', 0):.2f} Cr</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if not in_team:
                if st.button("➕ Add to Team", key=f"add_{player['player_name']}", use_container_width=True):
                    success, msg = add_player_to_team(player)
                    if success:
                        st.success(f"✅ Added {player['player_name']}!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(msg)
            else:
                st.info("✓ In Team")
    
    if len(filtered) > 30:
        st.info(f"Showing 30 of {len(filtered)} players.")

# ==================== MAIN APP ====================

def main():
    """Main application"""
    render_sidebar()
    
    page = st.session_state.page
    
    if page == "Home":
        render_home()
    elif page == "Players":
        render_players()
    elif page == "Team Builder":
        st.title("🛠️ TEAM BUILDER")
        squad = st.session_state.selected_players
        if not squad:
            st.warning("Your squad is empty! Go to Players tab.")
        else:
            budget_spent = sum([p.get('sold_price', 0) for p in squad])
            st.metric("Budget Spent", f"₹{budget_spent:.1f} Cr", f"₹{120-budget_spent:.1f} Cr left")
            st.write(f"**Selected:** {len(squad)}/{MAX_PLAYERS} players")
            for i, player in enumerate(squad):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{player['player_name']}** ({player['role']}) - ₹{player.get('sold_price', 0):.2f} Cr")
                with col2:
                    if st.button("❌", key=f"remove_{i}"):
                        st.session_state.selected_players.pop(i)
                        st.rerun()
    elif page == "Analytics":
        st.title("📊 ANALYTICS")
        squad = st.session_state.selected_players
        if not squad:
            st.warning("No players selected.")
        else:
            budget_spent = sum([p.get('sold_price', 0) for p in squad])
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=budget_spent,
                gauge={'axis': {'range': [None, 120]}},
                title={'text': "<b>BUDGET</b>"}
            ))
            st.plotly_chart(fig, use_container_width=True)
    elif page == "AI Suggestions":
        st.title("🤖 AI SUGGESTIONS")
        if len(st.session_state.selected_players) < 11:
            st.warning("Need at least 11 players.")
        else:
            if st.button("🤖 Get AI Recommendations"):
                with st.spinner("Analyzing..."):
                    payload = {"selected_players": st.session_state.selected_players}
                    try:
                        response = requests.post(f"{API_BASE_URL}/suggestions", json=payload, timeout=15)
                        if response.status_code == 200:
                            st.session_state.cached_suggestions = response.json()
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
    elif page == "Best XI":
        st.title("⭐ BEST PLAYING XI")
        if len(st.session_state.selected_players) < 11:
            st.warning("Need at least 11 players.")
        else:
            if st.button("🎯 Generate Best XI"):
                with st.spinner("Generating..."):
                    payload = {"selected_players": st.session_state.selected_players}
                    try:
                        response = requests.post(f"{API_BASE_URL}/best-xi", json=payload, timeout=15)
                        if response.status_code == 200:
                            result = response.json()
                            st.success("Best XI Generated!")
                            playing_xi = result.get('playing_xi', [])
                            for i, player in enumerate(playing_xi, 1):
                                st.markdown(f"**{i}. {player['player_name']}** ({player['role']})")
                    except Exception as e:
                        st.error(f"Error: {e}")
    elif page == "Team Optimization AI":
        st.title("🔥 TEAM OPTIMIZATION AI")
        st.markdown("Deep Learning-Powered Team Evaluation")
        if len(st.session_state.selected_players) < 11:
            st.warning("Need at least 11 players.")
        else:
            if st.button("🤖 Run AI Analysis"):
                with st.spinner("AI is analyzing..."):
                    payload = {"selected_players": st.session_state.selected_players}
                    try:
                        response = requests.post(f"{API_BASE_URL}/team-optimization", json=payload, timeout=15)
                        if response.status_code == 200:
                            data = response.json().get('data', {})
                            st.metric("Efficiency Score", f"{data.get('efficiency_score', 0):.2f}")
                            st.metric("Predicted Value", f"₹{data.get('total_predicted_value', 0):.2f} Cr")
                            
                            overpriced = data.get('overpriced_players', [])
                            undervalued = data.get('undervalued_players', [])
                            
                            if overpriced:
                                st.markdown("### 🔴 Overpriced Players")
                                for player in overpriced[:3]:
                                    st.markdown(f"- **{player['player_name']}**: Overpriced by ₹{player['actual_price'] - player['predicted_value']:.2f}Cr")
                            
                            if undervalued:
                                st.markdown("### 🟢 Undervalued Players")
                                for player in undervalued[:3]:
                                    st.markdown(f"- **{player['player_name']}**: Undervalued by ₹{player['predicted_value'] - player['actual_price']:.2f}Cr")
                        elif response.status_code == 400:
                            st.error(response.json().get('detail', 'Error'))
                    except Exception as e:
                        st.error(f"Error: {e}")
    elif page == "Auction Strategy":
        st.title("💼 AUCTION STRATEGY")
        st.info("""
        **Budget Allocation Strategy:**
        - Top Picks (3-4): ₹15-23 Cr each
        - Mid-range (5-7): ₹5-12 Cr each
        - Budget Picks (3-5): ₹1-4 Cr each
        
        **Key Insights:**
        - Don't overspend on WKs (1-2 enough)
        - Invest in quality batsmen
        - All-rounders provide best value
        - Need at least 4 specialist bowlers
        """)

if __name__ == "__main__":
    main()
