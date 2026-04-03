"""
AI-Powered Fantasy Cricket Team Optimizer (Dream11-like)
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from model import DataLoader
from ml_model import FantasyPointsPredictor
from optimizer import TeamOptimizer
from simulator import MatchSimulator
from utils import PlayerComparator, AIInsightsGenerator, format_points, get_role_short_name

# ==================== CONFIGURATION ====================

st.set_page_config(
    page_title="AI Fantasy Cricket Team Generator",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
}
.sub-header {
    font-size: 1.2rem;
    color: #666;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 0.5rem;
    color: white;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ==================== CACHE DATA ====================

@st.cache_resource
def load_all_data():
    """Load all data and initialize models"""
    loader = DataLoader()
    
    try:
        df = loader.load_ipl_complete_data()
        analytics = loader.load_advanced_analytics()
        
        # Prepare features
        df_processed = loader.prepare_features(df)
        
        return df, df_processed, analytics
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame(), None

@st.cache_resource
def train_ml_model(df: pd.DataFrame):
    """Train ML model for fantasy points prediction"""
    predictor = FantasyPointsPredictor(model_type='random_forest')
    
    try:
        metrics = predictor.train(df)
        return predictor, metrics
    except Exception as e:
        st.error(f"Error training model: {e}")
        return None, None

# ==================== UI COMPONENTS ====================

def render_header():
    """Render application header"""
    st.markdown('<p class="main-header">🏏 AI Fantasy Cricket Team Generator</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Powered by Machine Learning • Dream11-Style Team Optimization</p>', unsafe_allow_html=True)
    st.markdown("---")

def render_team_selection_ui(teams: List[str]) -> tuple:
    """Render team selection interface"""
    st.markdown("### 🎯 Step 1: Select Teams")
    
    col1, col2 = st.columns(2)
    
    with col1:
        team_a = st.selectbox("Select Team A", teams, key="team_a_select")
    
    with col2:
        team_b = st.selectbox("Select Team B", teams, index=len(teams)//2 if len(teams) > 1 else 0, key="team_b_select")
    
    return team_a, team_b

def render_player_selection_ui(df: pd.DataFrame, team_name: str, predictor: FantasyPointsPredictor) -> pd.DataFrame:
    """Render player selection interface"""
    st.markdown(f"### 👥 Players from {team_name}")
    
    # Filter players by team
    team_players = df[df['team'] == team_name].copy()
    
    if len(team_players) == 0:
        st.warning(f"No players found for {team_name}")
        return pd.DataFrame()
    
    # Predict points if not already done
    if 'predicted_fantasy_points' not in team_players.columns:
        predictions = predictor.predict(team_players)
        team_players['predicted_fantasy_points'] = predictions
    
    # Reset index to ensure clean integer indexing
    team_players = team_players.reset_index(drop=True)
    
    # Display in 3 columns
    cols = st.columns(3)
    selected_player_ids = []
    
    for i, (_, player) in enumerate(team_players.iterrows()):
        with cols[i % 3]:
            is_selected = st.checkbox(
                f"{player['name']} ({get_role_short_name(player['role'])})",
                value=False,
                key=f"select_{team_name}_{player['id']}_{i}"
            )
            
            if is_selected:
                selected_player_ids.append(player['id'])
            
            # Show predicted points
            pred_points = player.get('predicted_fantasy_points', 0)
            st.caption(f"Pred Points: {format_points(pred_points)}")
    
    # Return selected players by ID instead of index
    if selected_player_ids:
        return team_players[team_players['id'].isin(selected_player_ids)]
    else:
        return pd.DataFrame()

def render_best_team_display(optimal_team: pd.DataFrame, captain, vice_captain, total_score: float):
    """Display optimal team with captain and vice-captain"""
    st.markdown("### 🌟 AI-Generated Best XI")
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Players", len(optimal_team))
    
    with col2:
        st.metric("Total Predicted Points", f"{total_score:.1f}")
    
    with col3:
        st.metric("Average Points", f"{optimal_team['predicted_fantasy_points'].mean():.1f}")
    
    with col4:
        st.metric("Team Strength", f"{len(optimal_team) * 10}/10")
    
    # Display captain and vice-captain
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"#### 🏆 Captain (2x Points)")
        st.success(f"**{captain['name']}** - {format_points(captain['predicted_fantasy_points'] * 2)} pts")
        st.caption(f"Role: {captain['role']} | Team: {captain['team']}")
    
    with col2:
        st.markdown(f"#### ⭐ Vice-Captain (1.5x Points)")
        st.info(f"**{vice_captain['name']}** - {format_points(vice_captain['predicted_fantasy_points'] * 1.5)} pts")
        st.caption(f"Role: {vice_captain['role']} | Team: {vice_captain['team']}")
    
    # Display full team table
    st.markdown("---")
    st.markdown("#### Complete Playing XI")
    
    display_df = optimal_team[['name', 'role', 'team', 'predicted_fantasy_points']].copy()
    display_df.columns = ['Name', 'Role', 'Team', 'Pred. Points']
    display_df = display_df.sort_values('Pred. Points', ascending=False)
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)

def render_visualizations(optimal_team: pd.DataFrame):
    """Render visualizations for team analysis"""
    st.markdown("### 📊 Team Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Role distribution pie chart
        role_counts = optimal_team['role'].value_counts()
        fig_pie = go.Figure(data=[go.Pie(
            labels=[get_role_short_name(r) for r in role_counts.index],
            values=role_counts.values,
            hole=0.3
        )])
        
        fig_pie.update_layout(title="Role Distribution")
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Predicted points bar chart
        fig_bar = px.bar(
            optimal_team.sort_values('predicted_fantasy_points', ascending=True),
            x='predicted_fantasy_points',
            y='name',
            orientation='h',
            title="Player Contribution Analysis",
            color='predicted_fantasy_points',
            color_continuous_scale='Blues'
        )
        
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Team composition breakdown
    st.markdown("---")
    st.markdown("#### Team Composition")
    
    composition_cols = st.columns(4)
    comp_dict = {'Batsman': 0, 'Bowler': 0, 'All-rounder': 0, 'Wicket-keeper': 0}
    
    for _, player in optimal_team.iterrows():
        role = str(player['role'])
        if 'Wicket-keeper' in role:
            comp_dict['Wicket-keeper'] += 1
        elif 'Bowler' in role:
            comp_dict['Bowler'] += 1
        elif 'All-rounder' in role:
            comp_dict['All-rounder'] += 1
        else:
            comp_dict['Batsman'] += 1
    
    for i, (role, count) in enumerate(comp_dict.items()):
        with composition_cols[i]:
            st.metric(role, count)

def render_insights(insights: List[str]):
    """Display AI insights"""
    st.markdown("### 💡 AI Insights")
    
    for insight in insights:
        st.info(insight)

def render_player_comparison(df: pd.DataFrame):
    """Render player comparison interface"""
    st.markdown("### ⚔️ Player Comparison")
    
    players_list = sorted(df['name'].unique())
    
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        player_a_name = st.selectbox("Select Player A", players_list, key="comp_player_a")
    
    with col3:
        player_b_name = st.selectbox("Select Player B", players_list, key="comp_player_b")
    
    if st.button("🔍 Compare Players"):
        player_a = df[df['name'] == player_a_name].iloc[0] if len(df[df['name'] == player_a_name]) > 0 else None
        player_b = df[df['name'] == player_b_name].iloc[0] if len(df[df['name'] == player_b_name]) > 0 else None
        
        if player_a is not None and player_b is not None:
            comparator = PlayerComparator()
            comparison = comparator.compare(player_a, player_b)
            
            # Display comparison
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"#### {comparison['player_a']['name']}")
                st.metric("Batting Score", f"{comparison['player_a']['batting_score']:.1f}")
                st.metric("Bowling Score", f"{comparison['player_a']['bowling_score']:.1f}")
                st.metric("Total Score", f"{comparison['player_a']['total_score']:.1f}")
                st.metric("Predicted Points", f"{comparison['player_a']['predicted_points']:.1f}")
            
            with col2:
                st.markdown(f"#### {comparison['player_b']['name']}")
                st.metric("Batting Score", f"{comparison['player_b']['batting_score']:.1f}")
                st.metric("Bowling Score", f"{comparison['player_b']['bowling_score']:.1f}")
                st.metric("Total Score", f"{comparison['player_b']['total_score']:.1f}")
                st.metric("Predicted Points", f"{comparison['player_b']['predicted_points']:.1f}")
            
            # Better player
            st.success(f"🏆 **{comparison['better_player']}** is better by {comparison['score_difference']:.1f} points")
            
            # Radar chart
            fig_radar = go.Figure()
            
            categories = ['Batting', 'Bowling']
            
            fig_radar.add_trace(go.Scatterpolar(
                r=[comparison['player_a']['batting_score'], comparison['player_a']['bowling_score']],
                theta=categories,
                fill='toself',
                name=comparison['player_a']['name']
            ))
            
            fig_radar.add_trace(go.Scatterpolar(
                r=[comparison['player_b']['batting_score'], comparison['player_b']['bowling_score']],
                theta=categories,
                fill='toself',
                name=comparison['player_b']['name']
            ))
            
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True)),
                showlegend=True,
                title="Player Comparison Radar Chart"
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)

def render_match_simulation(team_a_df: pd.DataFrame, team_b_df: pd.DataFrame):
    """Render match simulation results"""
    st.markdown("### 🎮 Match Simulation (50 Simulations)")
    
    simulator = MatchSimulator()
    
    # Run simulations
    with st.spinner("🔄 Running 50 match simulations..."):
        analysis = simulator.get_detailed_analysis(team_a_df, team_b_df, n_simulations=50)
    
    # Display results
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Team A Wins", f"{analysis['simulation_results']['team_a_wins']}/50")
        st.progress(analysis['simulation_results']['team_a_win_percentage'] / 100)
        st.caption(f"Win Rate: {analysis['simulation_results']['team_a_win_percentage']:.1f}%")
    
    with col2:
        st.metric("Team B Wins", f"{analysis['simulation_results']['team_b_wins']}/50")
        st.progress(analysis['simulation_results']['team_b_win_percentage'] / 100)
        st.caption(f"Win Rate: {analysis['simulation_results']['team_b_win_percentage']:.1f}%")
    
    # Win probability
    prob_a, prob_b = analysis['win_probabilities']['team_a'], analysis['win_probabilities']['team_b']
    
    st.markdown("---")
    st.markdown("#### Win Probability")
    
    fig_pie = go.Figure(data=[go.Pie(
        labels=['Team A', 'Team B'],
        values=[prob_a, prob_b],
        hole=0.4
    )])
    
    fig_pie.update_layout(title="Match Win Probability Distribution")
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Prediction confidence
    st.markdown("---")
    st.info(f"🎯 **Prediction Confidence:** {analysis['prediction_confidence']}")
    st.caption(f"Based on {50} Monte Carlo simulations")

# ==================== MAIN APPLICATION ====================

def main():
    """Main application"""
    
    # Render header
    render_header()
    
    # Load data
    df_raw, df_processed, analytics = load_all_data()
    
    if len(df_raw) == 0:
        st.error("Failed to load data. Please ensure dataset files exist.")
        return
    
    # Train ML model
    with st.spinner("🤖 Training AI model for fantasy points prediction..."):
        predictor, metrics = train_ml_model(df_processed)
    
    if predictor is None:
        st.error("Failed to train ML model")
        return
    
    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Fantasy Team Generator", "Player Comparison", "Match Simulation"]
    )
    
    if page == "Fantasy Team Generator":
        # Team selection
        teams = df_raw['team'].unique().tolist()
        team_a, team_b = render_team_selection_ui(teams)
        
        if team_a == team_b:
            st.warning("⚠️ Please select different teams")
            return
        
        st.markdown("---")
        
        # Player selection
        col1, col2 = st.columns(2)
        
        with col1:
            selected_team_a = render_player_selection_ui(df_processed, team_a, predictor)
        
        with col2:
            selected_team_b = render_player_selection_ui(df_processed, team_b, predictor)
        
        # Generate team button
        st.markdown("---")
        if st.button("🚀 Generate Best Fantasy Team", type="primary"):
            if len(selected_team_a) + len(selected_team_b) < 11:
                st.error("❌ Please select at least 11 players total")
            else:
                # Combine selected players
                all_selected = pd.concat([selected_team_a, selected_team_b], ignore_index=True)
                
                if len(all_selected) < 11:
                    st.error("Need at least 11 players to generate optimal team")
                    return
                
                # Predict points
                predictions = predictor.predict(all_selected)
                all_selected['predicted_fantasy_points'] = predictions
                
                # Generate optimal team
                optimizer = TeamOptimizer()
                optimal_team = optimizer.generate_optimal_team(all_selected, predictions)
                
                if len(optimal_team) < 11:
                    st.error("Could not generate valid team with constraints")
                    return
                
                # Select captain and vice-captain
                captain, vice_captain = optimizer.select_captain_vice_captain(optimal_team)
                
                # Calculate total score
                total_score = optimizer.calculate_team_score(
                    optimal_team, 
                    captain['id'], 
                    vice_captain['id']
                )
                
                # Validate team
                is_valid, issues = optimizer.validate_team(optimal_team)
                
                if not is_valid:
                    st.warning("⚠️ Team validation issues:")
                    for issue in issues:
                        st.write(f"- {issue}")
                
                # Display results
                st.markdown("---")
                render_best_team_display(optimal_team, captain, vice_captain, total_score)
                
                # Visualizations
                st.markdown("---")
                render_visualizations(optimal_team)
                
                # AI insights
                insights = AIInsightsGenerator.generate_team_insights(optimal_team)
                render_insights(insights)
    
    elif page == "Player Comparison":
        # Predict points for all players
        if 'predicted_fantasy_points' not in df_processed.columns:
            predictions = predictor.predict(df_processed)
            df_processed['predicted_fantasy_points'] = predictions
        
        render_player_comparison(df_processed)
    
    elif page == "Match Simulation":
        st.markdown("### 🔮 AI Match Predictor")
        
        # Get two fantasy teams
        teams = df_raw['team'].unique().tolist()
        
        col1, col2 = st.columns(2)
        
        with col1:
            sim_team_a_name = st.selectbox("Team A", teams, key="sim_team_a")
        
        with col2:
            sim_team_b_name = st.selectbox("Team B", teams, index=len(teams)//2, key="sim_team_b")
        
        if sim_team_a_name != sim_team_b_name:
            if st.button("🎮 Run Match Simulation"):
                # Get top 11 from each team
                team_a_players = df_processed[df_processed['team'] == sim_team_a_name].nlargest(11, 'performance_score')
                team_b_players = df_processed[df_processed['team'] == sim_team_b_name].nlargest(11, 'performance_score')
                
                # Predict points
                pred_a = predictor.predict(team_a_players)
                pred_b = predictor.predict(team_b_players)
                
                team_a_players['predicted_fantasy_points'] = pred_a
                team_b_players['predicted_fantasy_points'] = pred_b
                
                # Run simulation
                render_match_simulation(team_a_players, team_b_players)
                
                # AI insights
                match_insights = AIInsightsGenerator.generate_match_insights(team_a_players, team_b_players)
                render_insights(match_insights)

if __name__ == "__main__":
    main()
