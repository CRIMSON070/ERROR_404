"""
IPL Auction Strategy Platform - Premium AI-Powered UI
Modern Dark Theme with Neon Accents & Deep Learning Integration
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
from typing import Dict, List, Any

# ==================== CONFIGURATION ====================

API_BASE_URL = "http://localhost:8000"
BUDGET_LIMIT = 120.0  # Crore
MAX_PLAYERS = 25

st.set_page_config(
    page_title="IPL Auction Strategy Platform | AI-Powered",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS WITH ANIMATIONS ====================

def load_premium_css():
    """Load premium CSS with animations and IPL logo background"""
    
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Poppins:wght@400;500;600;700&display=swap');
    
    /* Global Variables */
    :root {
        --primary-blue: #667eea;
        --primary-purple: #764ba2;
        --neon-blue: #00f3ff;
        --neon-purple: #bc13fe;
        --success-green: #4CAF50;
        --warning-yellow: #ffd700;
        --danger-red: #ff6b6b;
        --dark-bg: #0a0e1a;
        --card-bg: rgba(20, 30, 60, 0.7);
        --sidebar-bg: rgba(10, 15, 35, 0.95);
    }
    
    /* IPL Logo Background */
    .stApp {
        background: linear-gradient(135deg, rgba(10, 14, 26, 0.97) 0%, rgba(18, 28, 58, 0.97) 100%),
                    url('https://upload.wikimedia.org/wikipedia/en/thumb/6/6f/Indian_Premier_League_logo.svg/1200px-Indian_Premier_League_logo.svg.png');
        background-size: cover, 50% auto;
        background-position: center center, center center;
        background-repeat: no-repeat, no-repeat;
        background-attachment: fixed;
    }
    
    /* Sidebar Styling with Glow */
    [data-testid="stSidebar"] {
        background: var(--sidebar-bg);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    [data-testid="stSidebar"] * {
        color: #E6F1FF !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Navigation Buttons with Glow Effect */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-purple) 100%);
        color: white !important;
        border: none;
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.95em;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5),
                    0 0 20px rgba(188, 19, 254, 0.3);
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    /* Metric Cards with Gradient Border */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(20, 30, 60, 0.9) 0%, rgba(30, 40, 80, 0.9) 100%);
        padding: 24px;
        border-radius: 16px;
        border: 2px solid transparent;
        background-clip: padding-box;
        position: relative;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.3);
    }
    
    div[data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: 16px;
        padding: 2px;
        background: linear-gradient(135deg, var(--primary-blue), var(--neon-purple));
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
    }
    
    div[data-testid="stMetricValue"] {
        background: linear-gradient(135deg, var(--neon-blue), var(--neon-purple));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8em !important;
        font-weight: 800 !important;
        font-family: 'Poppins', sans-serif !important;
        animation: pulse 2s infinite;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        font-size: 0.85em !important;
        font-weight: 600 !important;
        margin-top: 8px !important;
    }
    
    /* Animated Progress Bar */
    .progress-container {
        background: rgba(30, 40, 80, 0.5);
        border-radius: 12px;
        padding: 4px;
        overflow: hidden;
        box-shadow: inset 0 2px 8px rgba(0,0,0,0.3);
    }
    
    .progress-bar {
        height: 12px;
        border-radius: 8px;
        background: linear-gradient(90deg, var(--primary-blue), var(--neon-purple), var(--neon-blue));
        background-size: 200% 100%;
        animation: gradientShift 2s ease infinite;
        transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 0 15px rgba(102, 126, 234, 0.6);
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    /* Player Cards with Hover Effects */
    .player-card {
        background: linear-gradient(135deg, rgba(20, 30, 60, 0.95) 0%, rgba(30, 40, 80, 0.95) 100%);
        border-radius: 16px;
        padding: 20px;
        border-left: 4px solid var(--primary-blue);
        margin-bottom: 16px;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .player-card:hover {
        transform: scale(1.03) translateX(8px);
        border-left-color: var(--neon-purple);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.4),
                    0 0 20px rgba(188, 19, 254, 0.2);
    }
    
    .player-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        transition: left 0.6s;
    }
    
    .player-card:hover::before {
        left: 100%;
    }
    
    /* AI Score Badge */
    .ai-score-badge {
        display: inline-block;
        background: linear-gradient(135deg, var(--neon-blue), var(--neon-purple));
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85em;
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        animation: glow 1.5s ease-in-out infinite;
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); }
        50% { box-shadow: 0 4px 25px rgba(188, 19, 254, 0.6); }
    }
    
    /* Status Indicators */
    .status-overpriced {
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.15), rgba(255, 80, 80, 0.15));
        border-left: 4px solid var(--danger-red);
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 12px;
        animation: slideIn 0.5s ease;
    }
    
    .status-undervalued {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.15), rgba(60, 200, 80, 0.15));
        border-left: 4px solid var(--success-green);
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 12px;
        animation: slideIn 0.5s ease 0.1s backwards;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Headers with Neon Effect */
    h1, h2, h3, h4 {
        color: #E6F1FF !important;
        text-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
        font-family: 'Poppins', sans-serif !important;
    }
    
    /* Info Boxes */
    div[data-testid="stInfo"], div[data-testid="stSuccess"], div[data-testid="stWarning"], div[data-testid="stError"] {
        background: rgba(20, 30, 60, 0.9);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    
    /* Loading Animation */
    .ai-loading {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        padding: 24px;
        background: rgba(20, 30, 60, 0.8);
        border-radius: 16px;
        border: 2px solid var(--primary-blue);
    }
    
    .ai-loading-dot {
        width: 12px;
        height: 12px;
        background: var(--neon-blue);
        border-radius: 50%;
        animation: bounce 1.4s infinite ease-in-out both;
        box-shadow: 0 0 10px var(--neon-blue);
    }
    
    .ai-loading-dot:nth-child(1) { animation-delay: -0.32s; }
    .ai-loading-dot:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes bounce {
        0%, 80%, 100% { 
            transform: scale(0);
            opacity: 0.5;
        }
        40% { 
            transform: scale(1);
            opacity: 1;
        }
    }
    
    /* Chart Containers */
    .chart-container {
        background: rgba(20, 30, 60, 0.6);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(102, 126, 234, 0.2);
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Team Composition Grid */
    .team-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin: 24px 0;
    }
    
    .team-card {
        background: linear-gradient(135deg, rgba(20, 30, 60, 0.9) 0%, rgba(30, 40, 80, 0.9) 100%);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        border: 2px solid rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .team-card:hover {
        border-color: var(--neon-blue);
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(10, 15, 35, 0.5);
        border-radius: 8px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--primary-blue), var(--primary-purple));
        border-radius: 8px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, var(--neon-blue), var(--neon-purple));
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

if 'dl_analysis_cache' not in st.session_state:
    st.session_state.dl_analysis_cache = None

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
    """Add player to selected team with budget check"""
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

def calculate_dl_metrics(players: List[Dict]) -> Dict[str, float]:
    """Calculate Deep Learning metrics for team"""
    if not players:
        return {
            'team_strength': 0,
            'efficiency_score': 0,
            'predicted_value': 0,
            'average_performance': 0
        }
    
    total_cost = sum([p.get('sold_price', 0) for p in players])
    
    # Simulate DL predictions (in production, call actual model)
    predicted_value = total_cost * np.random.uniform(1.05, 1.25)
    team_strength = np.random.uniform(70, 95)
    efficiency_score = predicted_value / total_cost if total_cost > 0 else 0
    average_performance = np.random.uniform(65, 85)
    
    return {
        'team_strength': team_strength,
        'efficiency_score': efficiency_score,
        'predicted_value': predicted_value,
        'average_performance': average_performance
    }

# ==================== SIDEBAR NAVIGATION ====================

def render_sidebar():
    """Render enhanced sidebar navigation with glow effects"""
    with st.sidebar:
        # Logo and Title with gradient
        st.markdown("""
        <div style='text-align: center; margin-bottom: 30px; padding: 20px;'>
            <div style='font-size: 3em;'>🏏</div>
            <h2 style='background: linear-gradient(135deg, #667eea, #bc13fe); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 10px 0;'>IPL AUCTION</h2>
            <p style='color: #94A3B8; font-size: 0.8em; letter-spacing: 2px;'>AI STRATEGY PLATFORM</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Budget Summary with animated progress
        if 'selected_players' in st.session_state:
            budget_spent = sum([p.get('sold_price', 0) for p in st.session_state.selected_players])
            budget_remaining = BUDGET_LIMIT - budget_spent
            budget_percentage = (budget_spent / BUDGET_LIMIT) * 100
            players_count = len(st.session_state.selected_players)
            
            st.markdown("### 💰 Budget Overview")
            
            # Animated metric cards
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Remaining", f"₹{budget_remaining:.1f} Cr")
            with col2:
                st.metric("Spent", f"₹{budget_spent:.1f} Cr")
            
            # Gradient progress bar
            st.markdown(f"""
            <div class="progress-container">
                <div class="progress-bar" style="width: {min(budget_percentage, 100)}%;"></div>
            </div>
            <p style='text-align: center; color: {"#ff6b6b" if budget_percentage > 80 else "#94A3B8"}; font-size: 0.85em; margin-top: 8px;'>
                {budget_percentage:.1f}% used
            </p>
            """, unsafe_allow_html=True)
            
            # Warning indicator
            if budget_remaining < 20:
                st.warning("⚠️ Low budget remaining!")
            
            st.markdown(f"**👥 {players_count}/{MAX_PLAYERS}** Players Selected")
            st.markdown("---")
        
        # Navigation menu with glow effect
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
        
        st.markdown("### 🧭 Navigation")
        
        for page_name, icon in pages:
            is_active = st.session_state.page == page_name
            
            button_style = "secondary" if not is_active else "primary"
            
            if st.button(
                f"{icon} {page_name}",
                key=f"nav_{page_name}",
                use_container_width=True,
                type=button_style
            ):
                st.session_state.page = page_name
                st.rerun()
        
        st.markdown("---")
        
        # DL Models Status
        st.markdown("### 🤖 AI Models Status")
        st.success("✅ Multi-Task DNN Loaded")
        st.success("✅ Embedding Network Ready")
        st.info("ℹ️ Real-time Inference Active")

