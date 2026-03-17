"""
Player Performance Prediction Model (Deep Neural Network)
Predicts player performance metrics: runs, strike rate, wickets, economy
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import os

class PlayerPerformanceDataset(Dataset):
    """PyTorch Dataset for player performance data"""
    
    def __init__(self, features, targets):
        self.features = torch.FloatTensor(features)
        self.targets = torch.FloatTensor(targets)
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        return self.features[idx], self.targets[idx]


class PlayerPerformanceDNN(nn.Module):
    """
    Deep Neural Network for multi-output player performance prediction
    Architecture: Input → Dense(128) → Dense(64) → Dense(32) → Output
    """
    
    def __init__(self, input_dim, output_dim=4):
        super(PlayerPerformanceDNN, self).__init__()
        
        self.network = nn.Sequential(
            # Layer 1: 128 neurons
            nn.Linear(input_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            # Layer 2: 64 neurons
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2),
            
            # Layer 3: 32 neurons
            nn.Linear(64, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.1),
            
            # Output layer
            nn.Linear(32, output_dim)
        )
    
    def forward(self, x):
        return self.network(x)


class MultiTaskLoss(nn.Module):
    """Multi-task loss function with learnable weights"""
    
    def __init__(self, num_tasks=4):
        super(MultiTaskLoss, self).__init__()
        self.log_vars = nn.Parameter(torch.zeros(num_tasks))
        self.mse = nn.MSELoss()
    
    def forward(self, outputs, targets):
        precision = torch.exp(-self.log_vars)
        loss = 0
        for i in range(len(outputs)):
            loss += precision[i] * self.mse(outputs[i], targets[i])
            loss += self.log_vars[i]
        return loss


def load_and_preprocess_data(data_path):
    """Load and preprocess data for training"""
    print(f"Loading data from {data_path}...")
    
    # Try to load from parquet, fallback to CSV
    try:
        if os.path.exists(os.path.join(data_path, 'engineered_features')):
            df = pd.read_parquet(os.path.join(data_path, 'engineered_features'))
        else:
            df = pd.read_csv(os.path.join(data_path, 'players_processed.csv'))
    except:
        # Generate synthetic data for demonstration
        print("Generating synthetic training data...")
        n_samples = 1000
        df = pd.DataFrame({
            'batting_average': np.random.uniform(15, 60, n_samples),
            'strike_rate': np.random.uniform(100, 200, n_samples),
            'wickets_taken': np.random.uniform(0, 100, n_samples),
            'economy_rate': np.random.uniform(5, 12, n_samples),
            'consistency_rating': np.random.uniform(30, 90, n_samples),
            'overall_impact': np.random.uniform(20, 100, n_samples),
            'value_for_money': np.random.uniform(0.5, 5, n_samples),
            'matches_played': np.random.uniform(10, 200, n_samples),
            'runs_scored': np.random.uniform(500, 5000, n_samples),
            'performance_index': np.random.uniform(30, 150, n_samples)
        })
    
    # Select feature columns
    feature_cols = [
        'batting_average', 'strike_rate', 'wickets_taken', 'economy_rate',
        'consistency_rating', 'overall_impact', 'value_for_money',
        'matches_played', 'runs_scored', 'performance_index'
    ]
    
    # Filter available columns
    available_features = [c for c in feature_cols if c in df.columns]
    
    if len(available_features) < 5:
        print(f"Warning: Only {len(available_features)} features available")
        # Create minimum viable features
        for col in ['batting_average', 'strike_rate', 'consistency_rating']:
            if col not in df.columns:
                df[col] = np.random.uniform(20, 80, len(df))
    
    # Target columns (what we want to predict)
    target_cols = ['runs_scored', 'strike_rate', 'wickets_taken', 'economy_rate']
    
    # Ensure targets exist
    for col in target_cols:
        if col not in df.columns:
            if col == 'runs_scored':
                df[col] = np.random.uniform(500, 5000, len(df))
            elif col == 'wickets_taken':
                df[col] = np.random.uniform(0, 100, len(df))
    
    # Handle missing values
    df = df.fillna(df.mean(numeric_only=True))
    
    X = df[available_features].values
    y = df[target_cols].values
    
    # Normalize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Normalize targets
    target_scaler = StandardScaler()
    y_scaled = target_scaler.fit_transform(y)
    
    return X_scaled, y_scaled, scaler, target_scaler, available_features, target_cols


def train_model(model, train_loader, val_loader, device, epochs=100, lr=0.001):
    """Train the DNN model"""
    
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=10, factor=0.5)
    
    best_val_loss = float('inf')
    patience_counter = 0
    max_patience = 20
    
    print(f"\nStarting training on {device}...")
    print(f"Training samples: {len(train_loader.dataset)}")
    print(f"Validation samples: {len(val_loader.dataset)}\n")
    
    for epoch in range(epochs):
        # Training phase
        model.train()
        train_loss = 0.0
        
        for features, targets in train_loader:
            features, targets = features.to(device), targets.to(device)
            
            optimizer.zero_grad()
            outputs = model(features)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        train_loss /= len(train_loader)
        
        # Validation phase
        model.eval()
        val_loss = 0.0
        
        with torch.no_grad():
            for features, targets in val_loader:
                features, targets = features.to(device), targets.to(device)
                outputs = model(features)
                loss = criterion(outputs, targets)
                val_loss += loss.item()
        
        val_loss /= len(val_loader)
        scheduler.step(val_loss)
        
        # Early stopping check
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            # Save best model
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': val_loss,
            }, 'models/saved_models/performance_model_best.pth')
        else:
            patience_counter += 1
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{epochs} - Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, LR: {optimizer.param_groups[0]['lr']:.6f}")
        
        if patience_counter >= max_patience:
            print(f"Early stopping at epoch {epoch+1}")
            break
    
    return model


def evaluate_model(model, test_loader, device, target_scaler):
    """Evaluate model performance"""
    
    model.eval()
    all_predictions = []
    all_actuals = []
    
    with torch.no_grad():
        for features, targets in test_loader:
            features = features.to(device)
            outputs = model(features)
            all_predictions.append(outputs.cpu().numpy())
            all_actuals.append(targets.numpy())
    
    predictions = np.vstack(all_predictions)
    actuals = np.vstack(all_actuals)
    
    # Denormalize
    predictions_denorm = target_scaler.inverse_transform(predictions)
    actuals_denorm = target_scaler.inverse_transform(actuals)
    
    # Calculate metrics
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    
    metrics = {}
    target_names = ['Runs', 'Strike Rate', 'Wickets', 'Economy']
    
    print("\n=== Model Evaluation ===")
    for i, name in enumerate(target_names):
        mae = mean_absolute_error(actuals_denorm[:, i], predictions_denorm[:, i])
        rmse = np.sqrt(mean_squared_error(actuals_denorm[:, i], predictions_denorm[:, i]))
        r2 = r2_score(actuals_denorm[:, i], predictions_denorm[:, i])
        
        metrics[name.lower().replace(' ', '_')] = {
            'mae': mae,
            'rmse': rmse,
            'r2': r2
        }
        
        print(f"{name}: MAE={mae:.2f}, RMSE={rmse:.2f}, R²={r2:.4f}")
    
    return metrics


def save_model_artifacts(model, scaler, target_scaler, feature_names, metadata_path):
    """Save complete model artifacts for inference"""
    
    artifacts = {
        'model_state_dict': model.state_dict(),
        'feature_scaler': scaler,
        'target_scaler': target_scaler,
        'feature_names': feature_names,
        'input_dim': len(feature_names),
        'output_dim': 4
    }
    
    torch.save(artifacts, metadata_path)
    print(f"\nModel artifacts saved to {metadata_path}")


def main():
    """Main training pipeline"""
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create directories
    os.makedirs('models/saved_models', exist_ok=True)
    
    # Load and preprocess data
    data_path = 'data'
    X, y, feature_scaler, target_scaler, feature_names, target_names = load_and_preprocess_data(data_path)
    
    print(f"Features: {feature_names}")
    print(f"Targets: {target_names}")
    print(f"Dataset shape: X={X.shape}, y={y.shape}")
    
    # Split data
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)
    
    # Create datasets and dataloaders
    train_dataset = PlayerPerformanceDataset(X_train, y_train)
    val_dataset = PlayerPerformanceDataset(X_val, y_val)
    test_dataset = PlayerPerformanceDataset(X_test, y_test)
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    
    # Initialize model
    input_dim = X.shape[1]
    model = PlayerPerformanceDNN(input_dim=input_dim, output_dim=4).to(device)
    
    print(f"\nModel Architecture:")
    print(model)
    print(f"\nTotal parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Train model
    trained_model = train_model(model, train_loader, val_loader, device, epochs=100, lr=0.001)
    
    # Evaluate model
    metrics = evaluate_model(trained_model, test_loader, device, target_scaler)
    
    # Save model artifacts
    save_model_artifacts(
        trained_model, 
        feature_scaler, 
        target_scaler, 
        feature_names,
        'models/saved_models/performance_model_complete.pth'
    )
    
    print("\n✅ Training completed successfully!")
    
    return trained_model, metrics


if __name__ == "__main__":
    model, metrics = main()
