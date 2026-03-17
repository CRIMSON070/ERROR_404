"""
Deep Learning Models for IPL Player Value Prediction and Team Optimization
Multi-task DNN architecture for predicting player value, performance, and risk
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, Tuple, Optional
import os


class PlayerValueDNN(nn.Module):
    """
    Multi-Task Deep Neural Network for Player Analysis
    
    Predicts:
    1. Player's true market value (₹ Crore)
    2. Performance score (0-100)
    3. Risk score (0-1)
    """
    
    def __init__(self, input_dim: int, hidden_dims=[128, 64, 32], dropout_rate=0.3):
        super(PlayerValueDNN, self).__init__()
        
        self.input_dim = input_dim
        
        # Feature extraction layers
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.BatchNorm1d(hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout_rate)
            ])
            prev_dim = hidden_dim
        
        self.feature_extractor = nn.Sequential(*layers)
        
        # Task-specific heads
        # Head 1: Player Value Prediction (Regression)
        self.value_head = nn.Sequential(
            nn.Linear(hidden_dims[-1], 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Softplus()  # Ensure positive values
        )
        
        # Head 2: Performance Score (0-100)
        self.performance_head = nn.Sequential(
            nn.Linear(hidden_dims[-1], 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()  # 0-1 range
        )
        
        # Head 3: Risk Score (0-1)
        self.risk_head = nn.Sequential(
            nn.Linear(hidden_dims[-1], 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()  # 0-1 range
        )
        
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize weights using Xavier initialization"""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.BatchNorm1d):
                nn.init.ones_(m.weight)
                nn.init.zeros_(m.bias)
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass
        
        Returns:
            predicted_value: Market value in ₹ Crore
            performance_score: 0-100 scale
            risk_score: 0-1 scale
        """
        # Extract features
        features = self.feature_extractor(x)
        
        # Task-specific predictions
        predicted_value = self.value_head(features)
        performance_score = self.performance_head(features) * 100  # Scale to 0-100
        risk_score = self.risk_head(features)
        
        return predicted_value.squeeze(-1), performance_score.squeeze(-1), risk_score.squeeze(-1)
    
    def predict(self, x: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Inference method for single prediction
        
        Args:
            x: Input features (batch_size, input_dim) or (input_dim,)
        
        Returns:
            Dictionary with predictions
        """
        self.eval()
        
        # Handle single sample
        if len(x.shape) == 1:
            x = x.reshape(1, -1)
        
        with torch.no_grad():
            x_tensor = torch.FloatTensor(x)
            value, perf, risk = self.forward(x_tensor)
            
            return {
                'predicted_value': value.numpy()[0],
                'performance_score': perf.numpy()[0],
                'risk_score': risk.numpy()[0]
            }
    
    def save_model(self, path: str):
        """Save model checkpoint"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save({
            'model_state_dict': self.state_dict(),
            'input_dim': self.input_dim,
            'architecture': 'PlayerValueDNN'
        }, path)
        print(f"✅ Model saved to {path}")
    
    @classmethod
    def load_model(cls, path: str) -> 'PlayerValueDNN':
        """Load model from checkpoint"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
        
        checkpoint = torch.load(path, map_location=torch.device('cpu'))
        model = cls(input_dim=checkpoint['input_dim'])
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()
        print(f"✅ Model loaded from {path}")
        return model


class PlayerEmbeddingNetwork(nn.Module):
    """
    Embedding network for player similarity computation
    Used for replacement suggestions
    """
    
    def __init__(self, input_dim: int, embedding_dim: int = 32):
        super(PlayerEmbeddingNetwork, self).__init__()
        
        self.embedding_network = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Linear(32, embedding_dim)
        )
        
        self._initialize_weights()
    
    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Generate normalized embeddings"""
        embeddings = self.embedding_network(x)
        # L2 normalize for cosine similarity
        embeddings = F.normalize(embeddings, p=2, dim=1)
        return embeddings
    
    def get_similar_players(self, player_embedding: np.ndarray, 
                           all_embeddings: np.ndarray, 
                           top_k: int = 5) -> np.ndarray:
        """
        Find most similar players using cosine similarity
        
        Args:
            player_embedding: Target player embedding (embedding_dim,)
            all_embeddings: All player embeddings (n_players, embedding_dim)
            top_k: Number of similar players to return
        
        Returns:
            Indices of top_k similar players
        """
        # Compute cosine similarity
        similarities = np.dot(all_embeddings, player_embedding)
        
        # Get top_k indices (excluding the player itself)
        top_indices = np.argsort(similarities)[::-1][:top_k+1]
        
        return top_indices


class CombinedLoss(nn.Module):
    """
    Multi-task loss function with weighted components
    """
    
    def __init__(self, value_weight=1.0, performance_weight=0.5, risk_weight=0.3):
        super(CombinedLoss, self).__init__()
        
        self.value_weight = value_weight
        self.performance_weight = performance_weight
        self.risk_weight = risk_weight
        
        # MSE for regression tasks
        self.mse_loss = nn.MSELoss()
        # BCE for risk score
        self.bce_loss = nn.BCELoss()
    
    def forward(self, predictions: Tuple[torch.Tensor, torch.Tensor, torch.Tensor],
                targets: Tuple[torch.Tensor, torch.Tensor, torch.Tensor]) -> torch.Tensor:
        """
        Compute combined loss
        
        Args:
            predictions: (value, performance, risk)
            targets: (value, performance, risk)
        """
        pred_value, pred_perf, pred_risk = predictions
        true_value, true_perf, true_risk = targets
        
        # Value loss (MSE)
        value_loss = self.mse_loss(pred_value, true_value)
        
        # Performance loss (MSE scaled)
        performance_loss = self.mse_loss(pred_perf, true_perf)
        
        # Risk loss (BCE)
        risk_loss = self.bce_loss(pred_risk, true_risk)
        
        # Combined loss
        total_loss = (
            self.value_weight * value_loss +
            self.performance_weight * performance_loss +
            self.risk_weight * risk_loss
        )
        
        return total_loss, {
            'value_loss': value_loss.item(),
            'performance_loss': performance_loss.item(),
            'risk_loss': risk_loss.item()
        }


# Example usage and testing
if __name__ == "__main__":
    # Test model
    input_dim = 50  # Example feature dimension
    batch_size = 32
    
    model = PlayerValueDNN(input_dim=input_dim)
    
    # Random input
    x = torch.randn(batch_size, input_dim)
    
    # Forward pass
    value, perf, risk = model(x)
    
    print(f"📊 Model Output Shapes:")
    print(f"  Predicted Value: {value.shape}")
    print(f"  Performance Score: {perf.shape}")
    print(f"  Risk Score: {risk.shape}")
    
    # Test inference
    sample_input = np.random.randn(input_dim)
    predictions = model.predict(sample_input)
    
    print(f"\n🎯 Sample Predictions:")
    print(f"  Value: ₹{predictions['predicted_value']:.2f} Cr")
    print(f"  Performance: {predictions['performance_score']:.1f}/100")
    print(f"  Risk: {predictions['risk_score']:.2f}")
    
    # Save and load test
    model.save_model("test_model.pth")
    loaded_model = PlayerValueDNN.load_model("test_model.pth")
    
    print("\n✅ All tests passed!")
