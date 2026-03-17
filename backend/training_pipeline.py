"""
Training Pipeline for IPL Player Value Prediction Model
Handles data loading, training loop, and model checkpointing
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Optional
import os
from tqdm import tqdm
import logging

from models.player_value_model import PlayerValueDNN, CombinedLoss
from backend.feature_engineering import PlayerFeatureEngineer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlayerDataset(Dataset):
    """PyTorch Dataset for player features and targets"""
    
    def __init__(self, X: np.ndarray, y_value: np.ndarray, 
                 y_performance: np.ndarray, y_risk: np.ndarray):
        self.X = torch.FloatTensor(X)
        self.y_value = torch.FloatTensor(y_value)
        self.y_performance = torch.FloatTensor(y_performance)
        self.y_risk = torch.FloatTensor(y_risk)
    
    def __len__(self) -> int:
        return len(self.X)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor, torch.Tensor]]:
        return (
            self.X[idx],
            (self.y_value[idx], self.y_performance[idx], self.y_risk[idx])
        )


class ModelTrainer:
    """
    Trainer class for Player Value DNN
    
    Features:
    - Batch training with DataLoader
    - Early stopping
    - Learning rate scheduling
    - Model checkpointing
    - Progress tracking
    """
    
    def __init__(self, input_dim: int, hidden_dims=[128, 64, 32], 
                 learning_rate=0.001, batch_size=32, device='cpu'):
        
        self.device = device
        self.batch_size = batch_size
        
        # Initialize model
        self.model = PlayerValueDNN(input_dim=input_dim, hidden_dims=hidden_dims).to(device)
        
        # Loss function
        self.criterion = CombinedLoss(
            value_weight=1.0,
            performance_weight=0.5,
            risk_weight=0.3
        )
        
        # Optimizer
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        
        # Learning rate scheduler
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', factor=0.5, patience=5, verbose=True
        )
        
        # Training history
        self.history = {
            'train_loss': [],
            'val_loss': [],
            'value_loss': [],
            'performance_loss': [],
            'risk_loss': []
        }
        
        # Early stopping parameters
        self.best_val_loss = float('inf')
        self.patience_counter = 0
        self.early_stop_patience = 15
    
    def train_epoch(self, train_loader: DataLoader) -> float:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        n_batches = 0
        
        for batch_X, (batch_y_val, batch_y_perf, batch_y_risk) in train_loader:
            batch_X = batch_X.to(self.device)
            batch_y_val = batch_y_val.to(self.device)
            batch_y_perf = batch_y_perf.to(self.device)
            batch_y_risk = batch_y_risk.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            predictions = self.model(batch_X)
            
            # Compute loss
            loss, loss_dict = self.criterion(predictions, (batch_y_val, batch_y_perf, batch_y_risk))
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            n_batches += 1
        
        return total_loss / n_batches
    
    def validate(self, val_loader: DataLoader) -> Tuple[float, Dict[str, float]]:
        """Validate on validation set"""
        self.model.eval()
        total_loss = 0.0
        total_value_loss = 0.0
        total_perf_loss = 0.0
        total_risk_loss = 0.0
        n_batches = 0
        
        with torch.no_grad():
            for batch_X, (batch_y_val, batch_y_perf, batch_y_risk) in val_loader:
                batch_X = batch_X.to(self.device)
                batch_y_val = batch_y_val.to(self.device)
                batch_y_perf = batch_y_perf.to(self.device)
                batch_y_risk = batch_y_risk.to(self.device)
                
                # Forward pass
                predictions = self.model(batch_X)
                
                # Compute loss
                loss, loss_dict = self.criterion(predictions, (batch_y_val, batch_y_perf, batch_y_risk))
                
                total_loss += loss.item()
                total_value_loss += loss_dict['value_loss']
                total_perf_loss += loss_dict['performance_loss']
                total_risk_loss += loss_dict['risk_loss']
                n_batches += 1
        
        avg_loss = total_loss / n_batches
        loss_components = {
            'value_loss': total_value_loss / n_batches,
            'performance_loss': total_perf_loss / n_batches,
            'risk_loss': total_risk_loss / n_batches
        }
        
        return avg_loss, loss_components
    
    def train(self, train_data: Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
              val_data: Optional[Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = None,
              epochs: int = 100) -> Dict:
        """
        Full training loop with early stopping
        
        Args:
            train_data: (X_train, y_val_train, y_perf_train, y_risk_train)
            val_data: Optional validation data
            epochs: Maximum number of epochs
        
        Returns:
            Training history
        """
        # Create DataLoaders
        train_dataset = PlayerDataset(*train_data)
        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
        
        val_loader = None
        if val_data is not None:
            val_dataset = PlayerDataset(*val_data)
            val_loader = DataLoader(val_dataset, batch_size=self.batch_size, shuffle=False)
        
        logger.info(f"🚀 Starting training for {epochs} epochs...")
        logger.info(f"   Training samples: {len(train_dataset)}")
        if val_loader:
            logger.info(f"   Validation samples: {len(val_dataset)}")
        
        # Training loop
        pbar = tqdm(range(epochs), desc="Training")
        
        for epoch in pbar:
            # Train
            train_loss = self.train_epoch(train_loader)
            self.history['train_loss'].append(train_loss)
            
            # Validate
            if val_loader:
                val_loss, val_loss_dict = self.validate(val_loader)
                self.history['val_loss'].append(val_loss)
                self.history['value_loss'].append(val_loss_dict['value_loss'])
                self.history['performance_loss'].append(val_loss_dict['performance_loss'])
                self.history['risk_loss'].append(val_loss_dict['risk_loss'])
                
                # Update scheduler
                self.scheduler.step(val_loss)
                
                # Progress update
                pbar.set_postfix({
                    'train_loss': f"{train_loss:.4f}",
                    'val_loss': f"{val_loss:.4f}",
                    'lr': f"{self.optimizer.param_groups[0]['lr']:.6f}"
                })
                
                # Early stopping check
                if val_loss < self.best_val_loss:
                    self.best_val_loss = val_loss
                    self.patience_counter = 0
                    # Save best model
                    self.save_checkpoint("best_model.pth")
                else:
                    self.patience_counter += 1
                    if self.patience_counter >= self.early_stop_patience:
                        logger.info(f"\n⏹️ Early stopping at epoch {epoch+1}")
                        break
            else:
                pbar.set_postfix({'train_loss': f"{train_loss:.4f}"})
                self.history['val_loss'].append(train_loss)
        
        logger.info(f"\n✅ Training completed!")
        logger.info(f"   Best validation loss: {self.best_val_loss:.4f}")
        
        # Load best model
        if os.path.exists("best_model.pth"):
            self.load_checkpoint("best_model.pth")
        
        return self.history
    
    def save_checkpoint(self, path: str):
        """Save training checkpoint"""
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'history': self.history,
            'best_val_loss': self.best_val_loss
        }, path)
        logger.info(f"💾 Checkpoint saved to {path}")
    
    def load_checkpoint(self, path: str):
        """Load training checkpoint"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Checkpoint not found: {path}")
        
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.history = checkpoint['history']
        self.best_val_loss = checkpoint['best_val_loss']
        logger.info(f"📂 Checkpoint loaded from {path}")
    
    def get_model(self) -> PlayerValueDNN:
        """Get trained model"""
        return self.model