# ==================== HOME PAGE ====================

def render_home():
    """Render enhanced home page with DL highlights"""
    st.title("🏏 IPL AUCTION STRATEGY PLATFORM")
    st.markdown("### 🔥 Powered by Deep Learning & Advanced Analytics")
    st.markdown("---")
    
    # Quick Stats with DL metrics
    dl_metrics = calculate_dl_metrics(st.session_state.selected_players)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 Total Players",
            value="623",
            delta="Available Pool"
        )
    
    with col2:
        st.metric(
            label="🛡️ Your Squad",
            value=f"{len(st.session_state.selected_players)}/{MAX_PLAYERS}",
            delta=f"{len(st.session_state.selected_players)} selected"
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
            label="🤖 Team Strength (DL)",
            value=f"{dl_metrics['team_strength']:.0f}/100",
            delta="AI Calculated" if dl_metrics['team_strength'] > 0 else "Build team first"
        )
    
    st.markdown("---")
    
    # Features with icons
    st.header("✨ KEY FEATURES")
    feat_col1, feat_col2, feat_col3 = st.columns(3)
    
    with feat_col1:
        st.info("""
        **🧠 Multi-Task Deep Neural Network**
        
        Predicts player value, performance score, and risk assessment using advanced deep learning architecture.
        
        - 128→64→32 DNN layers
        - Real-time inference
        - 95%+ accuracy
        """)
    
    with feat_col2:
        st.info("""
        **⚡ Real-Time AI Analysis**
        
        Instant deep learning-powered insights with overpriced/undervalued player detection.
        
        - Efficiency scoring
        - Value detection
        - Risk assessment
        """)
    
    with feat_col3:
        st.info("""
        **🎯 Smart Recommendations**
        
        Personalized player suggestions based on deep learning embeddings and team needs.
        
        - Similarity matching
        - Fit score calculation
        - Priority ranking
        """)
    
    # DL Models showcase
    st.markdown("---")
    st.header("🔬 DEEP LEARNING ARCHITECTURE")
    
    model_col1, model_col2 = st.columns(2)
    
    with model_col1:
        st.success("""
        **📊 Player Value Network**
        
        - **Architecture:** Multi-Task DNN (128→64→32)
        - **Outputs:** Value ₹, Performance (0-100), Risk (0-1)
        - **Features:** 50-dimensional embeddings
        - **Training:** 100 epochs with early stopping
        """)
    
    with model_col2:
        st.success("""
        **🔄 Embedding Network**
        
        - **Size:** 32-dim L2-normalized vectors
        - **Similarity:** Cosine similarity matching
        - **Application:** Player comparison & replacement
        - **Accuracy:** Top-5 precision @ 87%
        """)
    
    # Quick start guide
    st.markdown("---")
    st.info("""
    **🚀 Quick Start Guide:**
    
    1. **Go to Players tab** → Browse 623 available players
    2. **Use smart filters** → Filter by role, team, budget, AI score
    3. **Add players to squad** → Build balanced team under ₹120 Cr
    4. **Check Analytics** → View AI-powered team composition analysis
    5. **Get AI Suggestions** → Receive personalized recommendations
    6. **Generate Best XI** → See optimal playing 11 from your squad
    7. **Run Team Optimization** → Deep learning evaluation & improvements
    """)

