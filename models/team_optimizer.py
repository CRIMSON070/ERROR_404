"""
Team Optimization AI Module
Deep Learning-powered team evaluation and player replacement suggestions
"""

import torch
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import os
from datetime import datetime

from models.player_value_model import PlayerValueDNN, PlayerEmbeddingNetwork


class TeamOptimizationAI:
    """
    AI-powered team optimization engine
    
    Features:
    - Player value prediction using DL
    - Cost efficiency analysis
    - Overpriced/undervalued detection
    - Replacement suggestions using embeddings
    """
    
    def __init__(self, model_path: str = "player_value_model_final.pth",
                 embedding_dim: int = 32):
        
        self.device = 'cpu'
        self.model_path = model_path
        
        # Load main model
        if os.path.exists(model_path):
            self.model = PlayerValueDNN.load_model(model_path)
        else:
            # Initialize with default architecture
            self.model = PlayerValueDNN(input_dim=50)
            print(f"⚠️ Using untrained model. Please train first or provide model path.")
        
        self.model.to(self.device)
        self.model.eval()
        
        # Embedding network for similarity
        self.embedding_net = PlayerEmbeddingNetwork(input_dim=50, embedding_dim=embedding_dim)
        
        # Cache for player embeddings
        self.player_embeddings_cache = {}
    
    def analyze_player(self, player_features: np.ndarray, 
                      sold_price: float) -> Dict[str, float]:
        """
        Analyze individual player
        
        Args:
            player_features: Feature vector (50,)
            sold_price: Actual auction price in ₹ Cr
        
        Returns:
            Dictionary with analysis results
        """
        predictions = self.model.predict(player_features)
        
        predicted_value = predictions['predicted_value']
        performance_score = predictions['performance_score']
        risk_score = predictions['risk_score']
        
        # Calculate value for money
        value_ratio = predicted_value / (sold_price + 0.1)
        
        # Determine status
        if value_ratio > 1.2:
            status = "undervalued"
            color_code = "🟢"
        elif value_ratio < 0.8:
            status = "overpriced"
            color_code = "🔴"
        else:
            status = "fair_value"
            color_code = "🟡"
        
        return {
            'predicted_value': float(predicted_value),
            'performance_score': float(performance_score),
            'risk_score': float(risk_score),
            'actual_price': float(sold_price),
            'value_ratio': float(value_ratio),
            'status': status,
            'color_code': color_code,
            'surplus_value': float(predicted_value - sold_price)
        }
    
    def analyze_team(self, team_data: pd.DataFrame) -> Dict:
        """
        Analyze complete team
        
        Args:
            team_data: DataFrame with columns:
                      - player_name
                      - role
                      - sold_price
                      - features (numpy array)
        
        Returns:
            Complete team analysis
        """
        players_analysis = []
        total_predicted_value = 0.0
        total_actual_cost = 0.0
        total_performance = 0.0
        total_risk = 0.0
        
        overpriced_players = []
        undervalued_players = []
        
        for idx, row in team_data.iterrows():
            player_name = row.get('player_name', f'Player_{idx}')
            sold_price = row.get('sold_price', 1.0)
            features = row.get('features', np.random.randn(50))
            
            # Analyze player
            analysis = self.analyze_player(features, sold_price)
            analysis['player_name'] = player_name
            analysis['role'] = row.get('role', 'Unknown')
            
            players_analysis.append(analysis)
            
            # Accumulate metrics
            total_predicted_value += analysis['predicted_value']
            total_actual_cost += sold_price
            total_performance += analysis['performance_score']
            total_risk += analysis['risk_score']
            
            # Categorize
            if analysis['status'] == 'overpriced':
                overpriced_players.append(analysis)
            elif analysis['status'] == 'undervalued':
                undervalued_players.append(analysis)
        
        n_players = len(team_data)
        
        # Calculate team efficiency
        efficiency_score = total_predicted_value / (total_actual_cost + 0.1)
        
        # Sort players by value surplus
        players_analysis.sort(key=lambda x: x['surplus_value'], reverse=True)
        
        return {
            'team_size': n_players,
            'total_budget_spent': float(total_actual_cost),
            'total_predicted_value': float(total_predicted_value),
            'budget_limit': 120.0,
            'efficiency_score': float(efficiency_score),
            'average_performance': float(total_performance / n_players),
            'average_risk': float(total_risk / n_players),
            'overpriced_count': len(overpriced_players),
            'undervalued_count': len(undervalued_players),
            'overpriced_players': overpriced_players,
            'undervalued_players': undervalued_players,
            'all_players': players_analysis,
            'team_composition': self._analyze_composition(team_data),
            'recommendations': self._generate_recommendations(
                efficiency_score, overpriced_players, undervalued_players
            )
        }
    
    def _analyze_composition(self, team_data: pd.DataFrame) -> Dict:
        """Analyze team composition by role"""
        role_counts = team_data['role'].value_counts().to_dict()
        
        return {
            'wicket_keepers': role_counts.get('Wicket-keeper', 0),
            'batsmen': role_counts.get('Batsman', 0),
            'all_rounders': role_counts.get('All-rounder', 0),
            'bowlers': role_counts.get('Bowler', 0),
            'total': len(team_data)
        }
    
    def _generate_recommendations(self, efficiency: float,
                                  overpriced: List[Dict],
                                  undervalued: List[Dict]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if efficiency < 0.7:
            recommendations.append("🔴 Critical: Team efficiency is very low. Consider major changes.")
        elif efficiency < 0.9:
            recommendations.append("🟡 Team efficiency is below optimal. Review overpriced players.")
        else:
            recommendations.append("🟢 Good team efficiency! Well-balanced squad.")
        
        if len(overpriced) > 3:
            recommendations.append(f"⚠️ You have {len(overpriced)} overpriced players. Consider replacements.")
        
        if len(undervalued) > 2:
            recommendations.append(f"✅ Great value picks! {len(undervalued)} undervalued players found.")
        
        return recommendations
    
    def find_replacement_suggestions(self, player_to_replace: str,
                                     team_data: pd.DataFrame,
                                     player_pool: pd.DataFrame,
                                     top_k: int = 3) -> List[Dict]:
        """
        Find better replacement options for a player
        
        Args:
            player_to_replace: Name of player to replace
            team_data: Current team DataFrame
            player_pool: Available players DataFrame
            top_k: Number of suggestions
        
        Returns:
            List of replacement suggestions
        """
        # Find current player
        current_player = team_data[team_data['player_name'] == player_to_replace]
        
        if len(current_player) == 0:
            return []
        
        current_row = current_player.iloc[0]
        current_price = current_row.get('sold_price', 0)
        current_role = current_row.get('role', '')
        current_features = current_row.get('features', np.random.randn(50))
        
        # Generate embedding for current player
        with torch.no_grad():
            current_embedding = self.embedding_net(
                torch.FloatTensor(current_features).unsqueeze(0)
            ).numpy().flatten()
        
        # Find similar players from pool
        suggestions = []
        
        for idx, pool_row in player_pool.iterrows():
            pool_name = pool_row.get('player_name', '')
            pool_price = pool_row.get('sold_price', 0)
            pool_role = pool_row.get('role', '')
            
            # Skip if same player or already in team
            if pool_name == player_to_replace:
                continue
            
            if pool_name in team_data['player_name'].values:
                continue
            
            # Check role compatibility
            if pool_role != current_role:
                continue
            
            # Get features and generate embedding
            pool_features = pool_row.get('features', np.random.randn(50))
            
            with torch.no_grad():
                pool_embedding = self.embedding_net(
                    torch.FloatTensor(pool_features).unsqueeze(0)
                ).numpy().flatten()
            
            # Compute similarity
            similarity = np.dot(current_embedding, pool_embedding)
            
            # Analyze value
            pool_analysis = self.analyze_player(pool_features, pool_price)
            
            # Only suggest if better value or lower price
            if (pool_price < current_price * 0.9 or 
                pool_analysis['predicted_value'] > current_price):
                
                reason = []
                if pool_price < current_price * 0.8:
                    reason.append(f"₹{current_price - pool_price:.2f}Cr cheaper")
                if pool_analysis['predicted_value'] > current_price:
                    reason.append("Higher predicted value")
                if pool_analysis['risk_score'] < 0.4:
                    reason.append("Lower risk")
                
                suggestions.append({
                    'suggested_player': pool_name,
                    'role': pool_role,
                    'predicted_price': float(pool_price),
                    'predicted_value': pool_analysis['predicted_value'],
                    'similarity_score': float(similarity),
                    'reason': ', '.join(reason) if reason else "Better overall value",
                    'performance_score': pool_analysis['performance_score'],
                    'risk_score': pool_analysis['risk_score']
                })
        
        # Sort by similarity and value
        suggestions.sort(key=lambda x: (x['similarity_score'], x['predicted_value']), reverse=True)
        
        return suggestions[:top_k]
    
    def get_optimization_report(self, team_data: pd.DataFrame,
                               player_pool: pd.DataFrame) -> Dict:
        """
        Generate comprehensive optimization report
        
        Args:
            team_data: Current team
            player_pool: Available players
        
        Returns:
            Complete optimization report
        """
        # Analyze team
        team_analysis = self.analyze_team(team_data)
        
        # Find replacement opportunities
        replacement_opportunities = []
        
        # Focus on overpriced players
        for overpriced_player in team_analysis['overpriced_players'][:3]:
            player_name = overpriced_player['player_name']
            
            replacements = self.find_replacement_suggestions(
                player_name, team_data, player_pool, top_k=2
            )
            
            if replacements:
                replacement_opportunities.append({
                    'replace_player': player_name,
                    'reason': overpriced_player['status'],
                    'suggestions': replacements
                })
        
        team_analysis['replacement_opportunities'] = replacement_opportunities
        
        # Add timestamp
        team_analysis['generated_at'] = datetime.now().isoformat()
        
        return team_analysis


# Example usage
if __name__ == "__main__":
    # Initialize optimizer
    optimizer = TeamOptimizationAI(model_path="player_value_model_final.pth")
    
    # Create dummy team data
    team_data = pd.DataFrame({
        'player_name': [f'Player_{i}' for i in range(15)],
        'role': np.random.choice(['Batsman', 'Bowler', 'All-rounder', 'Wicket-keeper'], 15),
        'sold_price': np.random.uniform(1, 20, 15),
        'features': [np.random.randn(50) for _ in range(15)]
    })
    
    # Analyze team
    report = optimizer.get_optimization_report(team_data, team_data)
    
    print(f"\n📊 Team Optimization Report")
    print(f"   Efficiency Score: {report['efficiency_score']:.2f}")
    print(f"   Total Value: ₹{report['total_predicted_value']:.2f} Cr")
    print(f"   Total Cost: ₹{report['total_budget_spent']:.2f} Cr")
    print(f"   Overpriced Players: {report['overpriced_count']}")
    print(f"   Undervalued Players: {report['undervalued_count']}")
    
    print(f"\n✅ Analysis complete!")
