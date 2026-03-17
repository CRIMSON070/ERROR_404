"""
Match Outcome Prediction Model (LSTM/Transformer)
Predicts win probability based on sequence of match events/features
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import os


class MatchSequenceDataset(Dataset):
    """Dataset for match sequence data"""
    
    def __init__(self, sequences, targets):
        self.sequences = torch.FloatTensor(sequences)
        self.targets = torch.FloatTensor(targets)
    
    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        return self.sequences[idx], self.targets[idx]


class MatchOutcomeLSTM(nn.Module):
    """
    LSTM-based model for match outcome prediction
    Architecture: LSTM → Dropout → Dense → Sigmoid
    """
    
    def __init__(self, input_dim, hidden_dim=128, num_layers=2, dropout=0.3):
        super(MatchOutcomeLSTM, self).__init__()
        
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=True
        )
        
        # Attention mechanism
        self.attention = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1)
        )
        
        # Fully connected layers
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim * 2, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(64, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.2),
            
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        # LSTM forward
        lstm_out, _ = self.lstm(x)
        
        # Attention weights
        attention_weights = self.attention(lstm_out)
        attention_weights = torch.softmax(attention_weights, dim=1)
        
        # Weighted sum
        context = torch.sum(lstm_out * attention_weights, dim=1)
        
        # Fully connected layers
        output = self.fc(context)
        
        return output


class MatchOutcomeTransformer(nn.Module):
    """
    Transformer-based model for match outcome prediction
    Alternative to LSTM for capturing long-range dependencies
    """
    
    def __init__(self, input_dim, d_model=128, nhead=8, num_layers=4, dropout=0.1):
        super(MatchOutcomeTransformer, self).__init__()
        
        # Input embedding
        self.input_embedding = nn.Linear(input_dim, d_model)
        
        # Positional encoding
        self.pos_encoder = PositionalEncoding(d_model, dropout)
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 4,
            dropout=dropout,
            activation='relu',
            batch_first=True
        )
        
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Global average pooling
        self.global_pool = nn.AdaptiveAvgPool1d(1)
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        # Embedding
        x = self.input_embedding(x)
        
        # Positional encoding
        x = self.pos_encoder(x)
        
        # Transformer encoder
        x = self.transformer_encoder(x)
        
        # Global pooling
        x = x.transpose(1, 2)  # (batch, features, seq)
        x = self.global_pool(x).squeeze(-1)
        
        # Classification
        output = self.classifier(x)
        
        return output


class PositionalEncoding(nn.Module):
    """Positional encoding for transformer"""
    
    def __init__(self, d_model, dropout=0.1, max_len=5000):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-np.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        
        self.register_buffer('pe', pe)
    
    def forward(self, x):
        x = x + self.pe[:, :x.size(1), :]
        return self.dropout(x)


def generate_synthetic_match_data(n_samples=5000, seq_length=10, feature_dim=15):
    """Generate synthetic match sequence data for training"""
    
    print(f"Generating {n_samples} synthetic match sequences...")
    
    sequences = []
    targets = []
    
    for _ in range(n_samples):
        # Generate sequence of match states (e.g., 10 overs)
        sequence = np.random.randn(seq_length, feature_dim)
        
        # Add realistic patterns
        for t in range(seq_length):
            # Momentum effect
            if t > 0:
                sequence[t] += 0.3 * sequence[t-1]
            
            # Random events (wickets, boundaries)
            if np.random.random() < 0.1:
                sequence[t] *= 1.5
        
        # Generate target based on sequence characteristics
        run_rate = np.mean(sequence[:, 0]) if sequence.shape[1] > 0 else 0
        wickets_lost = np.sum(sequence[:, 1] > 1.5) if sequence.shape[1] > 1 else 0
        momentum = np.mean(sequence[-3:, 2]) if sequence.shape[1] > 2 else 0
        
        # Win probability formula
        win_prob = 1 / (1 + np.exp(-(run_rate * 0.5 - wickets_lost * 0.3 + momentum * 0.2)))
        
        sequences.append(sequence)
        targets.append([win_prob])
    
    return np.array(sequences), np.array(targets)


def load_match_data_from_csv(csv_path, seq_length=10):
    """Load and prepare match data from CSV"""
    
    print(f"Loading match data from {csv_path}...")
    
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print("Match data not found, generating synthetic data...")
        return generate_synthetic_match_data()
    
    # Feature columns (adjust based on actual data)
    feature_cols = [
        'runs_scored', 'wickets_lost', 'overs_bowled', 'run_rate',
        'required_run_rate', 'balls_remaining', 'wickets_remaining'
    ]
    
    available_cols = [c for c in feature_cols if c in df.columns]
    
    if len(available_cols) < 4:
        print("Insufficient features, using synthetic data...")
        return generate_synthetic_match_data()
    
    # Create sequences
    sequences = []
    targets = []
    
    # Group by match and create sequences
    if 'match_id' in df.columns:
        for match_id in df['match_id'].unique():
            match_df = df[df['match_id'] == match_id].sort_values('over_number')
            
            if len(match_df) >= seq_length:
                seq = match_df[available_cols].values[:seq_length]
                
                # Target: match outcome (1 = win, 0 = loss)
                target = match_df['match_result'].iloc[-1] if 'match_result' in match_df.columns else 1
                
                sequences.append(seq)
                targets.append([target])
    
    if len(sequences) == 0:
        print("No valid sequences found, generating synthetic data...")
        return generate_synthetic_match_data()
    
    return np.array(sequences), np.array(targets)


def train_lstm_model(model, train_loader, val_loader, device, epochs=50, lr=0.001):
    """Train the LSTM model"""
    
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=5, factor=0.5)
    
    best_val_loss = float('inf')
    patience_counter = 0
    
    print(f"\nTraining LSTM model on {device}...")
    
    for epoch in range(epochs):
        # Training
        model.train()
        train_loss = 0.0
        
        for sequences, targets in train_loader:
            sequences, targets = sequences.to(device), targets.to(device)
            
            optimizer.zero_grad()
            outputs = model(sequences)
            loss = criterion(outputs, targets)
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            
            optimizer.step()
            train_loss += loss.item()
        
        train_loss /= len(train_loader)
        
        # Validation
        model.eval()
        val_loss = 0.0
        
        with torch.no_grad():
            for sequences, targets in val_loader:
                sequences, targets = sequences.to(device), targets.to(device)
                outputs = model(sequences)
                loss = criterion(outputs, targets)
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
            }, 'models/saved_models/match_outcome_model_best.pth')
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{epochs} - Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")
    
    return model


def evaluate_model(model, test_loader, device):
    """Evaluate model performance"""
    
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
    
    model.eval()
    all_predictions = []
    all_actuals = []
    all_probabilities = []
    
    with torch.no_grad():
        for sequences, targets in test_loader:
            sequences = sequences.to(device)
            outputs = model(sequences)
            
            probs = outputs.cpu().numpy()
            preds = (probs > 0.5).astype(int)
            
            all_probabilities.extend(probs.flatten())
            all_predictions.extend(preds.flatten())
            all_actuals.extend(targets.numpy().flatten())
    
    # Calculate metrics
    accuracy = accuracy_score(all_actuals, all_predictions)
    precision = precision_score(all_actuals, all_predictions)
    recall = recall_score(all_actuals, all_predictions)
    f1 = f1_score(all_actuals, all_predictions)
    auc_roc = roc_auc_score(all_actuals, all_probabilities)
    
    print("\n=== Match Outcome Model Evaluation ===")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print(f"AUC-ROC: {auc_roc:.4f}")
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'auc_roc': auc_roc
    }


def main():
    """Main training pipeline"""
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create directories
    os.makedirs('models/saved_models', exist_ok=True)
    
    # Load or generate data
    seq_length = 10  # Sequence length (e.g., 10 overs)
    feature_dim = 15  # Number of features per time step
    
    sequences, targets = load_match_data_from_csv(
        'data/raw/Ball_By_Ball_Match_Data.csv',
        seq_length=seq_length
    )
    
    print(f"Dataset shape: sequences={sequences.shape}, targets={targets.shape}")
    
    # Split data
    from sklearn.model_selection import train_test_split
    
    X_train, X_temp, y_train, y_temp = train_test_split(
        sequences, targets, test_size=0.3, random_state=42
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42
    )
    
    # Create dataloaders
    train_dataset = MatchSequenceDataset(X_train, y_train)
    val_dataset = MatchSequenceDataset(X_val, y_val)
    test_dataset = MatchSequenceDataset(X_test, y_test)
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    
    # Initialize model (choose LSTM or Transformer)
    model_type = 'lstm'  # or 'transformer'
    
    if model_type == 'transformer':
        model = MatchOutcomeTransformer(
            input_dim=feature_dim,
            d_model=128,
            nhead=8,
            num_layers=4
        ).to(device)
    else:
        model = MatchOutcomeLSTM(
            input_dim=feature_dim,
            hidden_dim=128,
            num_layers=2
        ).to(device)
    
    print(f"\nModel Architecture ({model_type.upper()}):")
    print(model)
    print(f"\nTotal parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Train model
    trained_model = train_lstm_model(
        model, train_loader, val_loader, device, epochs=50, lr=0.001
    )
    
    # Evaluate model
    metrics = evaluate_model(trained_model, test_loader, device)
    
    # Save model
    torch.save({
        'model_state_dict': trained_model.state_dict(),
        'model_type': model_type,
        'feature_dim': feature_dim,
        'seq_length': seq_length,
        'metrics': metrics
    }, 'models/saved_models/match_outcome_model_complete.pth')
    
    print("\n✅ Match outcome model training completed!")
    
    return trained_model, metrics


if __name__ == "__main__":
    model, metrics = main()
