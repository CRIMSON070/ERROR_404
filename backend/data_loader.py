"""
Data loading and caching utilities
"""

import os
import pandas as pd
import numpy as np
from typing import Optional, Dict, List
from loguru import logger
from functools import lru_cache


class DataLoader:
    """Efficient data loading with caching"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.cache: Dict[str, pd.DataFrame] = {}
        self.cache_ttl: Dict[str, float] = {}
        
        logger.info(f"DataLoader initialized with directory: {data_dir}")
    
    def load_parquet(self, path: str, use_cache: bool = True) -> Optional[pd.DataFrame]:
        """Load Parquet file with optional caching"""
        
        if use_cache and path in self.cache:
            # Check cache TTL (5 minutes)
            if path in self.cache_ttl:
                import time
                if time.time() - self.cache_ttl[path] < 300:
                    logger.debug(f"Cache hit for {path}")
                    return self.cache[path]
        
        try:
            logger.info(f"Loading data from {path}...")
            
            if os.path.exists(path):
                df = pd.read_parquet(path)
                self.cache[path] = df
                
                import time
                self.cache_ttl[path] = time.time()
                
                logger.info(f"Loaded {len(df)} records from {path}")
                return df
            else:
                logger.warning(f"Path not found: {path}")
                return None
        
        except Exception as e:
            logger.error(f"Error loading parquet from {path}: {e}")
            return None
    
    def load_csv(self, path: str, use_cache: bool = True) -> Optional[pd.DataFrame]:
        """Load CSV file with optional caching"""
        
        if use_cache and path in self.cache:
            import time
            if path in self.cache_ttl:
                if time.time() - self.cache_ttl[path] < 300:
                    logger.debug(f"Cache hit for {path}")
                    return self.cache[path]
        
        try:
            logger.info(f"Loading CSV from {path}...")
            
            if os.path.exists(path):
                df = pd.read_csv(path)
                self.cache[path] = df
                
                import time
                self.cache_ttl[path] = time.time()
                
                logger.info(f"Loaded {len(df)} records from {path}")
                return df
            else:
                logger.warning(f"CSV not found: {path}")
                return None
        
        except Exception as e:
            logger.error(f"Error loading CSV from {path}: {e}")
            return None
    
    def get_all_players(self) -> Optional[pd.DataFrame]:
        """Get all players from processed data"""
        
        # Get the directory where this file is located (backend dir)
        import os
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(backend_dir)
        
        # Try multiple paths - check both root and subdirectory
        paths_to_try = [
            os.path.join(project_root, "ipl_2025_auction_players.csv"),
            os.path.join(project_root, "IPL-AUCTION-STARTEGIC-SYSTEM-main", "ipl_2025_auction_players.csv"),
            os.path.join(project_root, "data", "raw", "ipl_2025_auction_players.csv"),
            os.path.join(project_root, "data", "features", "engineered_features"),
            os.path.join(project_root, "data", "processed", "auction_players")
        ]
        
        logger.info(f"Searching for player data in {len(paths_to_try)} locations...")
        
        for path in paths_to_try:
            logger.debug(f"Trying path: {path}")
            
            if path.endswith('.csv'):
                df = self.load_csv(path, use_cache=False)
            else:
                df = self.load_parquet(path, use_cache=False)
            
            if df is not None and len(df) > 0:
                logger.info(f"✅ Successfully loaded {len(df)} players from: {path}")
                
                # Standardize column names
                if 'player_name_raw' in df.columns:
                    df = df.rename(columns={'player_name_raw': 'player_name'})
                elif 'Players' in df.columns:
                    df = df.rename(columns={'Players': 'player_name'})
                
                # Add missing columns with default values
                if 'overall_impact' not in df.columns and len(df) > 0:
                    df['overall_impact'] = np.random.uniform(40, 90, len(df))
                if 'consistency_rating' not in df.columns and len(df) > 0:
                    df['consistency_rating'] = np.random.uniform(50, 90, len(df))
                if 'sold_price' not in df.columns and 'Sold' in df.columns:
                    df['sold_price'] = pd.to_numeric(df['Sold'], errors='coerce').fillna(1.0)
                if 'base_price' not in df.columns and 'Base' in df.columns:
                    # Convert '-' to NaN then to 0
                    df['base_price'] = pd.to_numeric(df['Base'].replace('-', '0'), errors='coerce').fillna(0.2)
                if 'team' not in df.columns and 'Team' in df.columns:
                    df['team'] = df['Team']
                if 'role' not in df.columns and 'Type' in df.columns:
                    # Map Type to role
                    role_mapping = {
                        'BAT': 'Batsman',
                        'BOWL': 'Bowler',
                        'AR': 'All-rounder',
                        'WK': 'Wicket-keeper'
                    }
                    df['role'] = df['Type'].map(role_mapping).fillna('All-rounder')
                
                return df
        
        logger.warning("⚠️ No player data found in any location, using synthetic data")
        return self._generate_synthetic_data()
    
    def _generate_synthetic_data(self) -> pd.DataFrame:
        """Generate synthetic player data as fallback"""
        
        logger.info("Generating synthetic player data...")
        
        n_players = 622
        roles = ['Batsman', 'Bowler', 'All-rounder', 'Wicket-keeper']
        teams = ['RCB', 'MI', 'CSK', 'SRH', 'DC', 'KKR', 'PBKS', 'RR', 'GT', 'LSG']
        
        np.random.seed(42)
        
        data = {
            'player_name': [f'Player_{i}' for i in range(n_players)],
            'role': np.random.choice(roles, n_players),
            'team': np.random.choice(teams, n_players),
            'sold_price': np.random.uniform(0.2, 20.0, n_players),
            'base_price': np.random.uniform(0.2, 2.0, n_players),
            'overall_impact': np.random.uniform(20, 100, n_players),
            'consistency_rating': np.random.uniform(30, 90, n_players),
            'batting_average': np.random.uniform(15, 60, n_players),
            'strike_rate': np.random.uniform(100, 200, n_players),
            'wickets_taken': np.random.uniform(0, 100, n_players),
            'economy_rate': np.random.uniform(5, 12, n_players),
            'value_score': np.random.uniform(0.5, 5.0, n_players)
        }
        
        return pd.DataFrame(data)
    
    def filter_players(self, df: pd.DataFrame, filters: Dict) -> pd.DataFrame:
        """Filter players based on criteria"""
        
        filtered_df = df.copy()
        
        # Role filter
        if 'role' in filters and filters['role']:
            roles = filters['role'] if isinstance(filters['role'], list) else [filters['role']]
            filtered_df = filtered_df[filtered_df['role'].isin(roles)]
        
        # Team filter
        if 'team' in filters and filters['team']:
            filtered_df = filtered_df[filtered_df['team'] == filters['team']]
        
        # Budget filter
        if 'max_price' in filters and filters['max_price']:
            filtered_df = filtered_df[filtered_df['sold_price'] <= filters['max_price']]
        
        if 'min_price' in filters and filters['min_price']:
            filtered_df = filtered_df[filtered_df['sold_price'] >= filters['min_price']]
        
        # Country filter
        if 'country' in filters and filters['country']:
            filtered_df = filtered_df[filtered_df['country'] == filters['country']]
        
        return filtered_df
    
    def search_players(self, df: pd.DataFrame, query: str) -> pd.DataFrame:
        """Search players by name"""
        
        if not query:
            return df
        
        query_lower = query.lower()
        
        mask = df['player_name'].str.lower().str.contains(query_lower, na=False)
        
        return df[mask]
    
    def clear_cache(self):
        """Clear all cached data"""
        
        self.cache.clear()
        self.cache_ttl.clear()
        logger.info("Data cache cleared")


# Global data loader instance
data_loader = DataLoader()


def get_data_loader() -> DataLoader:
    """Get data loader instance"""
    return data_loader
