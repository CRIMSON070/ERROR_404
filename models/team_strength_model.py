"""
Team Strength Aggregation Model
Aggregates player embeddings to compute overall team strength score
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd


class TeamStrengthDataset(Dataset):
    """Dataset for team strength learning"""
    
    def __init__(self, team_embeddings, team_strengths):
        self.team_embeddings = torch.FloatTensor(team_embeddings)
        self.team_strengths = torch.FloatTensor(team_strengths)
    
    def __len__(self):
        return len(self.team_embeddings)
    
    def __getitem__(self, idx):
        return self.team_embeddings[idx], self.team_strengths[idx]


class TeamStrengthModel(nn.Module):
    """
    Team Strength Model using attention-based aggregation
    Input: List of player embeddings → Attention → Team Score
    """
    
    def __init__(self, player_embedding_dim=32, hidden_dim=64):
        super(TeamStrengthModel, self).__init__()
        
        # Attention mechanism for weighted aggregation
        self.attention_network = nn.Sequential(
            nn.Linear(player_embedding_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1)
        )
        
        # Team strength prediction network
        self.strength_network = nn.Sequential(
            nn.Linear(player_embedding_dim * 2 + 5, 128),  # +5 for additional team features
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2),
            
            nn.Linear(64, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.1),
            
            nn.Linear(32, 1),
            nn.Sigmoid()  # Output: 0-1 team strength score
        )
    
    def attention_aggregate(self, player_embeddings):
        """
        Aggregate player embeddings using attention
        player_embeddings: (batch_size, num_players, embedding_dim)
        """
        # Compute attention weights
        attention_weights = self.attention_network(player_embeddings)  # (batch, num_players, 1)
        attention_weights = torch.softmax(attention_weights, dim=1)
        
        # Weighted sum
        team_embedding = torch.sum(player_embeddings * attention_weights, dim=1)
        
        return team_embedding, attention_weights
    
    def forward(self, player_embeddings, team_features=None):
        """
        Forward pass
        player_embeddings: (batch_size, num_players, embedding_dim)
        team_features: (batch_size, 5) - additional team features
        """
        # Aggregate player embeddings
        team_emb, attention_weights = self.attention_aggregate(player_embeddings)
        
        # Add team composition features
        if team_features is not None:
            combined = torch.cat([team_emb, team_features], dim=1)
        else:
            combined = team_emb
        
        # Predict team strength
        strength_score = self.strength_network(combined)
        
        return strength_score, attention_weights


def generate_synthetic_team_data(n_teams=100, players_per_team=25, embedding_dim=32):
    """Generate synthetic team data for training"""
    
    print(f"Generating {n_teams} synthetic teams...")
    
    team_embeddings = []
    team_strengths = []
    
    for _ in range(n_teams):
        # Generate random player embeddings
        team_emb = np.random.randn(players_per_team, embedding_dim)
        
        # Normalize embeddings
        team_emb = team_emb / np.linalg.norm(team_emb, axis=1, keepdims=True)
        
        # Calculate team strength based on embedding quality
        avg_quality = np.mean(np.linalg.norm(team_emb, axis=1))
        variance = np.var(np.linalg.norm(team_emb, axis=1))
        
        # Strength formula (higher average, lower variance = better)
        strength = 0.7 * avg_quality + 0.3 * (1 - min(variance, 1))
        strength = min(max(strength, 0), 1)  # Clamp to [0, 1]
        
        team_embeddings.append(team_emb)
        team_strengths.append([strength])
    
    return np.array(team_embeddings), np.array(team_strengths)


def create_team_from_players(df, player_embeddings, n_players=25):
    """Create a team by selecting players from dataframe"""
    
    if len(df) < n_players:
        return None, None
    
    # Randomly select players
    selected_indices = np.random.choice(len(df), size=n_players, replace=False)
    
    team_df = df.iloc[selected_indices].reset_index(drop=True)
    team_embeddings = player_embeddings[selected_indices]
    
    # Calculate team strength (simplified)
    avg_impact = team_df['overall_impact'].mean() if 'overall_impact' in team_df.columns else 50
    avg_consistency = team_df['consistency_rating'].mean() if 'consistency_rating' in team_df.columns else 50
    
    strength_score = (avg_impact + avg_consistency) / 200.0  # Normalize to [0, 1]
    
    return team_embeddings, np.array([strength_score])


def train_team_model(model, train_loader, val_loader, device, epochs=100, lr=0.001):
    """Train the team strength model"""
    
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=10, factor=0.5)
    
    best_val_loss = float('inf')
    
    print(f"\nTraining team strength model on {device}...")
    
    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        
        for team_emb, strengths in train_loader:
            team_emb, strengths = team_emb.to(device), strengths.to(device)
            
            optimizer.zero_grad()
            
            # Forward pass
            predicted_strength, _ = model(team_emb)
            
            loss = criterion(predicted_strength, strengths)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        train_loss /= len(train_loader)
        
        # Validation
        model.eval()
        val_loss = 0.0
        
        with torch.no_grad():
            for team_emb, strengths in val_loader:
                team_emb, strengths = team_emb.to(device), strengths.to(device)
                predicted_strength, _ = model(team_emb)
                loss = criterion(predicted_strength, strengths)
                val_loss += loss.item()
        
        val_loss /= len(val_loader)
        scheduler.step(val_loss)
        
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': val_loss,
            }, 'models/saved_models/team_strength_best.pth')
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{epochs} - Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")
    
    return model


def evaluate_team_model(model, test_loader, device):
    """Evaluate team strength model"""
    
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    
    model.eval()
    all_predictions = []
    all_actuals = []
    
    with torch.no_grad():
        for team_emb, strengths in test_loader:
            team_emb = team_emb.to(device)
            predicted_strength, _ = model(team_emb)
            
            all_predictions.extend(predicted_strength.cpu().numpy().flatten())
            all_actuals.extend(strengths.numpy().flatten())
    
    # Calculate metrics
    mae = mean_absolute_error(all_actuals, all_predictions)
    rmse = np.sqrt(mean_squared_error(all_actuals, all_predictions))
    r2 = r2_score(all_actuals, all_predictions)
    
    print("\n=== Team Strength Model Evaluation ===")
    print(f"MAE: {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R²: {r2:.4f}")
    
    return {'mae': mae, 'rmse': rmse, 'r2': r2}


def predict_team_strength(model, team_embeddings, device):
    """Predict strength for a given team"""
    
    model.eval()
    
    if len(team_embeddings.shape) == 2:
        team_embeddings = team_embeddings.unsqueeze(0)
    
    team_embeddings = team_embeddings.to(device)
    
    with torch.no_grad():
        strength, attention_weights = model(team_embeddings)
    
    return strength.item(), attention_weights.cpu().numpy()


def main():
    """Main training pipeline"""
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create directories
    os.makedirs('models/saved_models', exist_ok=True)
    
    # Generate or load data
    embedding_dim = 32
    players_per_team = 25
    
    # Try to load player embeddings
    try:
        player_embeddings = np.load('models/saved_models/player_embeddings.npy')
        print(f"Loaded {len(player_embeddings)} player embeddings")
        
        # Load player dataframe
        df = pd.read_parquet('data/features/engineered_features')
    except:
        print("Player embeddings not found, generating synthetic data...")
        df = pd.DataFrame({'overall_impact': np.random.uniform(20, 100, 622)})
        player_embeddings = np.random.randn(622, embedding_dim)
    
    # Generate team data
    n_teams = 1000
    team_embeddings_list = []
    team_strengths_list = []
    
    for _ in range(n_teams):
        team_emb, strength = create_team_from_players(df, player_embeddings, players_per_team)
        if team_emb is not None:
            team_embeddings_list.append(team_emb)
            team_strengths_list.append(strength)
    
    team_embeddings = np.array(team_embeddings_list)
    team_strengths = np.array(team_strengths_list)
    
    print(f"Generated {len(team_embeddings)} teams")
    
    # Split data
    from sklearn.model_selection import train_test_split
    
    X_train, X_temp, y_train, y_temp = train_test_split(
        team_embeddings, team_strengths, test_size=0.3, random_state=42
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42
    )
    
    # Create dataloaders
    train_dataset = TeamStrengthDataset(X_train, y_train)
    val_dataset = TeamStrengthDataset(X_val, y_val)
    test_dataset = TeamStrengthDataset(X_test, y_test)
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    
    # Initialize model
    model = TeamStrengthModel(
        player_embedding_dim=embedding_dim,
        hidden_dim=64
    ).to(device)
    
    print(f"\nModel Architecture:")
    print(model)
    print(f"\nTotal parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Train model
    trained_model = train_team_model(
        model, train_loader, val_loader, device, epochs=100, lr=0.001
    )
    
    # Evaluate model
    metrics = evaluate_team_model(trained_model, test_loader, device)
    
    # Save model
    torch.save({
        'model_state_dict': trained_model.state_dict(),
        'metrics': metrics,
        'embedding_dim': embedding_dim
    }, 'models/saved_models/team_strength_complete.pth')
    
    print("\n✅ Team strength model training completed!")
    
    return trained_model, metrics


if __name__ == "__main__":
    model, metrics = main()