def prepare_data(csv_path: str, test_split: float = 0.2, val_split: float = 0.1) -> tuple:
    """
    Prepare data for training
    
    Splits data into train/val/test sets
    """
    logger.info(f"📊 Preparing data from {csv_path}...")
    
    # Feature engineering
    engineer = PlayerFeatureEngineer()
    X, y_val, y_perf, y_risk, feature_cols = engineer.run_full_pipeline(csv_path)
    
    # Normalize targets
    y_val_mean, y_val_std = y_val.mean(), y_val.std()
    y_perf_mean, y_perf_std = y_perf.mean(), y_perf.std()
    
    y_val_norm = (y_val - y_val_mean) / (y_val_std + 1e-6)
    y_perf_norm = (y_perf - y_perf_mean) / (y_perf_std + 1e-6)
    
    # Shuffle data
    indices = np.random.permutation(len(X))
    X = X[indices]
    y_val_norm = y_val_norm[indices]
    y_perf_norm = y_perf_norm[indices]
    y_risk = y_risk[indices]
    
    # Split data
    n_samples = len(X)
    n_test = int(n_samples * test_split)
    n_val = int(n_samples * val_split)
    n_train = n_samples - n_test - n_val
    
    X_train, X_test = X[:n_train], X[n_train:n_train+n_test]
    y_val_train, y_val_test = y_val_norm[:n_train], y_val_norm[n_train:n_train+n_test]
    y_perf_train, y_perf_test = y_perf_norm[:n_train], y_perf_norm[n_train:n_train+n_test]
    y_risk_train, y_risk_test = y_risk[:n_train], y_risk[n_train:n_train+n_test]
    
    X_train, X_val = X_train[:n_train], X[n_train:n_train+n_val]
    y_val_train, y_val_val = y_val_train[:n_train], y_val_norm[n_train:n_train+n_val]
    y_perf_train, y_perf_val = y_perf_train[:n_train], y_perf_norm[n_train:n_train+n_val]
    y_risk_train, y_risk_val = y_risk_train[:n_train], y_risk[n_train:n_train+n_val]
    
    logger.info(f"✅ Data prepared:")
    logger.info(f"   Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
    
    return (
        (X_train, y_val_train, y_perf_train, y_risk_train),
        (X_val, y_val_val, y_perf_val, y_risk_val),
        (X_test, y_val_test, y_perf_test, y_risk_test),
        feature_cols,
        {'value': (y_val_mean, y_val_std), 'performance': (y_perf_mean, y_perf_std)}
    )


# Main training script
if __name__ == "__main__":
    csv_path = "ipl_2025_auction_players.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ Data file not found: {csv_path}")
        print("Please ensure the CSV file is in the project root directory")
    else:
        # Prepare data
        train_data, val_data, test_data, feature_cols, normalization_params = prepare_data(csv_path)
        
        # Initialize trainer
        input_dim = train_data[0].shape[1]
        trainer = ModelTrainer(
            input_dim=input_dim,
            hidden_dims=[128, 64, 32],
            learning_rate=0.001,
            batch_size=32,
            device='cpu'
        )
        
        # Train model
        history = trainer.train(train_data, val_data, epochs=100)
        
        # Save final model
        trainer.save_checkpoint("player_value_model_final.pth")
        
        # Evaluate on test set
        test_loss = trainer.validate(DataLoader(PlayerDataset(*test_data), batch_size=32))
        print(f"\n📊 Test Loss: {test_loss[0]:.4f}")
        
        print("\n🎉 Training pipeline completed successfully!")
