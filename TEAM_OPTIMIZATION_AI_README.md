# 🔥 Team Optimization AI - Deep Learning Powered Module

## Overview

This module provides **Deep Learning-driven team evaluation and optimization** for the IPL Auction Strategy Platform. It uses a Multi-Task Deep Neural Network to predict player values, detect overpriced/undervalued players, and suggest optimal replacements.

---

## 🎯 Features

### 1. **Multi-Task DNN Model**
- **Architecture**: 128→64→32 fully connected layers with BatchNorm and Dropout
- **Predictions**:
  - Player's true market value (₹ Crore)
  - Performance score (0-100)
  - Risk score (0-1)

### 2. **Team-Level Analysis**
- **Efficiency Score**: `team_value / total_cost`
- **Total Predicted Value**: Sum of individual predicted values
- **Budget Spent**: Actual auction expenditure
- **Average Performance**: Team's average performance score

### 3. **Player Analysis**
- **Overpriced Detection**: Players where `cost > predicted_value`
- **Undervalued Detection**: Players where `value > cost`
- **Risk Assessment**: Based on consistency and historical performance

### 4. **Replacement Engine**
- Uses **player embeddings** for similarity matching
- Finds players with:
  - Lower price
  - Equal or better performance
  - Similar role/profile

---

## 📊 Deep Learning Architecture

### PlayerValueDNN

```python
Input (50 features)
    ↓
Linear(50 → 128) + BatchNorm + ReLU + Dropout
    ↓
Linear(128 → 64) + BatchNorm + ReLU + Dropout
    ↓
Linear(64 → 32) + BatchNorm + ReLU + Dropout
    ↓
    ├─→ Value Head: Linear(32 → 16 → 1) + Softplus
    ├─→ Performance Head: Linear(32 → 16 → 1) + Sigmoid × 100
    └─→ Risk Head: Linear(32 → 16 → 1) + Sigmoid
```

### Combined Loss Function

```python
loss = (value_weight × MSE_loss) + 
       (performance_weight × MSE_loss) + 
       (risk_weight × BCE_loss)
```

Default weights: `[1.0, 0.5, 0.3]`

---

## 🚀 Quick Start

### 1. Train the Model

```bash
cd IPL-AUCTION-STARTEGIC-SYSTEM-main
python models/training_pipeline.py
```

This will:
- Load player data from CSV
- Preprocess features
- Train the Multi-Task DNN
- Save model checkpoints

### 2. Start Backend Server

```bash
python run_backend.py
```

The server will load the trained model automatically on startup.

### 3. Launch Frontend

```bash
streamlit run frontend/app.py
```

Navigate to **"Team Optimization AI"** in the sidebar.

---

## 📁 File Structure

```
models/
├── player_value_model.py       # Multi-Task DNN architecture
├── training_pipeline.py         # Training script with DataLoader
├── team_optimizer.py            # Team analysis logic
├── player_embeddings.py         # Embedding network for similarity
└── best_player_value_model.pth  # Trained model checkpoint

backend/
├── main.py                      # FastAPI endpoints
└── schemas.py                   # Pydantic response schemas

frontend/
└── app.py                       # Streamlit UI with Team Optimization page
```

---

## 🔧 API Endpoints

### POST `/team-optimization`

**Request:**
```json
{
  "selected_players": [
    {"player_name": "MS Dhoni", "role": "Wicket-keeper", "sold_price": 12.0},
    ...
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "efficiency_score": 0.95,
    "total_predicted_value": 125.5,
    "total_budget_spent": 118.0,
    "average_performance": 72.3,
    "overpriced_players": [
      {
        "player_name": "Player A",
        "actual_price": 8.5,
        "predicted_value": 6.2,
        "risk_score": 0.65
      }
    ],
    "undervalued_players": [
      {
        "player_name": "Player B",
        "actual_price": 3.5,
        "predicted_value": 5.8,
        "risk_score": 0.25
      }
    ],
    "replacement_opportunities": [...],
    "recommendations": [...]
  }
}
```

### GET `/player-analysis/{player_name}`

Returns detailed analysis for a single player.

### GET `/replacement-suggestions?player_name=...`

Returns better alternatives for a specific player.

---

## 🎨 UI Features

### Team Optimization Page

1. **Summary Cards**
   - Team size
   - Budget spent
   - Budget remaining

2. **Performance Metrics**
   - Efficiency Score (gauge)
   - Predicted Team Value
   - Average Performance

3. **Visualizations**
   - Value vs Cost bar chart
   - Role distribution pie chart (in Analytics)

