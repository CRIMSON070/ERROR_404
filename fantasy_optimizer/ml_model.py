"""
Machine Learning Model for Fantasy Points Prediction
Uses RandomForestRegressor to predict player performance
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os
from typing import Dict, List, Tuple


class FantasyPointsPredictor:
    """ML model for predicting fantasy cricket points"""
    
    def __init__(self, model_type: str = 'random_forest'):
        """
        Initialize the predictor
        
        Args:
            model_type: Type of model ('random_forest' or 'gradient_boosting')
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = [
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
        
        # Initialize model based on type
        if model_type == 'gradient_boosting':
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
        else:  # Default: Random Forest
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
    
    def prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """
        Prepare feature matrix from DataFrame
        
        Args:
            df: DataFrame with player data
            
        Returns:
            Numpy array of features
        """
        # Ensure all required columns exist
        for col in self.feature_columns:
            if col not in df.columns:
                if col == 'batting_average':
                    df[col] = df['runs'] / df['matches'].replace(0, 1)
                elif col == 'experience':
                    df[col] = df['matches'] / 100.0
                elif col == 'value_rating':
                    df[col] = df.get('value_score', df.get('fantasy_points', 50) / 10)
                elif col.startswith('is_'):
                    df[col] = 0
                else:
                    df[col] = 0
        
        # Extract features
        X = df[self.feature_columns].values
        
        # Handle missing values
        X = np.nan_to_num(X, nan=0.0)
        
        return X
    
    def train(self, df: pd.DataFrame, target_col: str = 'fantasy_points') -> Dict:
        """
        Train the ML model
        
        Args:
            df: DataFrame with training data
            target_col: Name of target column
            
        Returns:
            Dictionary with training metrics
        """
        print("🤖 Training Fantasy Points Prediction Model...")
        
        # Prepare features
        X = self.prepare_features(df)
        
        # Prepare target
        if target_col not in df.columns:
            # Calculate fantasy points if not present
            df['fantasy_points'] = (
                df['runs'] / 2 +
                df['wickets'] * 25 +
                df['strike_rate'] / 10 -
                df['economy'] * 5
            ).clip(lower=0)
        
        y = df[target_col].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred_train = self.model.predict(X_train)
        y_pred_test = self.model.predict(X_test)
        
        train_mae = mean_absolute_error(y_train, y_pred_train)
        test_mae = mean_absolute_error(y_test, y_pred_test)
        train_r2 = r2_score(y_train, y_pred_train)
        test_r2 = r2_score(y_test, y_pred_test)
        
        self.is_trained = True
        
        metrics = {
            'train_mae': train_mae,
            'test_mae': test_mae,
            'train_r2': train_r2,
            'test_r2': test_r2,
            'n_samples': len(df),
            'n_features': len(self.feature_columns)
        }
        
        print(f"✅ Model trained successfully!")
        print(f"   Train MAE: {train_mae:.2f}, R²: {train_r2:.3f}")
        print(f"   Test MAE: {test_mae:.2f}, R²: {test_r2:.3f}")
        
        return metrics
    
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        Predict fantasy points for players
        
        Args:
            df: DataFrame with player data
            
        Returns:
            Array of predicted fantasy points
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        X = self.prepare_features(df)
        X_scaled = self.scaler.transform(X)
        
        predictions = self.model.predict(X_scaled)
        
        # Ensure non-negative predictions
        predictions = np.maximum(predictions, 0)
        
        return predictions
    
    def predict_with_confidence(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict with confidence intervals using ensemble variance
        
        Args:
            df: DataFrame with player data
            
        Returns:
            Tuple of (predictions, confidence_intervals)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        X = self.prepare_features(df)
        X_scaled = self.scaler.transform(X)
        
        # For Random Forest, use tree variance for confidence
        if hasattr(self.model, 'estimators_'):
            predictions_trees = np.array([tree.predict(X_scaled) for tree in self.model.estimators_])
            mean_pred = predictions_trees.mean(axis=0)
            std_pred = predictions_trees.std(axis=0)
            
            # 95% confidence interval
            ci_lower = mean_pred - 1.96 * std_pred
            ci_upper = mean_pred + 1.96 * std_pred
            
            confidence = np.column_stack([ci_lower, ci_upper])
        else:
            # Fallback: use fixed percentage
            mean_pred = self.model.predict(X_scaled)
            confidence = np.column_stack([
                mean_pred * 0.8,
                mean_pred * 1.2
            ])
        
        return mean_pred, confidence
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance from trained model
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self.is_trained:
            return {}
        
        if hasattr(self.model, 'feature_importances_'):
            importance = dict(zip(self.feature_columns, self.model.feature_importances_))
            return importance
        return {}
    
    def save_model(self, filepath: str):
        """
        Save trained model to disk
        
        Args:
            filepath: Path to save model
        """
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'model_type': self.model_type
        }, filepath)
        print(f"💾 Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """
        Load trained model from disk
        
        Args:
            filepath: Path to load model from
        """
        try:
            data = joblib.load(filepath)
            self.model = data['model']
            self.scaler = data['scaler']
            self.feature_columns = data['feature_columns']
            self.model_type = data['model_type']
            self.is_trained = True
            print(f"📂 Model loaded from {filepath}")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def get_top_performers(self, df: pd.DataFrame, top_n: int = 11) -> pd.DataFrame:
        """
        Get top performing players based on predictions
        
        Args:
            df: DataFrame with player data
            top_n: Number of top players to select
            
        Returns:
            DataFrame with top players
        """
        predictions = self.predict(df)
        
        result_df = df.copy()
        result_df['predicted_fantasy_points'] = predictions
        
        # Sort by predicted points
        top_players = result_df.nlargest(top_n, 'predicted_fantasy_points')
        
        return top_players
