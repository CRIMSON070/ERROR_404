"""
Model loading utilities for DL models
"""

import os
import torch
import numpy as np
from typing import Dict, Optional, Any
from loguru import logger


class ModelLoader:
    """Load and manage deep learning models"""
    
    def __init__(self, models_dir: str = "models/saved_models"):
        self.models_dir = models_dir
        self.models: Dict[str, Any] = {}
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        logger.info(f"ModelLoader initialized on {self.device}")
    
    def load_performance_model(self) -> Optional[Any]:
        """Load player performance prediction model"""
        
        try:
            model_path = os.path.join(self.models_dir, "performance_model_complete.pth")
            
            if not os.path.exists(model_path):
                logger.warning("Performance model not found, using synthetic predictions")
                return None
            
            checkpoint = torch.load(model_path, map_location=self.device)
            
            # Import model architecture
            from models.performance_predictor import PlayerPerformanceDNN
            
            model = PlayerPerformanceDNN(
                input_dim=checkpoint.get('input_dim', 10),
                output_dim=checkpoint.get('output_dim', 4)
            )
            model.load_state_dict(checkpoint['model_state_dict'])
            model.to(self.device)
            model.eval()
            
            self.models['performance'] = model
            logger.info("✅ Performance model loaded")
            
            return model
        
        except Exception as e:
            logger.error(f"Error loading performance model: {e}")
            return None
    
    def load_embedding_model(self) -> Optional[tuple]:
        """Load player embedding model and embeddings"""
        
        try:
            model_path = os.path.join(self.models_dir, "player_embedding_complete.pth")
            embeddings_path = os.path.join(self.models_dir, "player_embeddings.npy")
            
            if not os.path.exists(model_path):
                logger.warning("Embedding model not found")
                return None
            
            checkpoint = torch.load(model_path, map_location=self.device)
            
            # Load embeddings
            embeddings = np.load(embeddings_path) if os.path.exists(embeddings_path) else None
            
            self.models['embeddings'] = {
                'checkpoint': checkpoint,
                'embeddings': embeddings
            }
            
            logger.info("✅ Embedding model loaded")
            
            return checkpoint, embeddings
        
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            return None
    
    def load_team_strength_model(self) -> Optional[Any]:
        """Load team strength model"""
        
        try:
            model_path = os.path.join(self.models_dir, "team_strength_complete.pth")
            
            if not os.path.exists(model_path):
                logger.warning("Team strength model not found")
                return None
            
            checkpoint = torch.load(model_path, map_location=self.device)
            
            from models.team_strength_model import TeamStrengthModel
            
            model = TeamStrengthModel(
                player_embedding_dim=checkpoint.get('embedding_dim', 32)
            )
            model.load_state_dict(checkpoint['model_state_dict'])
            model.to(self.device)
            model.eval()
            
            self.models['team_strength'] = model
            logger.info("✅ Team strength model loaded")
            
            return model
        
        except Exception as e:
            logger.error(f"Error loading team strength model: {e}")
            return None
    
    def load_match_outcome_model(self) -> Optional[Any]:
        """Load match outcome LSTM model"""
        
        try:
            model_path = os.path.join(self.models_dir, "match_outcome_model_complete.pth")
            
            if not os.path.exists(model_path):
                logger.warning("Match outcome model not found")
                return None
            
            checkpoint = torch.load(model_path, map_location=self.device)
            
            from models.match_outcome_lstm import MatchOutcomeLSTM
            
            model = MatchOutcomeLSTM(
                input_dim=checkpoint.get('feature_dim', 15),
                hidden_dim=128,
                num_layers=2
            )
            model.load_state_dict(checkpoint['model_state_dict'])
            model.to(self.device)
            model.eval()
            
            self.models['match_outcome'] = model
            logger.info("✅ Match outcome model loaded")
            
            return model
        
        except Exception as e:
            logger.error(f"Error loading match outcome model: {e}")
            return None
    
    def predict_performance(self, features: np.ndarray) -> np.ndarray:
        """Predict player performance using loaded model"""
        
        if 'performance' not in self.models:
            # Return synthetic predictions
            return np.random.randn(len(features), 4) * 20 + 50
        
        model = self.models['performance']
        
        with torch.no_grad():
            features_tensor = torch.FloatTensor(features).to(self.device)
            predictions = model(features_tensor)
            return predictions.cpu().numpy()
    
    def calculate_team_strength(self, team_embeddings: np.ndarray) -> float:
        """Calculate team strength score"""
        
        if 'team_strength' not in self.models:
            # Return synthetic score
            return np.random.uniform(0.6, 0.9)
        
        model = self.models['team_strength']
        
        if len(team_embeddings.shape) == 2:
            team_embeddings = team_embeddings.unsqueeze(0)
        
        with torch.no_grad():
            team_tensor = torch.FloatTensor(team_embeddings).to(self.device)
            strength, _ = model(team_tensor)
            return strength.item()
    
    def is_model_loaded(self, model_name: str) -> bool:
        """Check if a model is loaded"""
        return model_name in self.models
    
    def get_all_models_status(self) -> Dict[str, bool]:
        """Get status of all models"""
        
        return {
            'performance': 'performance' in self.models,
            'embeddings': 'embeddings' in self.models,
            'team_strength': 'team_strength' in self.models,
            'match_outcome': 'match_outcome' in self.models
        }


# Global model loader instance
model_loader = ModelLoader()


def get_model_loader() -> ModelLoader:
    """Get model loader instance"""
    return model_loader
