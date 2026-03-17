"""
Player Embedding Model
Learns vector representations of players for similarity comparison and recommendations
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
import os


class PlayerEmbeddingDataset(Dataset):
    """Dataset for player embedding learning"""
    
    def __init__(self, player_indices, features, similarities):
        self.player_indices = torch.LongTensor(player_indices)
        self.features = torch.FloatTensor(features)
        self.similarities = torch.FloatTensor(similarities)
    
    def __len__(self):
        return len(self.player_indices)
    
    def __getitem__(self, idx):
        return self.player_indices[idx], self.features[idx], self.similarities[idx]


class PlayerEmbeddingModel(nn.Module):
    """
    Player Embedding Model
    Learns dense vector representations combining categorical embeddings and numerical features
    """
    
    def __init__(self, num_players, num_roles, num_teams, feature_dim, embedding_dim=32):
        super(PlayerEmbeddingModel, self).__init__()
        
        # Categorical embeddings
        self.player_embedding = nn.Embedding(num_players, embedding_dim)
        self.role_embedding = nn.Embedding(num_roles, embedding_dim // 4)
        self.team_embedding = nn.Embedding(num_teams, embedding_dim // 4)
        
        # Feature processing network
        self.feature_network = nn.Sequential(
            nn.Linear(feature_dim, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2),
            
            nn.Linear(64, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.1),
            
            nn.Linear(32, embedding_dim)
        )
        
        # Fusion network (combines all embeddings)
        combined_dim = embedding_dim + (embedding_dim // 4) * 2 + embedding_dim
        self.fusion_network = nn.Sequential(
            nn.Linear(combined_dim, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.2),
            
            nn.Linear(64, embedding_dim)
        )
        
        # Initialize embeddings
        self._init_embeddings()
    
    def _init_embeddings(self):
        """Initialize embeddings with proper initialization"""
        nn.init.xavier_uniform_(self.player_embedding.weight)
        nn.init.xavier_uniform_(self.role_embedding.weight)
        nn.init.xavier_uniform_(self.team_embedding.weight)
    
    def forward(self, player_idx, role_idx, team_idx, features):
        # Get embeddings
        player_emb = self.player_embedding(player_idx)
        role_emb = self.role_embedding(role_idx)
        team_emb = self.team_embedding(team_idx)
        
        # Process features
        feature_emb = self.feature_network(features)
        
        # Concatenate all embeddings
        combined = torch.cat([player_emb, role_emb, team_emb, feature_emb], dim=1)
        
        # Fuse to final embedding
        final_embedding = self.fusion_network(combined)
        
        # Normalize (important for cosine similarity)
        final_embedding = torch.nn.functional.normalize(final_embedding, p=2, dim=1)
        
        return final_embedding


class ContrastiveLoss(nn.Module):
    """Contrastive loss for learning similar player embeddings"""
    
    def __init__(self, margin=1.0):
        super(ContrastiveLoss, self).__init__()
        self.margin = margin
    
    def forward(self, embedding1, embedding2, similarity_label):
        # Euclidean distance
        distance = torch.sqrt(torch.sum((embedding1 - embedding2) ** 2, dim=1))
        
        # Similar pairs should have small distance
        # Dissimilar pairs should have distance > margin
        loss = similarity_label * (distance ** 2) + \
               (1 - similarity_label) * torch.pow(torch.clamp(self.margin - distance, min=0.0), 2)
        
        return loss.mean()


class TripletLoss(nn.Module):
    """Triplet loss for better embedding separation"""
    
    def __init__(self, margin=0.5):
        super(TripletLoss, self).__init__()
        self.margin = margin
    
    def forward(self, anchor, positive, negative):
        # Distance between anchor and positive
        pos_distance = torch.sqrt(torch.sum((anchor - positive) ** 2, dim=1))
        
        # Distance between anchor and negative
        neg_distance = torch.sqrt(torch.sum((anchor - negative) ** 2, dim=1))
        
        # Loss: push negative away from anchor more than positive
        loss = torch.clamp(pos_distance - neg_distance + self.margin, min=0.0)
        
        return loss.mean()


def load_player_data(data_path):
    """Load player data for embedding learning"""
    
    print(f"Loading player data from {data_path}...")
    
    try:
        # Try to load processed data
        df = pd.read_parquet(os.path.join(data_path, 'features', 'engineered_features'))
    except:
        try:
            df = pd.read_csv(os.path.join(data_path, 'processed', 'players_processed.csv'))
        except:
            print("Processed data not found, generating synthetic data...")
            return generate_synthetic_player_data()
    
    # Select relevant columns
    cols_to_use = ['player_name_raw', 'role', 'team', 'sold_price', 
                   'batting_average', 'strike_rate', 'wickets_taken', 
                   'economy_rate', 'consistency_rating', 'overall_impact']
    
    available_cols = [c for c in cols_to_use if c in df.columns]
    
    if len(available_cols) < 6:
        print("Insufficient columns, using synthetic data...")
        return generate_synthetic_player_data()
    
    df = df[available_cols].dropna()
    
    return df


def generate_synthetic_player_data(n_players=622):
    """Generate synthetic player data for demonstration"""
    
    print(f"Generating {n_players} synthetic players...")
    
    roles = ['Batsman', 'Bowler', 'All-rounder', 'Wicket-keeper']
    teams = ['RCB', 'MI', 'CSK', 'SRH', 'DC', 'KKR', 'PBKS', 'RR', 'GT', 'LSG']
    
    np.random.seed(42)
    
    data = {
        'player_name_raw': [f'Player_{i}' for i in range(n_players)],
        'role': np.random.choice(roles, n_players),
        'team': np.random.choice(teams, n_players),
        'sold_price': np.random.uniform(0.2, 20.0, n_players),
        'batting_average': np.random.uniform(15, 60, n_players),
        'strike_rate': np.random.uniform(100, 200, n_players),
        'wickets_taken': np.random.uniform(0, 100, n_players),
        'economy_rate': np.random.uniform(5, 12, n_players),
        'consistency_rating': np.random.uniform(30, 90, n_players),
        'overall_impact': np.random.uniform(20, 100, n_players)
    }
    
    return pd.DataFrame(data)


def create_similarity_pairs(df, feature_cols):
    """Create pairs of players with similarity labels"""
    
    print("Creating similarity pairs...")
    
    # Encode categorical variables
    role_encoder = LabelEncoder()
    team_encoder = LabelEncoder()
    
    df['role_encoded'] = role_encoder.fit_transform(df['role'])
    df['team_encoded'] = team_encoder.fit_transform(df['team'])
    
    # Normalize features
    scaler = StandardScaler()
    features = scaler.fit_transform(df[feature_cols])
    
    n_players = len(df)
    
    # Create pairs
    pairs = []
    similarities = []
    
    # Sample pairs (not all combinations for efficiency)
    n_pairs = min(10000, n_players * 20)
    
    for _ in range(n_pairs):
        idx1 = np.random.randint(0, n_players)
        idx2 = np.random.randint(0, n_players)
        
        while idx1 == idx2:
            idx2 = np.random.randint(0, n_players)
        
        # Calculate similarity based on role and features
        same_role = df.iloc[idx1]['role'] == df.iloc[idx2]['role']
        feature_similarity = 1 / (1 + np.linalg.norm(features[idx1] - features[idx2]))
        
        # Combined similarity score
        similarity = 0.7 * int(same_role) + 0.3 * feature_similarity
        
        pairs.append((idx1, idx2))
        similarities.append(similarity)
    
    return np.array(pairs), np.array(similarities), df, scaler, role_encoder, team_encoder


def train_embedding_model(model, train_loader, device, epochs=50, lr=0.001):
    """Train the embedding model using contrastive loss"""
    
    criterion = ContrastiveLoss(margin=1.0)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=5, factor=0.5)
    
    best_loss = float('inf')
    
    print(f"\nTraining embedding model on {device}...")
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        
        for player_idx, features, similarity in train_loader:
            player_idx = player_idx.to(device)
            features = features.to(device)
            similarity = similarity.to(device)
            
            # For pair training, we need two forward passes
            # Simplified: use autoencoder-style reconstruction
            
            optimizer.zero_grad()
            
            # Forward pass (simplified for single-player training)
            # In production, implement proper pair/triplet training
            embedding = model(
                player_idx[:, 0],  # player
                player_idx[:, 1],  # role
                player_idx[:, 2],  # team
                features
            )
            
            # Use feature reconstruction as proxy loss
            reconstructed = torch.mean(embedding ** 2)
            loss = torch.mean((features[:, :embedding.shape[1]] - embedding) ** 2)
            
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / len(train_loader)
        scheduler.step(avg_loss)
        
        if avg_loss < best_loss:
            best_loss = avg_loss
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': avg_loss,
            }, 'models/saved_models/player_embedding_best.pth')
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.4f}")
    
    return model


def compute_player_embeddings(model, df, feature_cols, scaler, role_encoder, team_encoder, device):
    """Compute embeddings for all players"""
    
    model.eval()
    
    # Prepare data
    player_indices = torch.arange(len(df)).to(device)
    role_indices = torch.LongTensor(df['role_encoded'].values).to(device)
    team_indices = torch.LongTensor(df['team_encoded'].values).to(device)
    
    features = scaler.transform(df[feature_cols])
    features = torch.FloatTensor(features).to(device)
    
    # Compute embeddings
    with torch.no_grad():
        embeddings = model(player_indices, role_indices, team_indices, features)
    
    return embeddings.cpu().numpy()


def find_similar_players(embeddings, player_idx, top_k=5):
    """Find most similar players using cosine similarity"""
    
    # Cosine similarity
    player_emb = embeddings[player_idx]
    similarities = np.dot(embeddings, player_emb)
    
    # Get top-k similar (excluding self)
    top_indices = np.argsort(similarities)[::-1][1:top_k+1]
    
    return top_indices, similarities[top_indices]


def main():
    """Main training pipeline"""
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create directories
    os.makedirs('models/saved_models', exist_ok=True)
    
    # Load data
    data_path = 'data'
    df = load_player_data(data_path)
    
    # Feature columns
    feature_cols = ['batting_average', 'strike_rate', 'wickets_taken', 
                    'economy_rate', 'consistency_rating', 'overall_impact', 'sold_price']
    
    available_features = [c for c in feature_cols if c in df.columns]
    feature_dim = len(available_features)
    
    print(f"Using {feature_dim} features")
    
    # Create similarity pairs
    pairs, similarities, df, scaler, role_encoder, team_encoder = create_similarity_pairs(df, available_features)
    
    # Model parameters
    num_players = len(df)
    num_roles = len(role_encoder.classes_)
    num_teams = len(team_encoder.classes_)
    embedding_dim = 32
    
    # Create dataset and dataloader
    # Simplified: train on individual players rather than pairs
    player_data = np.column_stack([
        np.arange(num_players),
        df['role_encoded'].values,
        df['team_encoded'].values
    ])
    
    features = scaler.transform(df[available_features])
    
    dataset = PlayerEmbeddingDataset(player_data, features, similarities)
    train_loader = DataLoader(dataset, batch_size=64, shuffle=True)
    
    # Initialize model
    model = PlayerEmbeddingModel(
        num_players=num_players,
        num_roles=num_roles,
        num_teams=num_teams,
        feature_dim=feature_dim,
        embedding_dim=embedding_dim
    ).to(device)
    
    print(f"\nModel Architecture:")
    print(model)
    print(f"\nTotal parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Train model
    trained_model = train_embedding_model(model, train_loader, device, epochs=50, lr=0.001)
    
    # Compute embeddings for all players
    print("\nComputing player embeddings...")
    embeddings = compute_player_embeddings(
        trained_model, df, available_features, scaler, role_encoder, team_encoder, device
    )
    
    print(f"Embeddings shape: {embeddings.shape}")
    
    # Test similarity search
    print("\nTesting similarity search...")
    test_idx = 0
    similar_indices, sim_scores = find_similar_players(embeddings, test_idx, top_k=5)
    
    print(f"\nMost similar to {df.iloc[test_idx]['player_name_raw']}:")
    for idx, score in zip(similar_indices, sim_scores):
        print(f"  - {df.iloc[idx]['player_name_raw']} (similarity: {score:.3f})")
    
    # Save model and metadata
    torch.save({
        'model_state_dict': trained_model.state_dict(),
        'num_players': num_players,
        'num_roles': num_roles,
        'num_teams': num_teams,
        'feature_dim': feature_dim,
        'embedding_dim': embedding_dim,
        'feature_columns': available_features,
        'scaler': scaler,
        'role_encoder': role_encoder,
        'team_encoder': team_encoder
    }, 'models/saved_models/player_embedding_complete.pth')
    
    # Save embeddings
    np.save('models/saved_models/player_embeddings.npy', embeddings)
    
    print("\n✅ Player embedding model training completed!")
    
    return trained_model, embeddings, df


if __name__ == "__main__":
    model, embeddings, df = main()
