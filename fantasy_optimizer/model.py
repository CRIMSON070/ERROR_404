"""
Data Loading Module for Fantasy Cricket Team Optimizer
Handles loading and preprocessing of IPL player data
"""

import json
import pandas as pd
from typing import Dict, List, Optional
import os


class DataLoader:
    """Load and preprocess IPL cricket data from JSON files"""
    
    def __init__(self, data_dir: str = '../data'):
        """
        Initialize DataLoader
        
        Args:
            data_dir: Directory containing dataset files
        """
        self.data_dir = data_dir
        self.players_data = None
        self.analytics_data = None
    
    def load_ipl_complete_data(self, filename: str = 'ipl_2025_complete.json') -> pd.DataFrame:
        """
        Load complete IPL player dataset
        
        Args:
            filename: Name of JSON file
            
        Returns:
            DataFrame with player data
        """
        possible_paths = [
            os.path.join(self.data_dir, 'processed', filename),
            os.path.join(self.data_dir, filename),
            os.path.join('data', 'processed', filename),
            os.path.join('data', filename),
            filename
        ]
        
        for path in possible_paths:
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                
                if 'players' in data:
                    self.players_data = pd.DataFrame(data['players'])
                else:
                    self.players_data = pd.DataFrame(data)
                
                print(f"✅ Loaded {len(self.players_data)} players from {path}")
                return self.players_data
                
            except FileNotFoundError:
                continue
            except Exception as e:
                print(f"Error loading {path}: {e}")
                continue
        
        raise FileNotFoundError(f"Could not find {filename} in any expected location")
    
    def load_advanced_analytics(self, filename: str = 'advanced_ipl_analytics.json') -> Optional[Dict]:
        """
        Load advanced analytics data
        
        Args:
            filename: Name of analytics JSON file
            
        Returns:
            Dictionary with analytics data
        """
        possible_paths = [
            os.path.join(self.data_dir, 'analytics', filename),
            os.path.join('data', 'analytics', filename),
            filename
        ]
        
        for path in possible_paths:
            try:
                with open(path, 'r') as f:
                    self.analytics_data = json.load(f)
                print(f"✅ Loaded analytics from {path}")
                return self.analytics_data
            except FileNotFoundError:
                continue
            except Exception as e:
                print(f"Error loading {path}: {e}")
                continue
        
        print("⚠️ Advanced analytics not found, continuing without it")
        return None
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for ML model
        
        Args:
            df: Raw player DataFrame
            
        Returns:
            DataFrame with engineered features
        """
        feature_df = df.copy()
        
        # Fill missing values
        feature_df['runs'] = feature_df.get('runs', 0).fillna(0)
        feature_df['wickets'] = feature_df.get('wickets', 0).fillna(0)
        feature_df['strike_rate'] = feature_df.get('strike_rate', 0).fillna(0)
        feature_df['economy'] = feature_df.get('economy', 0).fillna(0)
        feature_df['matches'] = feature_df.get('matches', 0).fillna(0)
        
        # Calculate batting average (if not present)
        if 'batting_average' not in feature_df.columns:
            innings = feature_df.get('innings', feature_df['matches'])
            feature_df['batting_average'] = feature_df['runs'] / innings.replace(0, 1)
        
        # Calculate fantasy points (target variable)
        # Formula: Runs/2 + Wickets*25 + StrikeRate/10 - Economy*5
        feature_df['fantasy_points'] = (
            feature_df['runs'] / 2 +
            feature_df['wickets'] * 25 +
            feature_df['strike_rate'] / 10 -
            feature_df['economy'] * 5
        ).clip(lower=0)
        
        # Create role-based encoding
        feature_df['is_batsman'] = feature_df['role'].apply(lambda x: 1 if 'Batsman' in str(x) else 0)
        feature_df['is_bowler'] = feature_df['role'].apply(lambda x: 1 if 'Bowler' in str(x) else 0)
        feature_df['is_allrounder'] = feature_df['role'].apply(lambda x: 1 if 'All-rounder' in str(x) else 0)
        
        # Add experience metric
        feature_df['experience'] = feature_df['matches'] / 100.0  # Normalize
        
        # Add value metric
        feature_df['value_rating'] = feature_df.get('value_score', feature_df['fantasy_points'] / 10)
        
        return feature_df
    
    def get_feature_columns(self) -> List[str]:
        """
        Get list of feature columns for ML model
        
        Returns:
            List of column names
        """
        return [
            'batting_average',
            'strike_rate',
            'wickets',
            'matches',
            'is_batsman',
            'is_bowler',
            'is_allrounder',
            'experience',
            'value_rating'
        ]
    
    def get_teams_list(self) -> List[str]:
        """
        Get list of unique teams
        
        Returns:
            List of team names
        """
        if self.players_data is None:
            return []
        return sorted(self.players_data['team'].unique().tolist())
    
    def get_players_by_team(self, team_name: str) -> pd.DataFrame:
        """
        Get all players from a specific team
        
        Args:
            team_name: Name of the team
            
        Returns:
            DataFrame with team players
        """
        if self.players_data is None:
            return pd.DataFrame()
        
        return self.players_data[self.players_data['team'] == team_name].copy()
    
    def get_player_by_name(self, player_name: str) -> Optional[pd.Series]:
        """
        Get player details by name
        
        Args:
            player_name: Name of the player
            
        Returns:
            Series with player data or None
        """
        if self.players_data is None:
            return None
        
        matches = self.players_data[self.players_data['name'] == player_name]
        if len(matches) > 0:
            return matches.iloc[0]
        return None
