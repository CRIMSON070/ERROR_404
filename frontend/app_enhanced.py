"""
IPL Auction Strategy Platform - Enhanced Modern UI
Deep Learning Powered Professional Dashboard
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

# Import custom UI components
from ui_components import (
    set_page_config,
    load_custom_css,
    render_sidebar,
    metric_card,
    player_card,
    create_budget_chart,
    create_team_composition_chart,
    create_value_distribution_chart,
    ai_loading_animation,
    alert_box
)

# ==================== CONFIGURATION ====================

API_BASE_URL = "http://localhost:8000"
BUDGET_LIMIT = 120.0  # Crore
MAX_PLAYERS = 25

# Initialize page config and CSS
set_page_config()
load_custom_css()

# ==================== SESSION STATE INITIALIZATION ====================

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

# ==================== PAGE RENDERERS ====================

def render_home():
    """Render Home Page with overview"""
    
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="fade-in">
        <h1 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-size: 3em; margin-bottom: 10px;">
            🏏 IPL AUCTION STRATEGY PLATFORM
        </h1>
        <p style="color: #94A3B8; font-size: 1.2em;">
            🔥 Deep Learning Powered Team Optimization
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(metric_card(
            title="Total Players",
            value="623",
            icon="👥"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(metric_card(
            title="Your Squad",
            value=f"{len(st.session_state.selected_players)}/{MAX_PLAYERS}",
            icon="🛡️"
        ), unsafe_allow_html=True)
    
    with col3:
        budget_spent = sum([p.get('sold_price', 0) for p in st.session_state.selected_players])
        st.markdown(metric_card(
            title="Budget Used",
            value=f"₹{budget_spent:.1f} Cr",
            delta=f"{(budget_spent/120)*100:.1f}%",
            icon="💰"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(metric_card(
            title="AI Models",
            value="4 Active",
            icon="🤖"
        ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Features Grid
    st.markdown('<h2 class="section-header">✨ KEY FEATURES</h2>', unsafe_allow_html=True)
    
    feat_col1, feat_col2, feat_col3 = st.columns(3)
    
    with feat_col1:
        st.markdown("""
        <div class="metric-card fade-in" style="height: 100%;">
            <div style="font-size: 3em; margin-bottom: 10px;">🧠</div>
            <h3 style="color: #667eea; margin-bottom: 10px;">Multi-Task DNN</h3>
            <p style="color: #94A3B8; line-height: 1.6;">
                Predicts Player Value, Performance Score, and Risk Score using advanced deep learning architecture.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat_col2:
        st.markdown("""
        <div class="metric-card fade-in" style="height: 100%;">
            <div style="font-size: 3em; margin-bottom: 10px;">⚡</div>
            <h3 style="color: #764ba2; margin-bottom: 10px;">Real-time Analysis</h3>
            <p style="color: #94A3B8; line-height: 1.6;">
                Instant AI-powered insights on every player with overpriced/undervalued detection.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat_col3:
        st.markdown("""
        <div class="metric-card fade-in" style="height: 100%;">
            <div style="font-size: 3em; margin-bottom: 10px;">🎯</div>
            <h3 style="color: #4CAF50; margin-bottom: 10px;">Smart Recommendations</h3>
            <p style="color: #94A3B8; line-height: 1.6;">
                Get personalized player suggestions and replacement opportunities based on embeddings.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # DL Models Info
    st.markdown("---")
    st.markdown('<h2 class="section-header">🔬 DEEP LEARNING MODELS</h2>', unsafe_allow_html=True)
    
    model_col1, model_col2 = st.columns(2)
    
    with model_col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #667eea; margin-bottom: 15px;">📊 Player Value Network</h3>
            <ul style="color: #94A3B8; line-height: 2;">
                <li><strong>Architecture:</strong> Multi-Task DNN (128→64→32)</li>
                <li><strong>Outputs:</strong> Value ₹, Performance (0-100), Risk (0-1)</li>
                <li><strong>Features:</strong> 50-dimensional player embeddings</li>
                <li><strong>Loss:</strong> Combined MSE + BCE weighted loss</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with model_col2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #764ba2; margin-bottom: 15px;">🔄 Embedding Network</h3>
            <ul style="color: #94A3B8; line-height: 2;">
                <li><strong>Embedding Size:</strong> 32-dim L2-normalized</li>
                <li><strong>Similarity:</strong> Cosine similarity for replacements</li>
                <li><strong>Application:</strong> Player matching & recommendations</li>
                <li><strong>Training:</strong> Early stopping with patience=15</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_players():
    """Render Players Page with modern cards"""
    
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    st.markdown('<h1 class="section-header">👥 PLAYER DATABASE</h1>', unsafe_allow_html=True)
    
    # Search and Filters
    col1, col2, col3 = st.columns([3, 2, 2])
    
    with col1:
        search_query = st.text_input("🔍 Search Players", placeholder="Search by name...")
    
    with col2:
        role_filter = st.selectbox(
            "Filter by Role",
            ["All", "Batsman", "Bowler", "All-rounder", "Wicket-keeper"]
        )
    
    with col3:
        team_filter = st.selectbox(
            "Filter by Team",
            ["All"] + ["CSK", "MI", "RCB", "KKR", "SRH", "DC", "PBKS", "RR", "GT", "LSG"]
        )
    
    # Fetch players
    with st.spinner("Loading players..."):
        all_players = get_all_players()
    
    if not all_players:
        alert_box("Failed to load players. Make sure backend is running.", "error")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Apply filters
    filtered = all_players
    
    if search_query:
        filtered = [p for p in filtered if search_query.lower() in p.get('player_name', '').lower()]
    
    if role_filter != "All":
        filtered = [p for p in filtered if role_filter.lower() in p.get('role', '').lower()]
    
    if team_filter != "All":
        filtered = [p for p in filtered if p.get('team', '') == team_filter]
    
    st.success(f"**{len(filtered)}** players found")
    
    # Display players in grid
    cols = st.columns(3)
    
    for i, player in enumerate(filtered[:30]):  # Limit to 30 for performance
        with cols[i % 3]:
            # Check if already in team
            in_team = any(p['player_name'] == player['player_name'] 
                         for p in st.session_state.selected_players)
            
            card_html = player_card(
                player,
                show_dl_insights=False,
                can_add=not in_team
            )
            
            st.markdown(card_html, unsafe_allow_html=True)
            
            # Add button logic
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
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_team_builder():
    """Render Team Builder with DL insights"""
    
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    st.markdown('<h1 class="section-header">🛠️ TEAM BUILDER</h1>', unsafe_allow_html=True)
    
    squad = st.session_state.selected_players
    
    if not squad:
        alert_box("Your squad is empty! Go to Players tab to add players.", "warning")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Summary Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        budget_spent = sum([p.get('sold_price', 0) for p in squad])
        st.markdown(metric_card(
            title="Budget Spent",
            value=f"₹{budget_spent:.1f} Cr",
            delta=f"₹{120-budget_spent:.1f} Cr left",
            icon="💰"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(metric_card(
            title="Players Selected",
            value=f"{len(squad)}/{MAX_PLAYERS}",
            icon="👥"
        ), unsafe_allow_html=True)
    
    with col3:
        avg_price = budget_spent / len(squad) if squad else 0
        st.markdown(metric_card(
            title="Avg Player Price",
            value=f"₹{avg_price:.1f} Cr",
            icon="📊"
        ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Role-wise breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 style="color: #667eea;">Role Distribution</h3>', unsafe_allow_html=True)
        
        role_counts = {}
        for player in squad:
            role = player.get('role', 'Unknown')
            if 'Wicket-keeper' in role:
                role_cat = 'WK'
            elif 'Batsman' in role:
                role_cat = 'BAT'
            elif 'All-rounder' in role:
                role_cat = 'AR'
            elif 'Bowler' in role:
                role_cat = 'BOWL'
            else:
                role_cat = 'OTH'
            
            role_counts[role_cat] = role_counts.get(role_cat, 0) + 1
        
        for role, count in role_counts.items():
            emoji = {"WK": "🧤", "BAT": "🏏", "AR": "🔄", "BOWL": "⚾", "OTH": "📋"}.get(role, "📋")
            st.write(f"{emoji} **{role}:** {count} players")
    
    with col2:
        st.markdown('<h3 style="color: #764ba2;">Price Distribution</h3>', unsafe_allow_html=True)
        
        price_ranges = {
            "₹0-5 Cr": 0,
            "₹5-10 Cr": 0,
            "₹10-15 Cr": 0,
            "₹15+ Cr": 0
        }
        
        for player in squad:
            price = player.get('sold_price', 0)
            if price < 5:
                price_ranges["₹0-5 Cr"] += 1
            elif price < 10:
                price_ranges["₹5-10 Cr"] += 1
            elif price < 15:
                price_ranges["₹10-15 Cr"] += 1
            else:
                price_ranges["₹15+ Cr"] += 1
        
        for range_name, count in price_ranges.items():
            st.write(f"**{range_name}:** {count} players")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig = create_team_composition_chart(squad)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = create_value_distribution_chart(squad)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Squad List
    st.markdown('<h3 style="color: #4CAF50;">📋 YOUR SQUAD</h3>', unsafe_allow_html=True)
    
    for i, player in enumerate(squad):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            card_html = player_card(player, show_dl_insights=False, can_add=False)
            st.markdown(card_html, unsafe_allow_html=True)
        
        with col2:
            if st.button("❌ Remove", key=f"remove_{i}", use_container_width=True):
                st.session_state.selected_players.pop(i)
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_analytics():
    """Render Analytics Dashboard"""
    
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    st.markdown('<h1 class="section-header">📊 ANALYTICS DASHBOARD</h1>', unsafe_allow_html=True)
    
    squad = st.session_state.selected_players
    
    if not squad:
        alert_box("No players selected. Build your team first!", "warning")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Budget Gauge
    budget_spent = sum([p.get('sold_price', 0) for p in squad])
    fig = create_budget_chart(budget_spent)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Advanced Analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 style="color: #667eea;">Team Composition Analysis</h3>', unsafe_allow_html=True)
        fig = create_team_composition_chart(squad)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<h3 style="color: #764ba2;">Value Distribution</h3>', unsafe_allow_html=True)
        fig = create_value_distribution_chart(squad)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_ai_suggestions():
    """Render AI Suggestions with DL insights"""
    
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    st.markdown('<h1 class="section-header">🤖 AI SUGGESTIONS</h1>', unsafe_allow_html=True)
    
    if len(st.session_state.selected_players) < 11:
        alert_box(f"You need at least 11 players. Currently have {len(st.session_state.selected_players)}.", "warning")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    if st.button("🤖 Get AI Recommendations", type="primary"):
        with st.spinner("Analyzing your team..."):
            try:
                payload = {"selected_players": st.session_state.selected_players}
                response = requests.post(f"{API_BASE_URL}/suggestions", json=payload, timeout=15)
                
                if response.status_code == 200:
                    st.session_state.cached_suggestions = response.json()
                    st.rerun()
                else:
                    st.error(f"API Error: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {e}")
    
    if st.session_state.cached_suggestions:
        data = st.session_state.cached_suggestions.get('data', {})
        suggestions = data.get('recommendations', [])
        
        if suggestions:
            st.markdown('<h3 style="color: #4CAF50;">🎯 Recommended Players for Your Team</h3>', unsafe_allow_html=True)
            
            cols = st.columns(2)
            
            for i, rec in enumerate(suggestions, 1):
                with cols[(i-1) % 2]:
                    player_name = rec.get('player_name', 'Unknown')
                    reason = rec.get('reason', 'Good value pick')
                    
                    # Find full player data
                    all_players = get_all_players()
                    player_data = next((p for p in all_players if p['player_name'] == player_name), None)
                    
                    if player_data:
                        card_html = player_card(player_data, show_dl_insights=True, can_add=True)
                        st.markdown(card_html, unsafe_allow_html=True)
                        
                        player_key = f"add_suggest_{i}_{player_name.replace(' ', '_')}"
                        if st.button("➕ Add to My Squad", key=player_key, use_container_width=True):
                            success, msg = add_player_to_team(player_data)
                            if success:
                                st.success(f"✅ Added {player_name}!")
                                st.balloons()
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(msg)
        else:
            st.info("No AI suggestions available at the moment.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_best_xi():
    """Render Best XI Generator"""
    
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    st.markdown('<h1 class="section-header">⭐ BEST PLAYING XI</h1>', unsafe_allow_html=True)
    
    squad = st.session_state.selected_players
    
    if not squad or len(squad) < 11:
        alert_box(f"You need at least 11 players. Currently have {len(squad) if squad else 0}.", "warning")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    if st.button("🎯 Generate Best XI", type="primary"):
        with st.spinner("AI is generating optimal lineup..."):
            try:
                payload = {"selected_players": squad}
                response = requests.post(f"{API_BASE_URL}/best-xi", json=payload, timeout=15)
                
                if response.status_code == 200:
                    result = response.json()
                    playing_xi = result.get('playing_xi', [])
                    bench = result.get('bench', [])
                    
                    st.success("**Best Playing XI Generated!**")
                    
                    # Visual Formation
                    fig = go.Figure()
                    
                    # Goalkeeper
                    wk_players = [p for p in playing_xi if 'Wicket-keeper' in p.get('role', '')]
                    if wk_players:
                        fig.add_trace(go.Scatter(x=[50], y=[5], mode='markers+text',
                                               marker=dict(size=25, color='#FFD700'),
                                               text=[f"🧤 {wk_players[0]['player_name']}"],
                                               name='WK'))
                    
                    # Batsmen
                    bat_players = [p for p in playing_xi if 'Batsman' in p.get('role', '')][:4]
                    for i, player in enumerate(bat_players):
                        fig.add_trace(go.Scatter(x=[20 + i*25], y=[25], mode='markers+text',
                                               marker=dict(size=20, color='#667eea'),
                                               text=[f"🏏 {player['player_name']}"],
                                               name=f'BAT {i+1}'))
                    
                    # All-rounders
                    ar_players = [p for p in playing_xi if 'All-rounder' in p.get('role', '')][:3]
                    for i, player in enumerate(ar_players):
                        fig.add_trace(go.Scatter(x=[30 + i*30], y=[50], mode='markers+text',
                                               marker=dict(size=20, color='#4CAF50'),
                                               text=[f"🔄 {player['player_name']}"],
                                               name=f'AR {i+1}'))
                    
                    # Bowlers
                    bowl_players = [p for p in playing_xi if 'Bowler' in p.get('role', '')][:4]
                    for i, player in enumerate(bowl_players):
                        fig.add_trace(go.Scatter(x=[15 + i*25], y=[75], mode='markers+text',
                                               marker=dict(size=20, color='#ff6b6b'),
                                               text=[f"⚾ {player['player_name']}"],
                                               name=f'BOWL {i+1}'))
                    
                    fig.update_layout(
                        title='<b>PLAYING XI FORMATION</b>',
                        xaxis=dict(range=[0, 100], showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(range=[0, 100], showgrid=False, zeroline=False, showticklabels=False),
                        plot_bgcolor='rgba(26, 31, 46, 0.9)',
                        paper_bgcolor='rgba(26, 31, 46, 0.9)',
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # List view
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown('<h3 style="color: #4CAF50;">Playing XI</h3>', unsafe_allow_html=True)
                        for i, player in enumerate(playing_xi, 1):
                            st.markdown(f"**{i}. {player['player_name']}** ({player['role']}) - ₹{player.get('sold_price', 0):.2f} Cr")
                    
                    with col2:
                        st.markdown('<h3 style="color: #FFC107;">Bench</h3>', unsafe_allow_html=True)
                        for i, player in enumerate(bench, 1):
                            st.markdown(f"**{i}. {player['player_name']}** ({player['role']}) - ₹{player.get('sold_price', 0):.2f} Cr")
                
                else:
                    st.error(f"API Error: {response.status_code}")
            
            except Exception as e:
                st.error(f"Error: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_team_optimization():
    """Render Team Optimization AI with DL insights"""
    
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    st.markdown('<h1 class="section-header">🔥 TEAM OPTIMIZATION AI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #94A3B8; font-size: 1.1em;">Deep Learning-Powered Team Evaluation & Optimization</p>', unsafe_allow_html=True)
    
    squad = st.session_state.selected_players
    
    if not squad or len(squad) < 11:
        alert_box(f"⚠️ You need at least 11 players for optimization. Currently have {len(squad) if squad else 0}.", "warning")
        st.info("💡 Go to the **Players** tab and build your team first!")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Summary Metrics
    budget_spent = sum([p.get('sold_price', 0) for p in squad])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(metric_card(
            title="Team Size",
            value=f"{len(squad)}/{MAX_PLAYERS}",
            icon="👥"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(metric_card(
            title="Budget Spent",
            value=f"₹{budget_spent:.1f} Cr",
            delta=f"₹{120-budget_spent:.1f} Cr left",
            icon="💰"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(metric_card(
            title="Avg Investment",
            value=f"₹{budget_spent/len(squad):.1f} Cr",
            icon="📊"
        ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.button("🤖 Run AI Optimization Analysis", type="primary"):
        with st.spinner(""):
            ai_loading_animation("🧠 AI is analyzing your team composition...")
            
            try:
                payload = {"selected_players": squad}
                response = requests.post(f"{API_BASE_URL}/team-optimization", json=payload, timeout=15)
                
                if response.status_code == 200:
                    result = response.json()
                    data = result.get('data', {})
                    
                    # Key metrics
                    st.markdown("---")
                    st.markdown('<h2 class="section-header">📊 TEAM PERFORMANCE METRICS</h2>', unsafe_allow_html=True)
                    
                    metric_col1, metric_col2, metric_col3 = st.columns(3)
                    
                    with metric_col1:
                        efficiency = data.get('efficiency_score', 0)
                        st.metric(
                            "Efficiency Score",
                            f"{efficiency:.2f}",
                            delta="Good" if efficiency > 0.9 else "Needs Improvement"
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
                            delta="Excellent" if avg_perf > 70 else "Average"
                        )
                    
                    # Visualizations
                    st.markdown("---")
                    st.markdown('<h3 style="color: #667eea;">💰 VALUE VS COST ANALYSIS</h3>', unsafe_allow_html=True)
                    
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
                    
                    # Overpriced and undervalued players
                    st.markdown("---")
                    overpriced = data.get('overpriced_players', [])
                    undervalued = data.get('undervalued_players', [])
                    
                    col_over, col_under = st.columns(2)
                    
                    with col_over:
                        st.markdown(f'<h3 style="color: #ff6b6b;">🔴 OVERPRICED PLAYERS ({len(overpriced)})</h3>', unsafe_allow_html=True)
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
                        st.markdown(f'<h3 style="color: #4CAF50;">🟢 UNDervalued PLAYERS ({len(undervalued)})</h3>', unsafe_allow_html=True)
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
                    
                    # Replacement suggestions
                    st.markdown("---")
                    st.markdown('<h3 style="color: #764ba2;">🔁 REPLACEMENT OPPORTUNITIES</h3>', unsafe_allow_html=True)
                    
                    replacement_opps = data.get('replacement_opportunities', [])
                    
                    if replacement_opps:
                        for opp in replacement_opps:
                            replace_player = opp.get('replace_player', '')
                            suggestions = opp.get('suggestions', [])
                            
                            st.markdown(f"""
                            <div class="metric-card" style="margin-bottom: 20px;">
                                <h4 style="color: #ff6b6b; margin-bottom: 10px;">Replace: {replace_player}</h4>
                                <p style="color: #94A3B8;"><strong>Reason:</strong> {opp.get('reason', 'Overpriced')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            for i, sug in enumerate(suggestions, 1):
                                st.markdown(f"""
                                <div class="status-undervalued" style="margin-left: 20px; margin-bottom: 10px;">
                                    <strong>Suggestion {i}: {sug['suggested_player']}</strong> ({sug['role']})<br>
                                    <small>Predicted Value: ₹{sug['predicted_value']:.2f}Cr | Price: ₹{sug['predicted_price']:.2f}Cr</small><br>
                                    <small>Performance: {sug['performance_score']:.1f}/100 | Risk: {sug['risk_score']:.2f}</small><br>
                                    <em style="color: #4CAF50;">💡 {sug['reason']}</em>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.success("✅ Your team is well optimized! No critical replacements needed.")
                    
                    # Recommendations
                    st.markdown("---")
                    st.markdown('<h3 style="color: #4CAF50;">💡 AI RECOMMENDATIONS</h3>', unsafe_allow_html=True)
                    recommendations = data.get('recommendations', [])
                    
                    for rec in recommendations:
                        icon = "✅" if "Good" in rec or "Great" in rec else "⚠️" if "Critical" in rec else "💡"
                        st.write(f"{icon} {rec}")
                
                elif response.status_code == 400:
                    error_detail = response.json().get('detail', 'Unknown error')
                    st.error(f"❌ {error_detail}")
                    st.info("💡 Please go to the **Players** tab and add more players to your team first.")
                else:
                    st.error(f"Failed to get analysis from API. Status: {response.status_code}")
            
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. The backend server may be busy. Please try again.")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Cannot connect to backend server. Make sure it's running on http://localhost:8000")
                st.info("💡 Run: `python run_backend.py` in the project directory")
            except Exception as e:
                st.error(f"Error: {e}")
                st.info("💡 Make sure the backend server is running and models are trained.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_auction_strategy():
    """Render Auction Strategy page"""
    
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    st.markdown('<h1 class="section-header">💼 AUCTION STRATEGY</h1>', unsafe_allow_html=True)
    
    squad = st.session_state.selected_players
    
    if not squad:
        alert_box("Build your team first to see auction strategy!", "warning")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    budget_spent = sum([p.get('sold_price', 0) for p in squad])
    remaining = 120 - budget_spent
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #667eea; margin-bottom: 15px;">📊 BUDGET ALLOCATION</h3>
            <p style="color: #94A3B8;">Recommended spending strategy:</p>
            <ul style="color: #E6F1FF; line-height: 2;">
                <li><strong>Top Picks (3-4):</strong> ₹15-23 Cr each</li>
                <li><strong>Mid-range (5-7):</strong> ₹5-12 Cr each</li>
                <li><strong>Budget Picks (3-5):</strong> ₹1-4 Cr each</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #764ba2; margin-bottom: 15px;">🎯 KEY INSIGHTS</h3>
            <ul style="color: #E6F1FF; line-height: 2;">
                <li>Don't overspend on WKs (1-2 enough)</li>
                <li>Invest in quality batsmen</li>
                <li>All-rounders provide best value</li>
                <li>Need at least 4 specialist bowlers</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== MAIN APP LOGIC ====================

def main():
    """Main application"""
    
    # Render sidebar
    render_sidebar(st.session_state.page)
    
    # Route to appropriate page
    page = st.session_state.page
    
    if page == "Home":
        render_home()
    elif page == "Players":
        render_players()
    elif page == "Team Builder":
        render_team_builder()
    elif page == "Analytics":
        render_analytics()
    elif page == "AI Suggestions":
        render_ai_suggestions()
    elif page == "Best XI":
        render_best_xi()
    elif page == "Team Optimization AI":
        render_team_optimization()
    elif page == "Auction Strategy":
        render_auction_strategy()
    else:
        render_home()

if __name__ == "__main__":
    main()
