"""
Team Optimization Engine
Uses ML predictions to generate optimal fantasy teams with constraints
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from itertools import combinations


class TeamOptimizer:
    """Generate optimal fantasy cricket teams using AI/ML"""
    
    def __init__(self):
        """Initialize team optimizer"""
        self.team_constraints = {
            'total_players': 11,
            'max_from_one_team': 7,
            'min_batsmen': 3,
            'min_bowlers': 3,
            'min_allrounders': 1,
            'min_wicketkeeper': 1
        }
    
    def generate_optimal_team(self, 
                             df: pd.DataFrame, 
                             predicted_points: np.ndarray,
                             constraints: Optional[Dict] = None) -> pd.DataFrame:
        """
        Generate optimal playing 11 based on predicted points
        
        Args:
            df: DataFrame with player data
            predicted_points: Array of predicted fantasy points
            constraints: Custom constraints (optional)
            
        Returns:
            DataFrame with optimal team
        """
        # Apply custom constraints if provided
        if constraints:
            self.team_constraints.update(constraints)
        
        # Add predictions to dataframe
        result_df = df.copy()
        result_df['predicted_fantasy_points'] = predicted_points
        
        # Sort by predicted points (descending)
        result_df = result_df.sort_values('predicted_fantasy_points', ascending=False)
        
        # Initialize team
        optimal_team = []
        team_counts = {}  # Track players from each real team
        role_counts = {'Batsman': 0, 'Bowler': 0, 'All-rounder': 0, 'Wicket-keeper': 0}
        
        # First pass: Ensure role diversity
        for role_priority in ['Wicket-keeper', 'All-rounder', 'Bowler', 'Batsman']:
            candidates = result_df[
                result_df['role'].str.contains(role_priority, case=False, na=False)
            ]
            
            for _, player in candidates.iterrows():
                if len(optimal_team) >= self.team_constraints['total_players']:
                    break
                
                # Check constraints
                player_team = player['team']
                current_team_count = team_counts.get(player_team, 0)
                
                # Skip if max from one team exceeded
                if current_team_count >= self.team_constraints['max_from_one_team']:
                    continue
                
                # Skip if already selected
                if player['id'] in [p['id'] for p in optimal_team]:
                    continue
                
                # Add player
                optimal_team.append(player.to_dict())
                team_counts[player_team] = current_team_count + 1
                
                # Update role count
                if 'Wicket-keeper' in str(player['role']):
                    role_counts['Wicket-keeper'] += 1
                elif 'Bowler' in str(player['role']):
                    role_counts['Bowler'] += 1
                elif 'All-rounder' in str(player['role']):
                    role_counts['All-rounder'] += 1
                else:
                    role_counts['Batsman'] += 1
        
        # Second pass: Fill remaining spots with best available
        for _, player in result_df.iterrows():
            if len(optimal_team) >= self.team_constraints['total_players']:
                break
            
            player_team = player['team']
            current_team_count = team_counts.get(player_team, 0)
            
            if current_team_count >= self.team_constraints['max_from_one_team']:
                continue
            
            if player['id'] in [p['id'] for p in optimal_team]:
                continue
            
            optimal_team.append(player.to_dict())
            team_counts[player_team] = current_team_count + 1
        
        # Convert to DataFrame
        optimal_team_df = pd.DataFrame(optimal_team)
        
        return optimal_team_df
    
    def select_captain_vice_captain(self, team_df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """
        Select captain and vice-captain based on predicted points
        
        Args:
            team_df: DataFrame with selected team
            
        Returns:
            Tuple of (captain, vice_captain) Series
        """
        # Sort by predicted points
        sorted_team = team_df.sort_values('predicted_fantasy_points', ascending=False)
        
        # Captain: Highest predicted points (2x multiplier)
        captain = sorted_team.iloc[0]
        
        # Vice-captain: Second highest (1.5x multiplier)
        vice_captain = sorted_team.iloc[1]
        
        return captain, vice_captain
    
    def calculate_team_score(self, 
                            team_df: pd.DataFrame, 
                            captain_id: str, 
                            vice_captain_id: str) -> float:
        """
        Calculate total fantasy team score with captain multipliers
        
        Args:
            team_df: DataFrame with team players
            captain_id: ID of captain
            vice_captain_id: ID of vice-captain
            
        Returns:
            Total team fantasy score
        """
        total_score = 0.0
        
        for _, player in team_df.iterrows():
            points = player['predicted_fantasy_points']
            
            if player['id'] == captain_id:
                points *= 2.0  # Captain gets 2x
            elif player['id'] == vice_captain_id:
                points *= 1.5  # Vice-captain gets 1.5x
            
            total_score += points
        
        return total_score
    
    def get_team_composition(self, team_df: pd.DataFrame) -> Dict[str, int]:
        """
        Get team composition breakdown
        
        Args:
            team_df: DataFrame with team
            
        Returns:
            Dictionary with role counts
        """
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
        
        return composition
    
    def validate_team(self, team_df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate team against constraints
        
        Args:
            team_df: DataFrame with team
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check total players
        if len(team_df) != self.team_constraints['total_players']:
            issues.append(f"Need exactly {self.team_constraints['total_players']} players, got {len(team_df)}")
        
        # Check team distribution
        team_counts = team_df['team'].value_counts()
        for team, count in team_counts.items():
            if count > self.team_constraints['max_from_one_team']:
                issues.append(f"Max {self.team_constraints['max_from_one_team']} players from {team}, got {count}")
        
        # Check role requirements
        composition = self.get_team_composition(team_df)
        
        if composition['Batsman'] < self.team_constraints['min_batsmen']:
            issues.append(f"Need at least {self.team_constraints['min_batsmen']} batsmen")
        
        if composition['Bowler'] < self.team_constraints['min_bowlers']:
            issues.append(f"Need at least {self.team_constraints['min_bowlers']} bowlers")
        
        if composition['All-rounder'] < self.team_constraints['min_allrounders']:
            issues.append(f"Need at least {self.team_constraints['min_allrounders']} all-rounders")
        
        if composition['Wicket-keeper'] < self.team_constraints['min_wicketkeeper']:
            issues.append(f"Need at least {self.team_constraints['min_wicketkeeper']} wicket-keeper")
        
        is_valid = len(issues) == 0
        return is_valid, issues
    
    def compare_two_teams(self, 
                         team_a_df: pd.DataFrame, 
                         team_b_df: pd.DataFrame) -> Dict:
        """
        Compare two fantasy teams
        
        Args:
            team_a_df: First team DataFrame
            team_b_df: Second team DataFrame
            
        Returns:
            Dictionary with comparison results
        """
        # Calculate scores
        captain_a, vc_a = self.select_captain_vice_captain(team_a_df)
        captain_b, vc_b = self.select_captain_vice_captain(team_b_df)
        
        score_a = self.calculate_team_score(team_a_df, captain_a['id'], vc_a['id'])
        score_b = self.calculate_team_score(team_b_df, captain_b['id'], vc_b['id'])
        
        # Get compositions
        comp_a = self.get_team_composition(team_a_df)
        comp_b = self.get_team_composition(team_b_df)
        
        # Average predicted points
        avg_a = team_a_df['predicted_fantasy_points'].mean()
        avg_b = team_b_df['predicted_fantasy_points'].mean()
        
        comparison = {
            'team_a': {
                'total_score': score_a,
                'avg_points': avg_a,
                'composition': comp_a,
                'captain': captain_a['name'],
                'vice_captain': vc_a['name']
            },
            'team_b': {
                'total_score': score_b,
                'avg_points': avg_b,
                'composition': comp_b,
                'captain': captain_b['name'],
                'vice_captain': vc_b['name']
            },
            'stronger_team': 'Team A' if score_a > score_b else 'Team B',
            'score_difference': abs(score_a - score_b)
        }
        
        return comparison
