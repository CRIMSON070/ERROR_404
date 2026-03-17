"""
Feature Engineering for IPL Player Value Prediction
Uses Spark for large-scale feature processing
"""

import pandas as pd
import numpy as np
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, avg, stddev, udf
from pyspark.sql.types import DoubleType
import os
from typing import Optional, List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlayerFeatureEngineer:
    """
    Feature engineering pipeline for player analysis
    
    Creates features from:
    - Player statistics (batting, bowling, fielding)
    - Auction data (base price, sold price)
    - Historical performance
    - Role encoding
    """
    
    def __init__(self, spark_session: Optional[SparkSession] = None):
        if spark_session is None:
            self.spark = SparkSession.builder \
                .appName("IPL_Player_Features") \
                .master("local[*]") \
                .config("spark.sql.shuffle.partitions", "4") \
                .getOrCreate()
        else:
            self.spark = spark_session
        
        self.feature_columns = []
        self.categorical_encodings = {}
    
    def load_raw_data(self, csv_path: str) -> pd.DataFrame:
        """Load raw player data from CSV"""
        logger.info(f"Loading data from {csv_path}")
        df = pd.read_csv(csv_path)
        logger.info(f"✅ Loaded {len(df)} players")
        return df
    
    def create_base_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create basic numerical and categorical features"""
        
        feature_df = df.copy()
        
        # Encode role as numerical
        role_mapping = {
            'WK': 0,
            'BAT': 1,
            'AR': 2,
            'BOWL': 3
        }
        feature_df['role_encoded'] = feature_df['Type'].map(role_mapping).fillna(2)
        
        # One-hot encode role
        roles = pd.get_dummies(feature_df['Type'], prefix='role')
        feature_df = pd.concat([feature_df, roles], axis=1)
        
        # Team encoding (frequency-based)
        team_freq = feature_df['Team'].value_counts(normalize=True).to_dict()
        feature_df['team_frequency'] = feature_df['Team'].map(team_freq).fillna(0.01)
        
        # Price features
        if 'Sold' in feature_df.columns:
            feature_df['sold_price_numeric'] = pd.to_numeric(
                feature_df['Sold'], errors='coerce'
            ).fillna(1.0)
        
        if 'Base' in feature_df.columns:
            feature_df['base_price_numeric'] = pd.to_numeric(
                feature_df['Base'].replace('-', '0'), errors='coerce'
            ).fillna(0.2)
            
            # Price ratio
            if 'sold_price_numeric' in feature_df.columns:
                feature_df['price_ratio'] = (
                    feature_df['sold_price_numeric'] / 
                    (feature_df['base_price_numeric'] + 0.1)
                )
        
        # Nationality indicator (if country column exists)
        if 'Country' in feature_df.columns:
            feature_df['is_indian'] = (feature_df['Country'] == 'India').astype(int)
        else:
            feature_df['is_indian'] = 1  # Default assumption
        
        # Age proxy (if DOB exists, otherwise use random)
        if 'DOB' in feature_df.columns:
            from datetime import datetime
            current_year = datetime.now().year
            
            def extract_year(dob_str):
                try:
                    if isinstance(dob_str, str) and len(dob_str) >= 4:
                        return int(dob_str[-4:])
                    return 1995  # Default
                except:
                    return 1995
            
            birth_years = feature_df['DOB'].apply(extract_year)
            feature_df['age'] = current_year - birth_years
            feature_df['age_normalized'] = (feature_df['age'] - feature_df['age'].mean()) / (feature_df['age'].std() + 1e-6)
        else:
            feature_df['age'] = np.random.randint(22, 35, len(feature_df))
            feature_df['age_normalized'] = np.random.randn(len(feature_df)) * 0.5
        
        logger.info(f"✅ Created {len(feature_df.columns)} base features")
        return feature_df
    
    def create_advanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create advanced derived features"""
        
        feature_df = df.copy()
        
        # Interaction features
        if 'sold_price_numeric' in feature_df.columns:
            feature_df['price_per_role'] = (
                feature_df['sold_price_numeric'] * feature_df['role_encoded']
            )
            
            feature_df['price_age_interaction'] = (
                feature_df['sold_price_numeric'] * feature_df.get('age_normalized', 0)
            )
        
        # Experience proxy
        feature_df['experience_score'] = np.clip(
            30 - feature_df.get('age', 28), 0, 10
        ) / 10.0
        
        # Market demand indicator
        if 'sold_price_numeric' in feature_df.columns:
            median_price = feature_df['sold_price_numeric'].median()
            feature_df['above_median'] = (
                feature_df['sold_price_numeric'] > median_price
            ).astype(int)
        
        # Risk indicators
        if 'base_price_numeric' in feature_df.columns and 'sold_price_numeric' in feature_df.columns:
            feature_df['price_volatility'] = np.abs(
                feature_df['sold_price_numeric'] - feature_df['base_price_numeric']
            ) / (feature_df['base_price_numeric'] + 0.1)
        
        logger.info(f"✅ Created advanced features")
        return feature_df
    
    def normalize_features(self, df: pd.DataFrame, 
                          columns_to_normalize: Optional[List[str]] = None) -> pd.DataFrame:
        """Apply z-score normalization to numerical features"""
        
        feature_df = df.copy()
        
        if columns_to_normalize is None:
            # Auto-detect numerical columns
            numerical_cols = feature_df.select_dtypes(include=[np.number]).columns.tolist()
            exclude_cols = ['role_encoded', 'is_indian', 'above_median']
            columns_to_normalize = [c for c in numerical_cols if c not in exclude_cols]
        
        for col in columns_to_normalize:
            if col in feature_df.columns:
                mean_val = feature_df[col].mean()
                std_val = feature_df[col].std()
                feature_df[f'{col}_normalized'] = (feature_df[col] - mean_val) / (std_val + 1e-6)
        
        logger.info(f"✅ Normalized {len(columns_to_normalize)} features")
        return feature_df
    
    def prepare_final_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare final feature matrix for model input"""
        
        feature_df = df.copy()
        
        # Select key features
        feature_cols = [
            'role_encoded',
            'is_indian',
            'team_frequency',
            'age_normalized' if 'age_normalized' in df.columns else 'age',
        ]
        
        # Add price features if available
        if 'sold_price_numeric' in df.columns:
            feature_cols.extend([
                'sold_price_numeric',
                'base_price_numeric' if 'base_price_numeric' in df.columns else None,
                'price_ratio' if 'price_ratio' in df.columns else None,
            ])
        
        # Add normalized versions
        for col in ['sold_price_numeric', 'base_price_numeric', 'team_frequency']:
            norm_col = f'{col}_normalized'
            if norm_col in df.columns:
                feature_cols.append(norm_col)
        
        # Remove None values
        feature_cols = [c for c in feature_cols if c is not None and c in df.columns]
        
        # Add one-hot encoded role columns
        role_cols = [c for c in df.columns if c.startswith('role_')]
        feature_cols.extend(role_cols)
        
        # Add advanced features
        advanced_cols = ['experience_score', 'price_volatility', 'above_median']
        feature_cols.extend([c for c in advanced_cols if c in df.columns])
        
        final_df = feature_df[feature_cols].copy()
        
        # Fill any remaining NaN values
        final_df = final_df.fillna(0)
        
        self.feature_columns = final_df.columns.tolist()
        
        logger.info(f"✅ Final feature matrix: {final_df.shape}")
        logger.info(f"   Features: {self.feature_columns[:10]}... ({len(self.feature_columns)} total)")
        
        return final_df
    
    def create_training_target(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create training targets for multi-task learning"""
        
        target_df = df.copy()
        
        # Target 1: Player value (use sold price or estimate)
        if 'sold_price_numeric' in target_df.columns:
            target_df['target_value'] = target_df['sold_price_numeric']
        else:
            # Synthetic target based on role
            role_values = {'WK': 5.0, 'BAT': 8.0, 'AR': 7.0, 'BOWL': 6.0}
            target_df['target_value'] = target_df['Type'].map(role_values).fillna(5.0)
            target_df['target_value'] += np.random.normal(0, 2, len(target_df))
        
        # Target 2: Performance score (synthetic based on role and price)
        base_perf = 50 + np.random.normal(0, 15, len(target_df))
        
        if 'sold_price_numeric' in target_df.columns:
            price_bonus = np.clip(target_df['sold_price_numeric'] * 2, 0, 30)
            base_perf += price_bonus
        
        if 'Type' in target_df.columns:
            role_bonus = target_df['Type'].map({
                'WK': 5, 'BAT': 10, 'AR': 8, 'BOWL': 7
            }).fillna(5)
            base_perf += role_bonus
        
        target_df['target_performance'] = np.clip(base_perf, 0, 100)
        
        # Target 3: Risk score (based on price volatility and age)
        risk = np.random.uniform(0.2, 0.5, len(target_df))
        
        if 'price_volatility' in target_df.columns:
            risk += np.clip(target_df['price_volatility'] * 0.1, 0, 0.3)
        
        if 'age' in target_df.columns:
            # Young or old players are riskier
            age_risk = np.abs(target_df['age'] - 28) / 30
            risk += age_risk * 0.2
        
        target_df['target_risk'] = np.clip(risk, 0, 1)
        
        logger.info(f"✅ Created training targets")
        
        return target_df
    
    def run_full_pipeline(self, csv_path: str) -> tuple:
        """Run complete feature engineering pipeline"""
        
        logger.info("🚀 Starting full feature engineering pipeline...")
        
        # Load data
        raw_df = self.load_raw_data(csv_path)
        
        # Create features
        base_df = self.create_base_features(raw_df)
        advanced_df = self.create_advanced_features(base_df)
        normalized_df = self.normalize_features(advanced_df)
        
        # Prepare final features
        feature_matrix = self.prepare_final_features(normalized_df)
        
        # Create targets
        target_df = self.create_training_target(feature_matrix)
        
        # Extract features and targets
        X = target_df[self.feature_columns].values
        y_value = target_df['target_value'].values
        y_performance = target_df['target_performance'].values
        y_risk = target_df['target_risk'].values
        
        logger.info(f"\n📊 Pipeline Complete!")
        logger.info(f"   Training samples: {len(X)}")
        logger.info(f"   Feature dimensions: {X.shape[1]}")
        logger.info(f"   Value range: ₹{y_value.min():.2f} - ₹{y_value.max():.2f} Cr")
        logger.info(f"   Performance range: {y_performance.min():.1f} - {y_performance.max():.1f}")
        logger.info(f"   Risk range: {y_risk.min():.2f} - {y_risk.max():.2f}")
        
        return X, y_value, y_performance, y_risk, self.feature_columns


# Usage example
if __name__ == "__main__":
    # Initialize engineer
    engineer = PlayerFeatureEngineer()
    
    # Run pipeline
    csv_path = "ipl_2025_auction_players.csv"
    
    if os.path.exists(csv_path):
        X, y_val, y_perf, y_risk, features = engineer.run_full_pipeline(csv_path)
        
        print(f"\n✅ Feature engineering successful!")
        print(f"   Ready to train model with {X.shape[0]} samples")
    else:
        print(f"⚠️ Data file not found: {csv_path}")