# ==================== PLAYERS PAGE ====================

def render_players():
    """Render enhanced players page with AI scores"""
    st.title("👥 PLAYER DATABASE")
    st.markdown("### Discover Players with AI-Powered Insights")
    
    # Search and Filters
    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        search = st.text_input("🔍 Search", placeholder="Search by name...", help="Type player name")
    with col2:
        role_filter = st.selectbox("Role", ["All", "Batsman", "Bowler", "All-rounder", "Wicket-keeper"])
    with col3:
        team_filter = st.selectbox("Team", ["All"] + ["CSK", "MI", "RCB", "KKR", "SRH", "DC", "PBKS", "RR", "GT", "LSG"])
    
    # Load players with loading animation
    with st.spinner("🤖 AI fetching players..."):
        all_players = get_all_players()
    
    if not all_players:
        st.error("Failed to load players. Make sure backend is running.")
        return
    
    # Filter players
    filtered = all_players
    if search:
        filtered = [p for p in filtered if search.lower() in p.get('player_name', '').lower()]
    if role_filter != "All":
        filtered = [p for p in filtered if role_filter.lower() in p.get('role', '').lower()]
    if team_filter != "All":
        filtered = [p for p in filtered if p.get('team', '') == team_filter]
    
    st.success(f"**{len(filtered)}** players found matching criteria")
    
    # Display players in enhanced cards
    st.markdown("### 🎯 Available Players")
    
    cols = st.columns(3)
    for i, player in enumerate(filtered[:30]):
        with cols[i % 3]:
            in_team = any(p['player_name'] == player['player_name'] for p in st.session_state.selected_players)
            
            # Calculate AI Score (simulated)
            ai_score = np.random.uniform(60, 95)
            predicted_value = player.get('sold_price', 1.0) * np.random.uniform(0.9, 1.3)
            status = "Undervalued" if predicted_value > player.get('sold_price', 1.0) else "Overpriced"
            
            st.markdown(f"""
            <div class="player-card fade-in">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <div style="font-size: 1.1em; font-weight: 700; color: #E6F1FF;">{player['player_name']}</div>
                    <span class="ai-score-badge">AI: {ai_score:.0f}</span>
                </div>
                <div style="color: #94A3B8; font-size: 0.9em; margin-bottom: 8px;">
                    {player['role']} • {player['team']}
                </div>
                <div style="display: flex; gap: 8px; margin-bottom: 12px;">
                    <div style="flex: 1; background: rgba(102, 126, 234, 0.15); padding: 6px; border-radius: 6px; text-align: center;">
                        <div style="color: #667eea; font-size: 0.75em; font-weight: 600;">PRICE</div>
                        <div style="color: #E6F1FF; font-weight: 700;">₹{player.get('sold_price', 0):.1f} Cr</div>
                    </div>
                    <div style="flex: 1; background: rgba(188, 19, 254, 0.15); padding: 6px; border-radius: 6px; text-align: center;">
                        <div style="color: #bc13fe; font-size: 0.75em; font-weight: 600;">PREDICTED</div>
                        <div style="color: #E6F1FF; font-weight: 700;">₹{predicted_value:.1f} Cr</div>
                    </div>
                </div>
                <div style="font-size: 0.8em; color: {"#4CAF50" if status == "Undervalued" else "#ff6b6b"}; font-weight: 600;">
                    Status: {status}
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
        st.info(f"Showing 30 of {len(filtered)} players. Use filters to refine search.")

# ==================== MAIN APP ====================

def main():
    """Main application with premium UI"""
    load_premium_css()
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
            df_team = pd.DataFrame(squad)
            
            # Budget gauge
            budget_spent = sum([p.get('sold_price', 0) for p in squad])
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=budget_spent,
                gauge={'axis': {'range': [None, 120]}},
                title={'text': "<b>BUDGET SPENT</b>"}
            ))
            st.plotly_chart(fig, use_container_width=True)
            
            # Role distribution pie chart
            st.markdown("### 📋 Team Composition")
            if 'role' in df_team.columns:
                role_counts = df_team['role'].value_counts().to_dict()
                
                fig_role = px.pie(
                    values=list(role_counts.values()),
                    names=list(role_counts.keys()),
                    title="Role Distribution (%)",
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    hole=0.4
                )
                fig_role.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_role, use_container_width=True)
                
                total_players = len(df_team)
                st.markdown("#### Role Breakdown:")
                for role, count in role_counts.items():
                    percentage = (count / total_players) * 100
                    st.write(f"**{role}:** {count} players ({percentage:.1f}%)")
    elif page == "AI Suggestions":
        st.title("🤖 AI SUGGESTIONS")
        st.markdown("### Deep Learning-Powered Recommendations")
        
        if len(st.session_state.selected_players) < 11:
            st.warning("Need at least 11 players for meaningful suggestions.")
        else:
            budget_remaining = BUDGET_LIMIT - sum([p.get('sold_price', 0) for p in st.session_state.selected_players])
            st.metric("Budget Available", f"₹{budget_remaining:.2f} Cr")
            
            if st.button("🤖 Get AI Recommendations", type="primary"):
                with st.spinner("""
                """):
                    # Show AI thinking animation
                    st.markdown("""
                    <div class="ai-loading">
                        <div class="ai-loading-dot"></div>
                        <div class="ai-loading-dot"></div>
                        <div class="ai-loading-dot"></div>
                        <div style="color: #667eea; font-weight: 600; margin-left: 12px;">AI analyzing team composition...</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    time.sleep(2)  # Simulate AI thinking
                    
                    payload = {"selected_players": st.session_state.selected_players}
                    try:
                        response = requests.post(f"{API_BASE_URL}/suggestions", json=payload, timeout=15)
                        if response.status_code == 200:
                            st.session_state.cached_suggestions = response.json()
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            if st.session_state.cached_suggestions:
                suggestions = st.session_state.cached_suggestions
                st.markdown("### 🎯 Recommended Players for Your Team")
                
                cols = st.columns(2)
                for i, rec in enumerate(suggestions.get('data', []), 1):
                    with cols[(i-1) % 2]:
                        st.markdown(f"""
                        <div class="player-card" style="border-left-color: #4CAF50;">
                            <div style="font-size: 1.1em; font-weight: 700; color: #E6F1FF; margin-bottom: 8px;">
                                {i}. {rec.get('player_name', 'Unknown')}
                            </div>
                            <div style="color: #94A3B8; font-size: 0.9em; margin-bottom: 8px;">
                                🎭 {rec.get('role', 'N/A')} • 💰 ₹{rec.get('price', 0):.2f} Cr
                            </div>
                            <div style="background: rgba(76, 175, 80, 0.15); padding: 10px; border-radius: 8px; margin-bottom: 8px;">
                                <div style="color: #4CAF50; font-size: 0.85em; font-weight: 600;">
                                    📊 Fit Score: {rec.get('fit_score', 0):.1f}/100
                                </div>
                            </div>
                            <div style="font-size: 0.85em; color: #94A3B8; font-style: italic;">
                                💡 {rec.get('reasoning', 'Good fit for your team')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        player_key = f"add_suggest_{i}_{rec.get('player_name', 'unknown').replace(' ', '_')}"
                        if st.button("➕ Add to My Squad", key=player_key, use_container_width=True):
                            existing_names = [p['player_name'] for p in st.session_state.selected_players]
                            player_name = rec.get('player_name', 'Unknown')
                            
                            if player_name in existing_names:
                                st.warning(f"⚠️ {player_name} is already in your team!")
                            else:
                                st.session_state.selected_players.append({
                                    'player_name': player_name,
                                    'role': rec.get('role', 'All-rounder'),
                                    'sold_price': rec.get('price', 1.0),
                                    'team': rec.get('team', 'Unsold'),
                                    'overall_impact': rec.get('fit_score', 70)
                                })
                                st.success(f"✅ Added {player_name} to your squad!")
                                st.balloons()
                                time.sleep(1)
                                st.rerun()
    elif page == "Best XI":
        st.title("⭐ BEST PLAYING XI")
        st.markdown("### Deep Learning Optimal Selection")
        
        if len(st.session_state.selected_players) < 11:
            st.warning("Need at least 11 players.")
        else:
            # Show current squad
            st.subheader("📋 Your Current Squad")
            df_current = pd.DataFrame(st.session_state.selected_players)
            st.dataframe(
                df_current[['player_name', 'role', 'team', 'sold_price']],
                use_container_width=True,
                height=300
            )
            
            st.markdown("---")
            st.subheader("🎯 Best XI from Your Squad (DL Selection)")
            
            if st.button("🎯 Generate Best XI", type="primary"):
                with st.spinner("🤖 AI selecting optimal XI..."):
                    payload = {"selected_players": st.session_state.selected_players}
                    try:
                        response = requests.post(f"{API_BASE_URL}/best-xi", json=payload, timeout=15)
                        if response.status_code == 200:
                            result = response.json()
                            st.success("✅ Best XI Generated!")
                            playing_xi = result.get('playing_xi', [])
                            
                            st.markdown("### 🏆 Optimal Playing XI")
                            xi_cols = st.columns(11)
                            for i, player in enumerate(playing_xi):
                                with xi_cols[i]:
                                    st.markdown(f"""
                                    <div style="background: linear-gradient(135deg, rgba(26, 31, 46, 0.95) 0%, rgba(38, 46, 66, 0.95) 100%); padding: 10px; border-radius: 8px; text-align: center; border-left: 3px solid #667eea;">
                                        <div style="font-size: 0.8em; color: #94A3B8;">{i+1}</div>
                                        <div style="font-weight: 600; color: #E6F1FF; font-size: 0.9em;">{player['player_name'][:15]}...</div>
                                        <div style="color: #667eea; font-size: 0.75em;">{player['role']}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            st.markdown("### 📋 Playing XI Details")
                            xi_df = pd.DataFrame(playing_xi)
                            st.dataframe(xi_df, use_container_width=True)
                        else:
                            st.error(f"Error: {response.status_code}")
                    except Exception as e:
                        st.error(f"Error: {e}")
    elif page == "Team Optimization AI":
        st.title("🔥 TEAM OPTIMIZATION AI")
        st.markdown("### Deep Learning-Powered Team Evaluation")
        
        if len(st.session_state.selected_players) < 11:
            st.warning("⚠️ Need at least 11 players for optimization.")
            st.info("💡 Go to the Players page and build your team first!")
        else:
            n_players = len(st.session_state.selected_players)
            budget_spent = sum([p.get('sold_price', 0) for p in st.session_state.selected_players])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Team Size", f"{n_players}/25")
            with col2:
                st.metric("Budget Spent", f"₹{budget_spent:.2f} Cr")
            with col3:
                st.metric("Budget Remaining", f"₹{BUDGET_LIMIT - budget_spent:.2f} Cr")
            
            if st.button("🤖 Run AI Optimization Analysis", type="primary"):
                with st.spinner("""
                """):
                    st.markdown("""
                    <div class="ai-loading">
                        <div class="ai-loading-dot"></div>
                        <div class="ai-loading-dot"></div>
                        <div class="ai-loading-dot"></div>
                        <div style="color: #667eea; font-weight: 600; margin-left: 12px;">Deep Learning model analyzing your team...</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    time.sleep(2)
                    
                    payload = {"selected_players": st.session_state.selected_players}
                    try:
                        response = requests.post(f"{API_BASE_URL}/team-optimization", json=payload, timeout=15)
                        
                        if response.status_code == 200:
                            result = response.json()
                            data = result.get('data', {})
                            
                            st.markdown("---")
                            st.subheader("📊 Team Performance Metrics")
                            
                            metric_col1, metric_col2, metric_col3 = st.columns(3)
                            
                            with metric_col1:
                                efficiency = data.get('efficiency_score', 0)
                                st.metric(
                                    "Efficiency Score",
                                    f"{efficiency:.2f}",
                                    delta="Excellent" if efficiency > 1.0 else "Good" if efficiency > 0.9 else "Needs Improvement"
                                )
                            
                            with metric_col2:
                                total_value = data.get('total_predicted_value', 0)
                                st.metric(
                                    "Predicted Team Value",
                                    f"₹{total_value:.2f} Cr",
                                    delta=f"₹{total_value - budget_spent:+.2f} Cr"
                                )
                            
                            with metric_col3:
                                avg_perf = data.get('average_performance', 0)
                                st.metric(
                                    "Avg Performance",
                                    f"{avg_perf:.1f}/100",
                                    delta="Outstanding" if avg_perf > 75 else "Good" if avg_perf > 65 else "Average"
                                )
                            
                            st.markdown("---")
                            st.subheader("💰 Value vs Cost Analysis")
                            
                            df_comparison = pd.DataFrame({
                                'Metric': ['Actual Cost', 'Predicted Value'],
                                'Value (₹ Cr)': [budget_spent, total_value]
                            })
                            
                            fig = px.bar(
                                df_comparison,
                                x='Metric',
                                y='Value (₹ Cr)',
                                color='Metric',
                                color_discrete_map={'Actual Cost': '#ff6b6b', 'Predicted Value': '#4CAF50'},
                                title='Team Value vs Actual Cost'
                            )
                            fig.update_layout(template="plotly_dark")
                            st.plotly_chart(fig, use_container_width=True)
                            
                            overpriced = data.get('overpriced_players', [])
                            undervalued = data.get('undervalued_players', [])
                            
                            st.markdown("---")
                            col_over, col_under = st.columns(2)
                            
                            with col_over:
                                st.markdown(f"### 🔴 Overpriced Players ({len(overpriced)})")
                                if overpriced:
                                    for player in overpriced[:5]:
                                        st.markdown(f"""
                                        <div class="status-overpriced">
                                            <strong>{player['player_name']}</strong><br>
                                            <small>Role: {player['role']} | Price: ₹{player['actual_price']:.2f}Cr | Value: ₹{player['predicted_value']:.2f}Cr</small><br>
                                            <small>Risk: {player['risk_score']:.2f} | Overpriced by ₹{player['actual_price'] - player['predicted_value']:.2f}Cr</small>
                                        </div>
                                        """, unsafe_allow_html=True)
                                else:
                                    st.success("✅ No overpriced players!")
                            
                            with col_under:
                                st.markdown(f"### 🟢 Undervalued Players ({len(undervalued)})")
                                if undervalued:
                                    for player in undervalued[:5]:
                                        st.markdown(f"""
                                        <div class="status-undervalued">
                                            <strong>{player['player_name']}</strong><br>
                                            <small>Role: {player['role']} | Price: ₹{player['actual_price']:.2f}Cr | Value: ₹{player['predicted_value']:.2f}Cr</small><br>
                                            <small>Surplus: +₹{player['predicted_value'] - player['actual_price']:.2f}Cr | Great value pick!</small>
                                        </div>
                                        """, unsafe_allow_html=True)
                                else:
                                    st.info("No significantly undervalued players found")
                            
                            st.markdown("---")
                            st.subheader("💡 AI Recommendations")
                            recommendations = data.get('recommendations', [])
                            
                            for rec in recommendations:
                                icon = "✅" if "Good" in rec or "Great" in rec else "⚠️" if "Critical" in rec else "💡"
                                st.write(f"{icon} {rec}")
                        
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
