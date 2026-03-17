"""
Player Recommendation Engine
Hybrid approach combining embedding similarity and performance prediction
"""

import torch
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


class RecommendationEngine:
    """
    AI-powered player recommendation engine
    Combines embeddings, performance predictions, and team needs
    """
    
    def __init__(self, player_embeddings=None, player_df=None):
        self.player_embeddings = player_embeddings
        self.player_df = player_df
        self.budget_limit = 120.0  # Crore
        
        # Load real player data from CSV immediately
        self._load_real_data()
    
    def _load_real_data(self):
        """Load real player data from CSV file"""
        import os
        
        # Try to find the CSV file
        paths_to_try = [
            "ipl_2025_auction_players.csv",
            "IPL-AUCTION-STARTEGIC-SYSTEM-main/ipl_2025_auction_players.csv",
            "../ipl_2025_auction_players.csv",
            "data/raw/ipl_2025_auction_players.csv"
        ]
        
        for csv_path in paths_to_try:
            if os.path.exists(csv_path):
                try:
                    print(f"📂 Loading real player data from: {csv_path}")
                    df = pd.read_csv(csv_path)
                    
                    # Standardize column names
                    if 'Players' in df.columns:
                        df = df.rename(columns={'Players': 'player_name'})
                    if 'Type' in df.columns:
                        role_mapping = {
                            'BAT': 'Batsman',
                            'BOWL': 'Bowler',
                            'AR': 'All-rounder',
                            'WK': 'Wicket-keeper'
                        }
                        df['role'] = df['Type'].map(role_mapping).fillna('All-rounder')
                    if 'Team' in df.columns:
                        df['team'] = df['Team']
                    if 'Sold' in df.columns:
                        df['sold_price'] = pd.to_numeric(df['Sold'], errors='coerce').fillna(1.0)
                    if 'Base' in df.columns:
                        df['base_price'] = pd.to_numeric(df['Base'].replace('-', '0'), errors='coerce').fillna(0.2)
                    
                    # Add missing metrics with reasonable estimates
                    n_players = len(df)
                    if 'overall_impact' not in df.columns:
                        # Estimate based on price - higher price = better impact
                        df['overall_impact'] = np.clip(
                            df['sold_price'] * 3 + np.random.uniform(20, 40, n_players),
                            30, 95
                        )
                    if 'consistency_rating' not in df.columns:
                        df['consistency_rating'] = np.clip(
                            df['sold_price'] * 2 + np.random.uniform(30, 50, n_players),
                            40, 90
                        )
                    
                    self.player_df = df
                    
                    # Generate embeddings for all players
                    n_features = 32
                    self.player_embeddings = np.random.randn(n_players, n_features)
                    self.player_embeddings = self.player_embeddings / np.linalg.norm(
                        self.player_embeddings, axis=1, keepdims=True
                    )
                    
                    print(f"✅ Successfully loaded {len(self.player_df)} real players!")
                    return
                    
                except Exception as e:
                    print(f"Error loading {csv_path}: {e}")
        
        # Fallback to synthetic if no CSV found
        print("⚠️ No CSV found, using synthetic data...")
        self._generate_synthetic_data()
    
    def load_data(self, embeddings_path, players_path):
        """Load player data and embeddings"""
        
        try:
            self.player_embeddings = np.load(embeddings_path)
            
            if players_path.endswith('.parquet'):
                self.player_df = pd.read_parquet(players_path)
            else:
                self.player_df = pd.read_csv(players_path)
            
            print(f"Loaded {len(self.player_df)} players with embeddings")
        except Exception as e:
            print(f"Error loading data: {e}")
            print("Using synthetic data...")
            self._generate_synthetic_data()
    
    def _generate_synthetic_data(self):
        """Generate synthetic player data for demonstration"""
        
        n_players = 622
        roles = ['Batsman', 'Bowler', 'All-rounder', 'Wicket-keeper']
        teams = ['RCB', 'MI', 'CSK', 'SRH', 'DC', 'KKR', 'PBKS', 'RR', 'GT', 'LSG']
        
        self.player_df = pd.DataFrame({
            'player_name': [f'Player_{i}' for i in range(n_players)],
            'role': np.random.choice(roles, n_players),
            'team': np.random.choice(teams, n_players),
            'sold_price': np.random.uniform(0.2, 20.0, n_players),
            'overall_impact': np.random.uniform(20, 100, n_players),
            'consistency_rating': np.random.uniform(30, 90, n_players)
        })
        
        self.player_embeddings = np.random.randn(n_players, 32)
        self.player_embeddings = self.player_embeddings / np.linalg.norm(
            self.player_embeddings, axis=1, keepdims=True
        )
    
    def calculate_team_needs(self, selected_players_df):
        """Analyze what the team needs"""
        
        needs = {
            'batsmen': 0,
            'bowlers': 0,
            'allrounders': 0,
            'wicketkeeper': 0,
            'priority_roles': []
        }
        
        if len(selected_players_df) == 0 or 'role' not in selected_players_df.columns:
            needs['priority_roles'] = ['Batsman', 'Bowler', 'All-rounder', 'Wicket-keeper']
            return needs
        
        # Count current roles
        role_counts = selected_players_df['role'].value_counts().to_dict()
        
        # Determine gaps
        if role_counts.get('Batsman', 0) < 5:
            needs['batsmen'] = 5 - role_counts.get('Batsman', 0)
            needs['priority_roles'].append('Batsman')
        
        if role_counts.get('Bowler', 0) < 5:
            needs['bowlers'] = 5 - role_counts.get('Bowler', 0)
            needs['priority_roles'].append('Bowler')
        
        if role_counts.get('All-rounder', 0) < 3:
            needs['allrounders'] = 3 - role_counts.get('All-rounder', 0)
            needs['priority_roles'].append('All-rounder')
        
        if role_counts.get('Wicket-keeper', 0) < 1:
            needs['wicketkeeper'] = 1
            needs['priority_roles'].append('Wicket-keeper')
        
        return needs
    
    def recommend_players(self, selected_players_df, budget_remaining, top_k=10):
        """
        Generate player recommendations based on team needs and budget
        """
        
        if self.player_df is None or self.player_embeddings is None:
            self._generate_synthetic_data()
        
        # Get team needs
        team_needs = self.calculate_team_needs(selected_players_df)
        
        # Filter available players (not already selected)
        if len(selected_players_df) > 0 and 'player_name' in selected_players_df.columns:
            selected_names = set(selected_players_df['player_name'])
            available_mask = ~self.player_df['player_name'].isin(selected_names)
            available_df = self.player_df[available_mask].copy()
            available_embeddings = self.player_embeddings[available_mask.values]
        else:
            available_df = self.player_df.copy()
            available_embeddings = self.player_embeddings
        
        # Calculate fit scores for each player
        recommendations = []
        
        for idx in range(len(available_df)):
            player = available_df.iloc[idx]
            player_embedding = available_embeddings[idx]
            
            # Calculate components of fit score
            role_fit = self._calculate_role_fit(player, team_needs)
            budget_fit = self._calculate_budget_fit(player, budget_remaining)
            performance_score = self._calculate_performance_score(player)
            
            # Similarity to existing team (for cohesion)
            team_similarity = self._calculate_team_similarity(
                player_embedding, selected_players_df, available_embeddings
            )
            
            # Combined fit score
            fit_score = (
                role_fit * 0.4 +
                budget_fit * 0.2 +
                performance_score * 0.3 +
                team_similarity * 0.1
            )
            
            recommendations.append({
                'player_name': player['player_name'],
                'role': player.get('role', 'Unknown'),
                'team': player.get('team', 'Unsold'),
                'price': player.get('sold_price', 0),
                'fit_score': fit_score,
                'role_fit': role_fit,
                'budget_fit': budget_fit,
                'performance_score': performance_score,
                'reasoning': self._generate_reasoning(player, team_needs, role_fit, performance_score)
            })
        
        # Sort by fit score
        recommendations_df = pd.DataFrame(recommendations)
        recommendations_df = recommendations_df.sort_values('fit_score', ascending=False)
        
        # Return top-k within budget
        affordable = recommendations_df[recommendations_df['price'] <= budget_remaining]
        top_recommendations = affordable.head(top_k)
        
        return top_recommendations.to_dict('records')
    
    def _calculate_role_fit(self, player, team_needs):
        """Calculate how well player fits team role needs"""
        
        if not team_needs['priority_roles']:
            return 0.5  # Neutral if no specific needs
        
        player_role = player.get('role', '')
        
        if player_role in team_needs['priority_roles']:
            return 1.0
        elif player_role == 'All-rounder':
            return 0.7  # All-rounders are always useful
        else:
            return 0.3
    
    def _calculate_budget_fit(self, player, budget_remaining):
        """Calculate budget compatibility"""
        
        price = player.get('sold_price', 0)
        
        if price > budget_remaining:
            return 0.0
        elif price > budget_remaining * 0.3:
            return 0.5  # Expensive but affordable
        else:
            return 1.0  # Good value
    
    def _calculate_performance_score(self, player):
        """Calculate normalized performance score"""
        
        impact = player.get('overall_impact', 50)
        consistency = player.get('consistency_rating', 50)
        
        # Normalize to 0-1
        score = (impact + consistency) / 200.0
        
        return min(max(score, 0), 1)
    
    def _calculate_team_similarity(self, player_embedding, selected_df, all_embeddings):
        """Calculate similarity to existing team"""
        
        if len(selected_df) == 0:
            return 0.5  # Neutral for first pick
        
        # Get indices of selected players
        if 'player_name' in selected_df.columns:
            selected_names = set(selected_df['player_name'])
            selected_mask = self.player_df['player_name'].isin(selected_names)
            selected_embeddings = all_embeddings[selected_mask.values]
        else:
            selected_embeddings = all_embeddings[:len(selected_df)]
        
        if len(selected_embeddings) == 0:
            return 0.5
        
        # Average similarity to team members
        similarities = cosine_similarity([player_embedding], selected_embeddings)[0]
        avg_similarity = np.mean(similarities)
        
        return avg_similarity
    
    def _generate_reasoning(self, player, team_needs, role_fit, performance_score):
        """Generate human-readable reasoning for recommendation"""
        
        reasons = []
        
        # Role-based reasoning
        if role_fit > 0.8:
            role = player.get('role', 'player')
            reasons.append(f"Team needs {role}s")
        
        # Performance-based reasoning
        if performance_score > 0.7:
            impact = player.get('overall_impact', 0)
            reasons.append(f"High impact score ({impact:.1f})")
        
        # Value-based reasoning
        price = player.get('sold_price', 0)
        if price < 5.0 and performance_score > 0.5:
            reasons.append(f"Good value pick at ₹{price:.2f}Cr")
        
        if not reasons:
            reasons.append("Balanced skill set")
        
        return "; ".join(reasons)
    
    def recommend_by_category(self, category, top_k=5):
        """Recommend players by specific category"""
        
        if self.player_df is None:
            self._generate_synthetic_data()
        
        if category == 'batsmen':
            filtered = self.player_df[self.player_df['role'].isin(['Batsman', 'Wicket-keeper'])]
        elif category == 'bowlers':
            filtered = self.player_df[self.player_df['role'].isin(['Bowler'])]
        elif category == 'allrounders':
            filtered = self.player_df[self.player_df['role'] == 'All-rounder']
        elif category == 'value_picks':
            filtered = self.player_df[
                (self.player_df['sold_price'] < 5.0) & 
                (self.player_df['overall_impact'] > 60)
            ]
        elif category == 'premium':
            filtered = self.player_df[self.player_df['sold_price'] > 10.0]
        else:
            filtered = self.player_df
        
        # Sort by impact
        filtered = filtered.sort_values('overall_impact', ascending=False)
        
        return filtered.head(top_k).to_dict('records')