4. **Player Analysis**
   - Overpriced players (🔴 red cards)
   - Undervalued players (🟢 green cards)

5. **Replacement Suggestions**
   - Similar players with better value
   - Performance comparison
   - Risk scores

6. **AI Recommendations**
   - Actionable insights
   - Priority-based suggestions

---

## 🧠 Feature Engineering

### Input Features (50 dimensions)

**Numeric Features:**
- Matches played
- Runs scored
- Wickets taken
- Strike rate
- Economy rate
- Batting/Bowling average
- Centuries/Fifties
- Base price

**Categorical Features (Encoded):**
- Role (Batsman, Bowler, All-rounder, WK)
- Team
- Country
- Playing style

**Derived Features:**
- Impact score
- Consistency rating
- Value score
- Form index

---

## 📈 Training Process

### Data Pipeline

```
CSV → Feature Engineering → Scaling → Dataset → DataLoader → Model
```

### Training Configuration

```python
{
  'batch_size': 32,
  'learning_rate': 0.001,
  'epochs': 100,
  'hidden_dims': [128, 64, 32],
  'dropout_rate': 0.3,
  'early_stopping_patience': 10,
  'validation_split': 0.2
}
```

### Model Saving

- `best_player_value_model.pth` - Best validation loss checkpoint
- `*_scaler.pkl` - StandardScaler for features
- `*_encoders.json` - LabelEncoder mappings

---

## 💡 Design Principles

### ✅ DO (Followed)

- **DL-driven decisions**: All insights from neural network outputs
- **No rule-based logic**: Pure machine learning
- **Modular code**: Separate model, training, inference
- **Clean UI**: Professional dark theme
- **Real-time analysis**: Instant feedback

### ❌ DON'T (Avoided)

- Hard-coded thresholds
- Manual weight assignments
- Mixed concerns (UI/logic/model)
- Synchronous blocking operations

---

## 🔍 Technical Details

### Efficiency Score Calculation

```python
efficiency = team_predicted_value / total_actual_cost
```

- `> 1.0`: Team is undervalued (good!)
- `= 1.0`: Fair value
- `< 1.0`: Overpaid (needs improvement)

### Replacement Algorithm

1. Generate embedding for target player
2. Find similar players (cosine similarity)
3. Filter by:
   - Lower price
   - Similar/higher performance
   - Same role
4. Rank by value surplus

---

## 🛠️ Troubleshooting

### Model Not Found Error

**Error:** `Model file not found: player_value_model_final.pth`

**Solution:**
```bash
python models/training_pipeline.py
```

### Connection Error

**Error:** `Cannot connect to backend server`

**Solution:**
```bash
# Terminal 1
python run_backend.py

# Terminal 2 (after backend starts)
streamlit run frontend/app.py
```

### Timeout Error

**Error:** `Request timed out`

**Solution:**
- Reduce batch size in training
- Use GPU if available
- Increase timeout in requests

---

## 📊 Expected Output

### Sample Team Analysis

```
Team Size: 15/25
Budget Spent: ₹98.5 Cr
Budget Remaining: ₹21.5 Cr

📊 Performance Metrics:
- Efficiency Score: 1.08 (Good)
- Predicted Value: ₹106.3 Cr
- Avg Performance: 74.2/100

🔴 Overpriced Players (2):
- Player X: Overpriced by ₹3.2 Cr
- Player Y: Overpriced by ₹1.8 Cr

🟢 Undervalued Players (3):
- Player A: Surplus +₹2.1 Cr
- Player B: Surplus +₹1.5 Cr
- Player C: Surplus +₹0.8 Cr

💡 Recommendations:
✅ Great value picks in middle order
⚠️ Consider replacing overpriced bowler
💡 Strong batting lineup identified
```

---

## 🎯 Future Enhancements

1. **Ensemble Models**: Combine multiple DL models
2. **Time-series Analysis**: Player form trends
3. **Match-up Based**: Venue/opponent-specific predictions
4. **Auction Dynamics**: Real-time bidding strategies
5. **Injury Risk**: Fitness/durability prediction

---

## 📚 References

- **PyTorch Documentation**: https://pytorch.org/docs/
- **FastAPI Guide**: https://fastapi.tiangolo.com/
- **Streamlit Components**: https://docs.streamlit.io/

---

## 👨‍💻 Author

Built with ❤️ using PyTorch, FastAPI, and Streamlit for the IPL Auction Strategy Platform.

---

## 📄 License

Part of the IPL Auction Strategy Platform - Educational/Research use.
