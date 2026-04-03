"""
Match Simulation and Win Probability Engine
Simulates matches multiple times and calculates win probabilities
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from typing import Dict, List, Tuple
import random


class MatchSimulator:
    """Simulate fantasy cricket matches and calculate win probabilities"""
    
    def __init__(self):
        """Initialize match simulator"""
        self.win_predictor = LogisticRegression(random_state=42)
    
    def calculate_team_strength(self, team_df: pd.DataFrame) -> float:
        """
        Calculate overall team strength score
        
        Args:
            team_df: DataFrame with team players
            
        Returns:
            Team strength score
        """
        # Weighted sum of predicted points
        total_points = team_df['predicted_fantasy_points'].sum()
        
        # Add composition bonus
        composition_bonus = 0
        role_counts = {'Batsman': 0, 'Bowler': 0, 'All-rounder': 0, 'Wicket-keeper': 0}
        
        for _, player in team_df.iterrows():
            role = str(player['role'])
            if 'Wicket-keeper' in role:
                role_counts['Wicket-keeper'] += 1
            elif 'Bowler' in role:
                role_counts['Bowler'] += 1
            elif 'All-rounder' in role:
                role_counts['All-rounder'] += 1
            else:
                role_counts['Batsman'] += 1
        
        # Bonus for balanced composition
        if role_counts['Wicket-keeper'] >= 1:
            composition_bonus += 5
        if role_counts['All-rounder'] >= 2:
            composition_bonus += 10
        if role_counts['Batsman'] >= 4 and role_counts['Bowler'] >= 4:
            composition_bonus += 15
        
        strength = total_points + composition_bonus
        
        return strength
    
    def simulate_single_match(self, 
                             team_a_df: pd.DataFrame, 
                             team_b_df: pd.DataFrame,
                             randomness_factor: float = 0.15) -> Dict:
        """
        Simulate a single match between two teams
        
        Args:
            team_a_df: Team A DataFrame
            team_b_df: Team B DataFrame
            randomness_factor: Variance factor (0.15 = ±15%)
            
        Returns:
            Dictionary with match result
        """
        # Calculate base strengths
        strength_a = self.calculate_team_strength(team_a_df)
        strength_b = self.calculate_team_strength(team_b_df)
        
        # Add randomness for realism
        random_factor_a = random.uniform(1 - randomness_factor, 1 + randomness_factor)
        random_factor_b = random.uniform(1 - randomness_factor, 1 + randomness_factor)
        
        performance_a = strength_a * random_factor_a
        performance_b = strength_b * random_factor_b
        
        # Determine winner
        winner = "Team A" if performance_a > performance_b else "Team B"
        margin = abs(performance_a - performance_b)
        
        return {
            'team_a_performance': performance_a,
            'team_b_performance': performance_b,
            'winner': winner,
            'margin': margin,
            'strength_a': strength_a,
            'strength_b': strength_b
        }
    
    def simulate_multiple_matches(self,
                                 team_a_df: pd.DataFrame,
                                 team_b_df: pd.DataFrame,
                                 n_simulations: int = 50) -> Dict:
        """
        Simulate match multiple times
        
        Args:
            team_a_df: Team A DataFrame
            team_b_df: Team B DataFrame
            n_simulations: Number of simulations to run
            
        Returns:
            Dictionary with simulation statistics
        """
        results = []
        
        for _ in range(n_simulations):
            result = self.simulate_single_match(team_a_df, team_b_df)
            results.append(result)
        
        # Calculate statistics
        team_a_wins = sum(1 for r in results if r['winner'] == 'Team A')
        team_b_wins = sum(1 for r in results if r['winner'] == 'Team B')
        
        avg_margin = np.mean([r['margin'] for r in results])
        
        simulation_stats = {
            'team_a_wins': team_a_wins,
            'team_b_wins': team_b_wins,
            'total_simulations': n_simulations,
            'team_a_win_percentage': (team_a_wins / n_simulations) * 100,
            'team_b_win_percentage': (team_b_wins / n_simulations) * 100,
            'avg_margin': avg_margin,
            'all_results': results
        }
        
        return simulation_stats
    
    def calculate_win_probability(self,
                                 team_a_df: pd.DataFrame,
                                 team_b_df: pd.DataFrame) -> Tuple[float, float]:
        """
        Calculate win probability using logistic regression
        
        Args:
            team_a_df: Team A DataFrame
            team_b_df: Team B DataFrame
            
        Returns:
            Tuple of (team_a_win_prob, team_b_win_prob)
        """
        # Calculate strengths
        strength_a = self.calculate_team_strength(team_a_df)
        strength_b = self.calculate_team_strength(team_b_df)
        
        # Strength differential
        strength_diff = strength_a - strength_b
        
        # Logistic function for probability
        # P(A wins) = 1 / (1 + e^(-diff/scale))
        scale_factor = 50  # Controls steepness of probability curve
        prob_a = 1 / (1 + np.exp(-strength_diff / scale_factor))
        prob_b = 1 - prob_a
        
        return prob_a * 100, prob_b * 100
    
    def get_detailed_analysis(self,
                             team_a_df: pd.DataFrame,
                             team_b_df: pd.DataFrame,
                             n_simulations: int = 50) -> Dict:
        """
        Get comprehensive match analysis
        
        Args:
            team_a_df: Team A DataFrame
            team_b_df: Team B DataFrame
            n_simulations: Number of simulations
            
        Returns:
            Dictionary with complete analysis
        """
        # Run simulations
        sim_stats = self.simulate_multiple_matches(team_a_df, team_b_df, n_simulations)
        
        # Calculate probabilities
        prob_a, prob_b = self.calculate_win_probability(team_a_df, team_b_df)
        
        # Get strengths
        strength_a = self.calculate_team_strength(team_a_df)
        strength_b = self.calculate_team_strength(team_b_df)
        
        # Top performers from each team
        top_a = team_a_df.nlargest(3, 'predicted_fantasy_points')['name'].tolist()
        top_b = team_b_df.nlargest(3, 'predicted_fantasy_points')['name'].tolist()
        
        analysis = {
            'simulation_results': sim_stats,
            'win_probabilities': {
                'team_a': prob_a,
                'team_b': prob_b
            },
            'team_strengths': {
                'team_a': strength_a,
                'team_b': strength_b
            },
            'top_performers': {
                'team_a': top_a,
                'team_b': top_b
            },
            'prediction_confidence': 'High' if abs(prob_a - prob_b) > 20 else 'Medium' if abs(prob_a - prob_b) > 10 else 'Low'
        }
        
        return analysis
    
    def predict_most_likely_winner(self,
                                  team_a_df: pd.DataFrame,
                                  team_b_df: pd.DataFrame,
                                  confidence_threshold: float = 60.0) -> Tuple[str, float, bool]:
        """
        Predict most likely winner with confidence
        
        Args:
            team_a_df: Team A DataFrame
            team_b_df: Team B DataFrame
            confidence_threshold: Threshold for confident prediction
            
        Returns:
            Tuple of (winner_name, confidence_percentage, is_confident)
        """
        prob_a, prob_b = self.calculate_win_probability(team_a_df, team_b_df)
        
        if prob_a >= prob_b:
            winner = "Team A"
            confidence = prob_a
        else:
            winner = "Team B"
            confidence = prob_b
        
        is_confident = confidence >= confidence_threshold
        
        return winner, confidence, is_confident
