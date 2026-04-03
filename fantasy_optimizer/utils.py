"""
Utility Functions for Fantasy Cricket Team Optimizer
Includes player comparison, insights generation, and helpers
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional


class PlayerComparator:
    """Compare two players across multiple metrics"""
    
    @staticmethod
    def compare(player_a: pd.Series, player_b: pd.Series) -> Dict:
        """
        Compare two players
        
        Args:
            player_a: First player Series
            player_b: Second player Series
            
        Returns:
            Dictionary with comparison results
        """
        # Calculate composite scores
        a_batting_score = player_a.get('runs', 0) * player_a.get('strike_rate', 100) / 100
        b_batting_score = player_b.get('runs', 0) * player_b.get('strike_rate', 100) / 100
        
        a_bowling_score = player_a.get('wickets', 0) * max(0, 10 - player_a.get('economy', 10))
        b_bowling_score = player_b.get('wickets', 0) * max(0, 10 - player_b.get('economy', 10))
        
        a_total = a_batting_score + a_bowling_score
        b_total = b_batting_score + b_bowling_score
        
        better_player = player_a['name'] if a_total > b_total else player_b['name']
        
        comparison = {
            'player_a': {
                'name': player_a['name'],
                'batting_score': a_batting_score,
                'bowling_score': a_bowling_score,
                'total_score': a_total,
                'avg': player_a.get('batting_average', player_a.get('runs', 0)),
                'strike_rate': player_a.get('strike_rate', 0),
                'wickets': player_a.get('wickets', 0),
                'predicted_points': player_a.get('predicted_fantasy_points', 0)
            },
            'player_b': {
                'name': player_b['name'],
                'batting_score': b_batting_score,
                'bowling_score': b_bowling_score,
                'total_score': b_total,
                'avg': player_b.get('batting_average', player_b.get('runs', 0)),
                'strike_rate': player_b.get('strike_rate', 0),
                'wickets': player_b.get('wickets', 0),
                'predicted_points': player_b.get('predicted_fantasy_points', 0)
            },
            'better_player': better_player,
            'score_difference': abs(a_total - b_total)
        }
        
        return comparison


class AIInsightsGenerator:
    """Generate AI-powered insights for teams and players"""
    
    @staticmethod
    def generate_team_insights(team_df: pd.DataFrame) -> List[str]:
        """
        Generate insights for a fantasy team
        
        Args:
            team_df: DataFrame with team players
            
        Returns:
            List of insight strings
        """
        insights = []
        
        # Calculate average predicted points
        avg_points = team_df['predicted_fantasy_points'].mean()
        
        # Analyze composition
        composition = {'Batsman': 0, 'Bowler': 0, 'All-rounder': 0, 'Wicket-keeper': 0}
        for _, player in team_df.iterrows():
            role = str(player['role'])
            if 'Wicket-keeper' in role:
                composition['Wicket-keeper'] += 1
            elif 'Bowler' in role:
                composition['Bowler'] += 1
            elif 'All-rounder' in role:
                composition['All-rounder'] += 1
            else:
                composition['Batsman'] += 1
        
        # Batting strength insights
        batsmen_avg_sr = team_df[team_df['role'].str.contains('Batsman', na=False)]['strike_rate'].mean()
        if not np.isnan(batsmen_avg_sr):
            if batsmen_avg_sr > 140:
                insights.append("🔥 Explosive batting lineup with exceptional strike rate")
            elif batsmen_avg_sr > 130:
                insights.append("✅ Strong batting attack with good strike rate")
            elif batsmen_avg_sr < 120:
                insights.append("⚠️ Batting strike rate needs improvement")
        
        # Bowling strength insights
        bowlers_avg_economy = team_df[team_df['role'].str.contains('Bowler|All-rounder', na=False)]['economy'].mean()
        if not np.isnan(bowlers_avg_economy) and bowlers_avg_economy > 0:
            if bowlers_avg_economy < 7.5:
                insights.append("🎯 Excellent bowling economy - wicket-taking attack")
            elif bowlers_avg_economy < 8.5:
                insights.append("✅ Decent bowling economy")
            elif bowlers_avg_economy > 9:
                insights.append("⚠️ Bowling economy is expensive")
        
        # Team balance insights
        if composition['All-rounder'] >= 2:
            insights.append("💪 Great team balance with multiple all-rounders")
        elif composition['All-rounder'] == 1:
            insights.append("👍 Adequate all-rounder support")
        else:
            insights.append("⚠️ Lack of all-rounders may limit flexibility")
        
        # Experience insights
        avg_matches = team_df['matches'].mean()
        if avg_matches > 100:
            insights.append("🎓 Highly experienced squad - reliable under pressure")
        elif avg_matches > 60:
            insights.append("✅ Good mix of experience and youth")
        elif avg_matches < 40:
            insights.append("🌟 Young team with high potential")
        
        # Top performer insight
        top_player = team_df.loc[team_df['predicted_fantasy_points'].idxmax()]
        insights.append(f"⭐ {top_player['name']} is the key player with highest predicted points")
        
        # Team distribution
        team_counts = team_df['team'].value_counts()
        if len(team_counts) > 0:
            most_represented_team = team_counts.index[0]
            count = team_counts.iloc[0]
            if count >= 6:
                insights.append(f"🎯 Heavily stacked with players from {most_represented_team}")
        
        return insights
    
    @staticmethod
    def generate_player_insight(player: pd.Series) -> str:
        """
        Generate insight for individual player
        
        Args:
            player: Player Series
            
        Returns:
            Insight string
        """
        role = str(player['role'])
        predicted_points = player.get('predicted_fantasy_points', 0)
        strike_rate = player.get('strike_rate', 0)
        economy = player.get('economy', 10)
        wickets = player.get('wickets', 0)
        runs = player.get('runs', 0)
        
        if 'Batsman' in role:
            if strike_rate > 150:
                return f"⚡ {player['name']} is an explosive power hitter"
            elif strike_rate > 135:
                return f"✅ {player['name']} maintains excellent scoring rate"
            elif runs > 2000:
                return f"🎯 {player['name']} is a consistent run-scorer"
        
        elif 'Bowler' in role:
            if economy < 7:
                return f"🎯 {player['name']} is highly economical"
            elif wickets > 100:
                return f"💪 {player['name']} is a proven wicket-taker"
            elif economy < 8:
                return f"✅ {player['name']} bowls economically"
        
        elif 'All-rounder' in role:
            if predicted_points > 100:
                return f"🌟 {player['name']} is a premium all-rounder - must pick!"
            elif predicted_points > 70:
                return f"⭐ {player['name']} provides great dual value"
            else:
                return f"👍 {player['name']} offers useful contributions"
        
        elif 'Wicket-keeper' in role:
            if predicted_points > 80:
                return f"💎 {player['name']} is a top wicket-keeper batsman"
            else:
                return f"✅ {player['name']} is a solid keeper option"
        
        return f"👤 {player['name']} is a valuable squad member"
    
    @staticmethod
    def generate_match_insights(team_a_df: pd.DataFrame, 
                               team_b_df: pd.DataFrame) -> List[str]:
        """
        Generate insights for a match between two teams
        
        Args:
            team_a_df: Team A DataFrame
            team_b_df: Team B DataFrame
            
        Returns:
            List of match insights
        """
        insights = []
        
        # Compare average points
        avg_a = team_a_df['predicted_fantasy_points'].mean()
        avg_b = team_b_df['predicted_fantasy_points'].mean()
        
        if avg_a > avg_b * 1.1:
            insights.append("📊 Team A has higher average player quality")
        elif avg_b > avg_a * 1.1:
            insights.append("📊 Team B has higher average player quality")
        else:
            insights.append("⚖️ Both teams have similar average player quality - closely matched!")
        
        # Compare total strength
        total_a = team_a_df['predicted_fantasy_points'].sum()
        total_b = team_b_df['predicted_fantasy_points'].sum()
        
        if abs(total_a - total_b) < 50:
            insights.append("🔥 This is expected to be a very close contest!")
        
        # Top performers comparison
        top_a = team_a_df['predicted_fantasy_points'].max()
        top_b = team_b_df['predicted_fantasy_points'].max()
        
        if top_a > top_b * 1.2:
            insights.append("⭐ Team A has the standout star player")
        elif top_b > top_a * 1.2:
            insights.append("⭐ Team B has the standout star player")
        
        return insights


def format_points(points: float) -> str:
    """Format fantasy points for display"""
    return f"{points:.1f}"


def get_role_short_name(role: str) -> str:
    """Get short name for role"""
    if 'Wicket-keeper' in role:
        return "WK"
    elif 'All-rounder' in role:
        return "AR"
    elif 'Bowler' in role:
        return "BWL"
    elif 'Batsman' in role:
        return "BAT"
    return role


def validate_player_data(df: pd.DataFrame) -> bool:
    """Validate that player data has required columns"""
    required_columns = ['id', 'name', 'team', 'role', 'runs', 'wickets', 'strike_rate']
    return all(col in df.columns for col in required_columns)