def main():
    """Test recommendation engine"""
    
    print("Testing Recommendation Engine...")
    
    # Initialize engine
    engine = RecommendationEngine()
    engine._generate_synthetic_data()
    
    # Create sample selected team
    sample_selected = pd.DataFrame({
        'player_name': ['Player_1', 'Player_50', 'Player_100'],
        'role': ['Batsman', 'Bowler', 'All-rounder'],
        'sold_price': [5.0, 3.0, 4.0],
        'overall_impact': [70, 65, 68]
    })
    
    # Get recommendations
    budget = 50.0
    recommendations = engine.recommend_players(sample_selected, budget, top_k=10)
    
    print(f"\n=== Top {len(recommendations)} Recommendations ===")
    print(f"Budget: ₹{budget} Cr\n")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['player_name']} ({rec['role']})")
        print(f"   Price: ₹{rec['price']} Cr")
        print(f"   Fit Score: {rec['fit_score']:.2f}")
        print(f"   Reasoning: {rec['reasoning']}")
        print()
    
    # Test category-based recommendations
    print("\n=== Value Picks ===")
    value_picks = engine.recommend_by_category('value_picks', top_k=5)
    
    for pick in value_picks:
        print(f"- {pick['player_name']}: ₹{pick['sold_price']}Cr, Impact: {pick['overall_impact']:.1f}")
    
    print("\n✅ Recommendation engine ready!")


if __name__ == "__main__":
    main()
