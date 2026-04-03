"""
AI-Powered IPL Match Simulator and Player Analysis System
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, accuracy_score
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Tuple
import json

# ==================== CONFIGURATION ====================

st.set_page_config(
    page_title="IPL Match Simulator | AI-Powered",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== LOAD DATA ====================

@st.cache_data
def load_ipl_data():
    """Load IPL dataset"""
    try:
        # Try multiple possible paths
        possible_paths = [
            'data/processed/ipl_2025_complete.json',
            '../data/processed/ipl_2025_complete.json',
            'data\\processed\\ipl_2025_complete.json',
            '..\\data\\processed\\ipl_2025_complete.json'
        ]
        
        for path in possible_paths:
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                return pd.DataFrame(data['players'])
            except FileNotFoundError:
                continue
        
        # If all paths fail, try absolute path
        import os
        abs_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'ipl_2025_complete.json')
        with open(abs_path, 'r') as f:
            data = json.load(f)
        return pd.DataFrame(data['players'])
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

@st.cache_data
def load_advanced_analytics():
    """Load advanced analytics dataset"""
    try:
        # Try multiple possible paths
        possible_paths = [
            'data/analytics/advanced_ipl_analytics.json',
            '../data/analytics/advanced_ipl_analytics.json',
            'data\\analytics\\advanced_ipl_analytics.json',
            '..\\data\\analytics\\advanced_ipl_analytics.json'
        ]
        
        for path in possible_paths:
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except FileNotFoundError:
                continue
        
        # If all paths fail, try absolute path
        import os
        abs_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'analytics', 'advanced_ipl_analytics.json')
        with open(abs_path, 'r') as f:
            return json.load(f)
    except:
        return {}

# ==================== ML MODELS ====================

class PlayerPerformancePredictor:
    """ML model for predicting player performance"""
    
    def __init__(self):
        self.batting_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.bowling_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
        
    def prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """Prepare features for ML model"""
        features = []
        for _, row in df.iterrows():
            feature_vector = [
                row.get('matches', 0),
                row.get('runs', 0),
                row.get('wickets', 0),
                row.get('strike_rate', 0),
                row.get('economy', 0),
                row.get('performance_score', 0),
                row.get('value_score', 0)
            ]
            features.append(feature_vector)
        return np.array(features)
    
    def train(self, df: pd.DataFrame):
        """Train ML models on player data"""
        if len(df) < 10:
            return
        
        X = self.prepare_features(df)
        
        # Create target variables (normalized performance)
        y_batting = (df['runs'] * df['strike_rate'] / 100).values
        y_bowling = (df['wickets'] * (10 - df['economy'].clip(0, 10))).values
        
        # Train batting model
        self.batting_model.fit(X, y_batting)
        
        # Train bowling model
        self.bowling_model.fit(X, y_bowling)
        
        self.is_trained = True
    
    def predict_batsman_performance(self, player: dict) -> float:
        """Predict expected runs for a batsman"""
        if not self.is_trained:
            return player.get('runs', 0) * 0.3
        
        X = self.prepare_features(pd.DataFrame([player]))
        predicted = self.batting_model.predict(X)[0]
        return max(0, predicted)
    
    def predict_bowler_performance(self, player: dict) -> float:
        """Predict expected wickets for a bowler"""
        if not self.is_trained:
            return player.get('wickets', 0) * 0.3
        
        X = self.prepare_features(pd.DataFrame([player]))
        predicted = self.bowling_model.predict(X)[0]
        return max(0, predicted)
    
    def calculate_player_score(self, player: dict) -> float:
        """Calculate overall player performance score"""
        role = player.get('role', '')
        
        if 'Batsman' in role or 'batsman' in role:
            return self.predict_batsman_performance(player)
        elif 'Bowler' in role or 'bowler' in role:
            return self.predict_bowler_performance(player) * 10  # Scale wickets
        elif 'All-rounder' in role or 'all-rounder' in role:
            bat_score = self.predict_batsman_performance(player)
            bowl_score = self.predict_bowler_performance(player) * 10
            return bat_score + bowl_score
        else:
            return player.get('performance_score', 50)


class MatchSimulator:
    """Simulate match outcomes using ML"""
    
    def __init__(self):
        self.win_predictor = LogisticRegression(random_state=42)
        
    def calculate_team_strength(self, playing_xi: List[dict], predictor: PlayerPerformancePredictor) -> float:
        """Calculate total team strength from playing XI"""
        total_strength = 0
        
        for player in playing_xi:
            player_score = predictor.calculate_player_score(player)
            total_strength += player_score
        
        return total_strength
    
    def simulate_match(self, team_a_xi: List[dict], team_b_xi: List[dict], 
                      predictor: PlayerPerformancePredictor) -> Dict:
        """Simulate a match between two teams"""
        
        # Calculate team strengths
        team_a_strength = self.calculate_team_strength(team_a_xi, predictor)
        team_b_strength = self.calculate_team_strength(team_b_xi, predictor)
        
        # Add randomness for realism (±15%)
        team_a_score = team_a_strength * np.random.uniform(0.85, 1.15)
        team_b_score = team_b_strength * np.random.uniform(0.85, 1.15)
        
        # Calculate win probability using logistic function
        strength_diff = team_a_strength - team_b_strength
        win_prob_a = 1 / (1 + np.exp(-strength_diff / 50))
        win_prob_b = 1 - win_prob_a
        
        # Determine winner
        winner = "Team A" if team_a_score > team_b_score else "Team B"
        
        return {
            'team_a_score': team_a_score,
            'team_b_score': team_b_score,
            'team_a_strength': team_a_strength,
            'team_b_strength': team_b_strength,
            'win_probability_a': win_prob_a * 100,
            'win_probability_b': win_prob_b * 100,
            'winner': winner,
            'margin': abs(team_a_score - team_b_score)
        }


class PlayerComparator:
    """Compare two players using statistics"""
    
    @staticmethod
    def compare(player_a: dict, player_b: dict) -> Dict:
        """Compare two players across multiple metrics"""
        
        # Calculate composite scores
        a_batting_score = player_a.get('runs', 0) * player_a.get('strike_rate', 100) / 100
        b_batting_score = player_b.get('runs', 0) * player_b.get('strike_rate', 100) / 100
        
        a_bowling_score = player_a.get('wickets', 0) * (10 - min(player_a.get('economy', 10), 10))
        b_bowling_score = player_b.get('wickets', 0) * (10 - min(player_b.get('economy', 10), 10))
        
        a_total = a_batting_score + a_bowling_score
        b_total = b_batting_score + b_bowling_score
        
        better_player = player_a['name'] if a_total > b_total else player_b['name']
        
        return {
            'player_a': {
                'name': player_a['name'],
                'batting_score': a_batting_score,
                'bowling_score': a_bowling_score,
                'total_score': a_total
            },
            'player_b': {
                'name': player_b['name'],
                'batting_score': b_batting_score,
                'bowling_score': b_bowling_score,
                'total_score': b_total
            },
            'better_player': better_player,
            'score_difference': abs(a_total - b_total)
        }


class AIInsightsGenerator:
    """Generate AI-powered insights"""
    
    @staticmethod
    def generate_team_insights(playing_xi: List[dict]) -> List[str]:
        """Generate insights for a team"""
        insights = []
        
        # Count roles
        batsmen = sum(1 for p in playing_xi if 'Batsman' in p.get('role', ''))
        bowlers = sum(1 for p in playing_xi if 'Bowler' in p.get('role', ''))
        all_rounders = sum(1 for p in playing_xi if 'All-rounder' in p.get('role', ''))
        
        # Batting strength
        avg_strike_rate = np.mean([p.get('strike_rate', 100) for p in playing_xi])
        if avg_strike_rate > 140:
            insights.append("🔥 Explosive batting lineup with high strike rate")
        elif avg_strike_rate < 120:
            insights.append("⚠️ Batting strike rate needs improvement")
        else:
            insights.append("✅ Balanced batting approach")
        
        # Bowling strength
        avg_economy = np.mean([p.get('economy', 8) for p in playing_xi if p.get('economy', 0) > 0])
        if avg_economy < 7.5:
            insights.append("🎯 Excellent bowling economy rate")
        elif avg_economy > 9:
            insights.append("⚠️ Bowling economy needs improvement")
        else:
            insights.append("✅ Decent bowling attack")
        
        # Team composition
        if batsmen >= 6:
            insights.append("💪 Strong batting depth")
        if bowlers >= 5:
            insights.append("🎳 Quality bowling attack")
        if all_rounders >= 3:
            insights.append("🔄 Great all-round balance")
        
        # Experience
        avg_matches = np.mean([p.get('matches', 0) for p in playing_xi])
        if avg_matches > 100:
            insights.append("🎓 Highly experienced squad")
        elif avg_matches < 50:
            insights.append("🌟 Young and energetic team")
        
        return insights
    
    @staticmethod
    def generate_player_insight(player: dict) -> str:
        """Generate insight for individual player"""
        role = player.get('role', '')
        value_score = player.get('value_score', 0)
        
        if value_score > 20:
            return f"💎 {player['name']} is excellent value for money!"
        elif value_score < 5:
            return f"⚠️ {player['name']} may be overpriced"
        
        if 'Batsman' in role and player.get('strike_rate', 100) > 150:
            return f"⚡ {player['name']} is a power hitter"
        elif 'Bowler' in role and player.get('economy', 10) < 7:
            return f"🎯 {player['name']} is an economical bowler"
        
        return f"👤 {player['name']} is a solid pick"


# ==================== UI COMPONENTS ====================

def render_team_selection(df: pd.DataFrame) -> Tuple[str, str]:
    """Render team selection UI"""
    st.title("🏏 IPL Match Simulator & Player Analysis")
    st.markdown("### Powered by Artificial Intelligence & Machine Learning")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔵 Team A")
        teams = sorted(df['team'].unique())
        team_a = st.selectbox("Select Team A", teams, key="team_a")
    
    with col2:
        st.markdown("#### 🔴 Team B")
        team_b = st.selectbox("Select Team B", teams, key="team_b", index=len(teams)//2)
    
    return team_a, team_b


def render_playing_xi_selection(df: pd.DataFrame, team_name: str, team_label: str) -> List[dict]:
    """Render playing XI selection UI"""
    st.markdown(f"### {team_label}: {team_name}")
    
    team_players = df[df['team'] == team_name].to_dict('records')
    
    if len(team_players) == 0:
        st.warning(f"No players found for {team_name}")
        return []
    
    # Display players in grid
    cols = st.columns(3)
    selected_players = []
    
    for i, player in enumerate(team_players[:18]):  # Show top 18
        with cols[i % 3]:
            is_selected = st.checkbox(
                f"{player['name']} ({player['role']})",
                value=False,
                key=f"{team_label}_{player['id']}"
            )
            if is_selected:
                selected_players.append(player)
            
            # Show stats
            st.caption(f"Matches: {player.get('matches', 0)}")
            if 'Batsman' in player.get('role', ''):
                st.caption(f"Runs: {player.get('runs', 0)} | SR: {player.get('strike_rate', 0)}")
            elif 'Bowler' in player.get('role', ''):
                st.caption(f"Wickets: {player.get('wickets', 0)} | Eco: {player.get('economy', 0)}")
    
    return selected_players


def render_match_simulation(result: Dict, team_a_name: str, team_b_name: str):
    """Render match simulation results"""
    st.markdown("## 🎯 Match Simulation Results")
    
    # Score display
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(f"{team_a_name} Score", f"{result['team_a_score']:.1f}")
        st.progress(result['win_probability_a'] / 100)
        st.caption(f"Win Probability: {result['win_probability_a']:.1f}%")
    
    with col2:
        st.metric(f"{team_b_name} Score", f"{result['team_b_score']:.1f}")
        st.progress(result['win_probability_b'] / 100)
        st.caption(f"Win Probability: {result['win_probability_b']:.1f}%")
    
    # Winner announcement
    winner_name = team_a_name if result['winner'] == "Team A" else team_b_name
    st.success(f"🏆 Winner: **{winner_name}** by {result['margin']:.1f} runs")
    
    # Visualization
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=['Team A Strength', 'Team B Strength'],
        y=[result['team_a_strength'], result['team_b_strength']],
        marker_color=['#1f77b4', '#ff7f0e']
    ))
    
    fig.update_layout(
        title="Team Strength Comparison",
        yaxis_title="Strength Score"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Win probability pie chart
    fig2 = go.Figure(data=[go.Pie(
        labels=[team_a_name, team_b_name],
        values=[result['win_probability_a'], result['win_probability_b']],
        hole=.3
    )])
    
    fig2.update_layout(title="Win Probability Distribution")
    st.plotly_chart(fig2, use_container_width=True)


def render_player_comparison(df: pd.DataFrame):
    """Render player comparison UI"""
    st.markdown("## ⚔️ Player Comparison")
    
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        players_list = sorted(df['name'].unique())
        player_a_name = st.selectbox("Select Player A", players_list, key="comp_a")
    
    with col3:
        player_b_name = st.selectbox("Select Player B", players_list, key="comp_b")
    
    if st.button("🔍 Compare Players", type="primary"):
        player_a = df[df['name'] == player_a_name].iloc[0].to_dict() if len(df[df['name'] == player_a_name]) > 0 else None
        player_b = df[df['name'] == player_b_name].iloc[0].to_dict() if len(df[df['name'] == player_b_name]) > 0 else None
        
        if player_a and player_b:
            comparator = PlayerComparator()
            comparison = comparator.compare(player_a, player_b)
            
            # Display comparison
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"### {comparison['player_a']['name']}")
                st.metric("Batting Score", f"{comparison['player_a']['batting_score']:.1f}")
                st.metric("Bowling Score", f"{comparison['player_a']['bowling_score']:.1f}")
                st.metric("Total Score", f"{comparison['player_a']['total_score']:.1f}")
            
            with col2:
                st.markdown(f"### {comparison['player_b']['name']}")
                st.metric("Batting Score", f"{comparison['player_b']['batting_score']:.1f}")
                st.metric("Bowling Score", f"{comparison['player_b']['bowling_score']:.1f}")
                st.metric("Total Score", f"{comparison['player_b']['total_score']:.1f}")
            
            # Better player
            st.success(f"🏆 **{comparison['better_player']}** is better by {comparison['score_difference']:.1f} points")
            
            # Radar chart
            fig = go.Figure()
            
            categories = ['Batting', 'Bowling']
            
            fig.add_trace(go.Scatterpolar(
                r=[comparison['player_a']['batting_score'], comparison['player_a']['bowling_score']],
                theta=categories,
                fill='toself',
                name=comparison['player_a']['name']
            ))
            
            fig.add_trace(go.Scatterpolar(
                r=[comparison['player_b']['batting_score'], comparison['player_b']['bowling_score']],
                theta=categories,
                fill='toself',
                name=comparison['player_b']['name']
            ))
            
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True)),
                showlegend=True,
                title="Player Comparison Radar Chart"
            )
            
            st.plotly_chart(fig, use_container_width=True)


# ==================== MAIN APP ====================

def main():
    """Main application"""
    
    # Load data
    df = load_ipl_data()
    analytics = load_advanced_analytics()
    
    if len(df) == 0:
        st.error("Failed to load data. Please ensure the dataset exists.")
        return
    
    # Initialize ML models
    predictor = PlayerPerformancePredictor()
    simulator = MatchSimulator()
    
    # Train ML model
    with st.spinner("🤖 Training AI models..."):
        predictor.train(df)
    
    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Match Simulator", "Player Comparison", "Team Analysis"]
    )
    
    if page == "Match Simulator":
        # Team selection
        team_a_name, team_b_name = render_team_selection(df)
        
        if team_a_name == team_b_name:
            st.warning("Please select different teams")
            return
        
        # Playing XI selection
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            team_a_xi = render_playing_xi_selection(df, team_a_name, "Team A")
            st.info(f"Selected: {len(team_a_xi)} players")
        
        with col2:
            team_b_xi = render_playing_xi_selection(df, team_b_name, "Team B")
            st.info(f"Selected: {len(team_b_xi)} players")
        
        # Simulate button
        if st.button("🎮 Simulate Match", type="primary"):
            if len(team_a_xi) >= 11 and len(team_b_xi) >= 11:
                with st.spinner("🤖 AI is simulating match..."):
                    result = simulator.simulate_match(team_a_xi, team_b_xi, predictor)
                    render_match_simulation(result, team_a_name, team_b_name)
                    
                    # AI Insights
                    st.markdown("---")
                    st.markdown("## 💡 AI Insights")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"### {team_a_name} Insights")
                        insights_a = AIInsightsGenerator.generate_team_insights(team_a_xi)
                        for insight in insights_a:
                            st.write(insight)
                    
                    with col2:
                        st.markdown(f"### {team_b_name} Insights")
                        insights_b = AIInsightsGenerator.generate_team_insights(team_b_xi)
                        for insight in insights_b:
                            st.write(insight)
            else:
                st.error("Please select at least 11 players for each team")
    
    elif page == "Player Comparison":
        render_player_comparison(df)
    
    elif page == "Team Analysis":
        st.title("📊 Team Performance Analysis")
        
        # Select team to analyze
        teams = sorted(df['team'].unique())
        selected_team = st.selectbox("Select Team", teams)
        
        team_df = df[df['team'] == selected_team]
        
        # Display stats
        st.markdown(f"### {selected_team} Squad Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Players", len(team_df))
        
        with col2:
            avg_performance = team_df['performance_score'].mean()
            st.metric("Avg Performance", f"{avg_performance:.1f}")
        
        with col3:
            avg_value = team_df['value_score'].mean()
            st.metric("Avg Value Score", f"{avg_value:.1f}")
        
        # Role distribution
        role_counts = team_df['role'].value_counts()
        fig = px.pie(values=role_counts.values, names=role_counts.index, title="Role Distribution")
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance distribution
        fig2 = px.histogram(team_df, x='performance_score', title="Performance Score Distribution")
        st.plotly_chart(fig2, use_container_width=True)
        
        # Top performers
        st.markdown("### 🌟 Top Performers")
        top_players = team_df.nlargest(10, 'performance_score')[['name', 'role', 'performance_score', 'value_score']]
        st.dataframe(top_players, use_container_width=True)


if __name__ == "__main__":
    main()
