"""
Training Pipeline for Player Value Deep Learning Model
Handles data loading, preprocessing, and model training
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import json
import os
from tqdm import tqdm
from models.player_value_model import PlayerValueDNN, CombinedLoss


class IPLPlayerDataset(Dataset):
    """PyTorch Dataset for IPL player data"""
    
    def __init__(self, features: np.ndarray, value_targets: np.ndarray, 
                 performance_targets: np.ndarray, risk_targets: np.ndarray):
        self.features = torch.FloatTensor(features)
        self.value_targets = torch.FloatTensor(value_targets)
        self.performance_targets = torch.FloatTensor(performance_targets) / 100.0  # Normalize to 0-1
        self.risk_targets = torch.FloatTensor(risk_targets)
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        return (
            self.features[idx],
            (
                self.value_targets[idx],
                self.performance_targets[idx],
                self.risk_targets[idx]
            )
        )


class TrainingPipeline:
    """Complete training pipeline for player value prediction"""
    
    def __init__(self, config: dict = None):
        self.config = config or {
            'batch_size': 32,
            'learning_rate': 0.001,
            'epochs': 100,
            'hidden_dims': [128, 64, 32],
            'dropout_rate': 0.3,
            'early_stopping_patience': 10,
            'validation_split': 0.2
        }
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
    def prepare_data(self, csv_path: str) -> tuple:
        """
        Load and preprocess data from CSV
        
        Returns:
            X, y_value, y_performance, y_risk
        """
        print(f"📂 Loading data from {csv_path}...")
        df = pd.read_csv(csv_path)
        
        # Select relevant features
        feature_cols = []
        
        # Numeric features (adjust based on actual CSV columns)
        numeric_cols = ['sold_price', 'base_price', 'matches_played', 'runs', 'wickets',
                       'strike_rate', 'economy_rate', 'average', 'centuries', 'fifties']
        
        for col in numeric_cols:
            if col in df.columns:
                feature_cols.append(col)
                df[col] = df[col].fillna(df[col].median())
        
        # Categorical features
        categorical_cols = ['role', 'team', 'country']
        for col in categorical_cols:
            if col in df.columns:
                df[col] = df[col].fillna('Unknown')
                le = LabelEncoder()
                df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
                feature_cols.append(f'{col}_encoded')
                self.label_encoders[col] = le
        
        # Remove rows with missing target
        if 'sold_price' in df.columns:
            df = df.dropna(subset=['sold_price'])
        
        # Create target variables
        # Value: actual sold price (in Crore)
        y_value = df['sold_price'].values
        
        # Performance: composite score (create heuristic if not available)
        if 'overall_impact' in df.columns:
            y_performance = df['overall_impact'].values
        else:
            # Create synthetic performance score
            y_performance = np.random.uniform(50, 90, len(df))
        
        # Risk: inverse of consistency (or synthetic)
        if 'consistency_rating' in df.columns:
            y_risk = 1 - (df['consistency_rating'].values / 100)
        else:
            y_risk = np.random.uniform(0.2, 0.5, len(df))
        
        # Features
        X = df[feature_cols].values
        
        print(f"✅ Data loaded: {X.shape[0]} players, {X.shape[1]} features")
        
        return X, y_value, y_performance, y_risk
    
    def build_model(self, input_dim: int):
        """Initialize the model"""
        self.model = PlayerValueDNN(
            input_dim=input_dim,
            hidden_dims=self.config['hidden_dims'],
            dropout_rate=self.config['dropout_rate']
        ).to(self.device)
        
        print(f"🤖 Model initialized on {self.device}")
        print(f"   Input dim: {input_dim}")
        print(f"   Architecture: {self.config['hidden_dims']}")
    
    def train(self, X: np.ndarray, y_value: np.ndarray, 
              y_performance: np.ndarray, y_risk: np.ndarray):
        """Train the model"""
        
        # Split data
        X_train, X_val, y_val, y_perf_val, y_risk_val = train_test_split(
            X, y_value, y_performance, y_risk, 
            test_size=self.config['validation_split'],
            random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        # Create datasets
        train_dataset = IPLPlayerDataset(
            X_train_scaled, y_val, y_perf_val, y_risk_val
        )
        val_dataset = IPLPlayerDataset(
            X_val_scaled, y_val, y_perf_val, y_risk_val
        )
        
        # Create dataloaders
        train_loader = DataLoader(
            train_dataset, 
            batch_size=self.config['batch_size'],
            shuffle=True
        )
        val_loader = DataLoader(
            val_dataset, 
            batch_size=self.config['batch_size'],
            shuffle=False
        )
        
        # Loss and optimizer
        criterion = CombinedLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=self.config['learning_rate'])
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', factor=0.5, patience=5, verbose=True
        )
        
        # Training loop
        best_val_loss = float('inf')
        patience_counter = 0
        
        print(f"\n🚀 Starting training for {self.config['epochs']} epochs...")
        print(f"   Training samples: {len(train_dataset)}")
        print(f"   Validation samples: {len(val_dataset)}")
        print("-" * 70)
        
        for epoch in range(self.config['epochs']):
            # Training phase
            self.model.train()
            train_loss = 0.0
            
            for batch_features, batch_targets in tqdm(train_loader, desc=f"Epoch {epoch+1}/{self.config['epochs']}"):
                batch_features = batch_features.to(self.device)
                true_value, true_perf, true_risk = batch_targets
                true_value = true_value.to(self.device)
                true_perf = true_perf.to(self.device)
                true_risk = true_risk.to(self.device)
                
                # Forward pass
                optimizer.zero_grad()
                pred_value, pred_perf, pred_risk = self.model(batch_features)
                
                # Compute loss
                loss, loss_dict = criterion(
                    (pred_value, pred_perf, pred_risk),
                    (true_value, true_perf, true_risk)
                )
                
                # Backward pass
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
            
            avg_train_loss = train_loss / len(train_loader)
            
            # Validation phase
            self.model.eval()
            val_loss = 0.0
            
            with torch.no_grad():
                for batch_features, batch_targets in val_loader:
                    batch_features = batch_features.to(self.device)
                    true_value, true_perf, true_risk = batch_targets
                    true_value = true_value.to(self.device)
                    true_perf = true_perf.to(self.device)
                    true_risk = true_risk.to(self.device)
                    
                    pred_value, pred_perf, pred_risk = self.model(batch_features)
                    loss, _ = criterion(
                        (pred_value, pred_perf, pred_risk),
                        (true_value, true_perf, true_risk)
                    )
                    
                    val_loss += loss.item()
            
            avg_val_loss = val_loss / len(val_loader)
            
            # Print progress
            print(f"Epoch {epoch+1:3d}: Train Loss={avg_train_loss:.4f}, Val Loss={avg_val_loss:.4f}")
            
            # Learning rate scheduling
            scheduler.step(avg_val_loss)
            
            # Early stopping
            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
                patience_counter = 0
                # Save best model
                self.save_model("models/best_player_value_model.pth")
            else:
                patience_counter += 1
                if patience_counter >= self.config['early_stopping_patience']:
                    print(f"\n⏹️ Early stopping at epoch {epoch+1}")
                    break
        
        print("-" * 70)
        print(f"✅ Training completed! Best validation loss: {best_val_loss:.4f}")
    
    def save_model(self, path: str):
        """Save model and preprocessing objects"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save model
        self.model.save_model(path)
        
        # Save scaler
        scaler_path = path.replace('.pth', '_scaler.pkl')
        import pickle
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        # Save label encoders
        encoder_path = path.replace('.pth', '_encoders.json')
        encoders_data = {}
        for name, encoder in self.label_encoders.items():
            encoders_data[name] = list(encoder.classes_)
        with open(encoder_path, 'w') as f:
            json.dump(encoders_data, f)
        
        print(f"✅ Model artifacts saved to {path}")
    
    def load_model(self, model_path: str):
        """Load trained model and preprocessing objects"""
        self.model = PlayerValueDNN.load_model(model_path)
        self.model.to(self.device)
        
        # Load scaler
        scaler_path = model_path.replace('.pth', '_scaler.pkl')
        if os.path.exists(scaler_path):
            import pickle
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
        
        # Load label encoders
        encoder_path = model_path.replace('.pth', '_encoders.json')
        if os.path.exists(encoder_path):
            with open(encoder_path, 'r') as f:
                encoders_data = json.load(f)
                self.label_encoders = {}
                for name, classes in encoders_data.items():
                    le = LabelEncoder()
                    le.classes_ = np.array(classes)
                    self.label_encoders[name] = le
        
        print(f"✅ Model loaded from {model_path}")


def main():
    """Main training script"""
    config = {
        'batch_size': 32,
        'learning_rate': 0.001,
        'epochs': 100,
        'hidden_dims': [128, 64, 32],
        'dropout_rate': 0.3,
        'early_stopping_patience': 10,
        'validation_split': 0.2
    }
    
    pipeline = TrainingPipeline(config)
    
    # Load and prepare data
    csv_path = "IPL-AUCTION-STARTEGIC-SYSTEM-main/data/raw/2024_players_details.csv"
    
    if os.path.exists(csv_path):
        X, y_value, y_performance, y_risk = pipeline.prepare_data(csv_path)
        
        # Build and train model
        pipeline.build_model(input_dim=X.shape[1])
        pipeline.train(X, y_value, y_performance, y_risk)
        
        # Save final model
        pipeline.save_model("models/player_value_model.pth")
        
        print("\n🎉 Training pipeline completed successfully!")
    else:
        print(f"❌ Data file not found: {csv_path}")
        print("Please ensure the CSV file exists in the correct location.")


if __name__ == "__main__":
    main()
