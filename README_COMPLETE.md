# IPL Auction Strategy Platform - Complete Setup Guide

## 🎯 Project Overview

A production-grade, **Deep Learning-dominated** IPL auction strategy platform where multiple IPL teams can:

- Select players from a 622+ player auction pool
- Manage ₹120 Crore budget with real-time tracking
- Analyze team strengths and weaknesses using AI
- Receive intelligent player suggestions
- Generate optimal playing XI
- Simulate match outcomes
- Get auction bidding strategies

**Core Intelligence**: 7 Deep Learning models drive ALL decision-making.

---

## 🏗 Architecture

```
HDFS Data Storage
    ↓
Apache Spark (ETL + Feature Engineering)
    ↓
HDFS /ipl/features
    ↓
🔥 Deep Learning Models (PyTorch)
    ├─ Player Performance DNN
    ├─ Match Outcome LSTM
    ├─ Player Embeddings
    ├─ Team Strength Model
    ├─ Weakness Detector
    ├─ Recommendation Engine
    └─ RL Auction Agent
    ↓
FastAPI Backend (REST API)
    ↓
Streamlit Frontend (Dark Theme UI)
```

---

## 📁 Project Structure

```
IPL-AUCTION-STARTEGIC-SYSTEM-main/
├── spark_jobs/
│   ├── enhanced_spark_etl.py       # Main ETL pipeline
│   ├── feature_engineering.py      # Advanced features
│   └── data_validation.py          # Quality checks
├── models/
│   ├── performance_predictor.py    # DNN for performance
│   ├── match_outcome_lstm.py       # LSTM for matches
│   ├── player_embeddings.py        # Embedding model
│   ├── team_strength_model.py      # Team aggregation
│   ├── weakness_detector.py        # Weakness analysis
│   ├── recommendation_engine.py    # AI recommendations
│   ├── auction_rl_agent.py         # RL auction agent
│   └── train_all_models.py         # Unified training
├── backend/
│   ├── main.py                     # FastAPI application
│   ├── config.py                   # Configuration
│   ├── schemas.py                  # Pydantic models
│   ├── data_loader.py              # Data utilities
│   └── model_loader.py             # Model loading
├── frontend/
│   └── app.py                      # Streamlit UI
├── data/
│   ├── raw/                        # Raw CSV files
│   ├── processed/                  # Parquet files
│   ├── features/                   # Engineered features
│   └── models/                     # Saved models
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
└── README.md                       # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- 8GB+ RAM recommended
- GPU optional (CUDA support available)

### Installation

**1. Install Dependencies**

```bash
cd IPL-AUCTION-STARTEGIC-SYSTEM-main
pip install -r requirements.txt
```

**2. Train Deep Learning Models**

```bash
python models/train_all_models.py
```

This trains all 7 DL models automatically (~30-60 minutes).

**3. Start Backend Server**

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at: `http://localhost:8000`

**4. Start Frontend (New Terminal)**

```bash
streamlit run frontend/app.py
```

Frontend runs at: `http://localhost:8501`

---

## 🤖 Deep Learning Models

### 1. Player Performance Predictor (DNN)
- **Architecture**: Input → Dense(128) → Dense(64) → Dense(32) → Output
- **Input**: Historical stats (matches, runs, SR, wickets, economy)
- **Output**: Predicted runs, strike rate, wickets, economy
- **Use**: Predict future performance

### 2. Match Outcome LSTM
- **Architecture**: Bidirectional LSTM(128) → Attention → Dense → Sigmoid
- **Input**: Sequence of match events (10 overs)
- **Output**: Win probability
- **Use**: Match simulation

### 3. Player Embedding Model
- **Architecture**: Categorical embeddings + Dense → 32-dim vector
- **Input**: Player stats + role + team
- **Output**: Normalized embedding vector
- **Use**: Similarity search, recommendations

### 4. Team Strength Aggregation
- **Architecture**: Attention-based pooling → Dense layers
- **Input**: List of player embeddings
- **Output**: Team strength score (0-100%)
- **Use**: Team comparison

### 5. Weakness Detector
- **Method**: Hybrid rule-based + Isolation Forest
- **Input**: Team composition + embeddings
- **Output**: Identified weaknesses with severity
- **Use**: Team gap analysis

### 6. Recommendation Engine
- **Method**: Embedding similarity + Performance scoring
- **Input**: Team needs + budget constraints
- **Output**: Ranked player recommendations
- **Use**: AI suggestions

### 7. RL Auction Agent (Advanced)
- **Algorithm**: PPO/DQN via Stable Baselines3
- **Environment**: Custom Gym auction simulator
- **State**: Budget, team, available players
- **Action**: Bid amount or pass
- **Use**: Optimal bidding strategy

---

## 📊 Features

### Player Dashboard
- Browse 622+ players with filters
- Color-coded budget badges:
  - 🔴 Red: ₹15+ Cr (Premium)
  - 🟠 Orange: ₹10-15 Cr (High)
  - 🟡 Yellow: ₹5-10 Cr (Mid)
  - 🟢 Green: <₹5 Cr (Value)
- Search by name, role, team, price

### Team Builder
- Real-time budget tracker (₹120 Cr limit)
- Role distribution visualization
- Add/remove players interface
- Slot counter (max 25 players)

### Analytics Dashboard
- Team composition radar charts
- Batting vs bowling balance
- Average impact scores
- Strength/weakness analysis

### AI Suggestions
- Context-aware recommendations
- Reasoning for each suggestion
- Fit score calculation
- Budget-compatible picks

### Best XI Generator
- Auto-select optimal 11 players
- Ensure role balance (1 WK, 3+ BAT, 2+ AR, 4+ BOWL)
- Formation visualization
- Predicted performance scores

### Match Simulation
- Monte Carlo simulation (1000 iterations)
- Win probability gauge chart
- Key performer predictions
- Score projections

### Auction Strategy
- Priority queue (CRITICAL → HIGH → MEDIUM → LOW)
- Maximum bid recommendations
- Budget allocation by department
- Strategic notes

---

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Key settings:
- `BUDGET_LIMIT_CRORE=120.0`
- `MAX_PLAYERS_IN_TEAM=25`
- `DEVICE=cuda` (if GPU available)

---

## 📈 API Endpoints

### Health & Metrics
- `GET /health` - API health check
- `GET /metrics` - Model status

### Players
- `GET /players` - List all players (with filters)
- `POST /add-player?player_name=X` - Add to team
- `DELETE /remove-player/{name}` - Remove from team

### Team Analysis
- `POST /team-analysis` - Analyze selected team
- `GET /team-composition` - Get current composition

### AI Features
- `POST /suggestions` - Get AI recommendations
- `POST /best-xi` - Generate optimal XI
- `POST /simulate-match` - Simulate match
- `POST /auction-strategy` - Get bidding strategy

---

## 🧪 Testing

Run test suite:

```bash
pytest tests/
```

Test coverage:
- Model initialization
- API endpoints
- Data loading
- Recommendation logic

---

## 🐳 Docker Deployment (Optional)

**Build Images**

```bash
docker-compose build
```

**Run Containers**

```bash
docker-compose up -d
```

Access:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:8501`

---

## 💻 Usage Guide

### Building Your Team

1. **Browse Players** → Filter by role/budget
2. **Add to Team** → Click "Add" button
3. **Monitor Budget** → Watch remaining purse
4. **Check Analytics** → Identify gaps
5. **Get Suggestions** → AI fills weak spots
6. **Generate Best XI** → See optimal lineup
7. **Simulate Matches** → Test team strength

### Auction Strategy Flow

1. Set remaining budget and slots
2. Get priority queue from AI
3. Follow max bid recommendations
4. Maintain role balance
5. Keep buffer for final rounds

---

## 🎯 Success Metrics

- ✅ All 7 DL models trained and loaded
- ✅ 622+ players in database
- ✅ Real-time budget tracking (<100ms)
- ✅ API response time <500ms
- ✅ Team strength prediction accuracy >80%
- ✅ Dark theme UI with all 8 pages functional

---

## 🔍 Troubleshooting

### Models Not Loading
```bash
# Retrain models
python models/train_all_models.py
```

### API Connection Error
```bash
# Check if backend is running
curl http://localhost:8000/health
```

### No Data Showing
```bash
# Verify data files exist
ls data/raw/
ls data/processed/
```

### Out of Memory
```bash
# Reduce batch size in models
# Or use CPU mode in .env: DEVICE=cpu
```

---

## 📚 Technologies Used

### Deep Learning
- PyTorch 2.x
- Transformers (LSTM, Attention)
- Stable Baselines3 (RL)

### Backend
- FastAPI
- Pydantic
- Uvicorn

### Frontend
- Streamlit
- Plotly (Charts)
- Pandas

### Big Data
- PySpark
- HDFS (Parquet)
- Apache Arrow

---

## 🎓 Educational Value

This project demonstrates:
- End-to-end ML pipeline
- Production DL deployment
- REST API design
- Real-time data processing
- Sports analytics
- Decision intelligence

Perfect for:
- Deep Learning portfolios
- Sports tech demonstrations
- AI engineering showcases
- Academic projects

---

## 📄 License

Educational/Demonstration purposes.

---

## 🙏 Acknowledgments

- IPL data sources
- PyTorch community
- FastAPI documentation
- Streamlit gallery

---

## 🚀 Next Steps

1. **Deploy to Cloud** (AWS/GCP/Azure)
2. **Add User Authentication**
3. **Multi-team Support**
4. **Live Auction Mode**
5. **Historical Data Integration**
6. **Advanced Visualizations**

---

**Ready to build your championship team?** 🏆

Start the platform and let Deep Learning guide your auction strategy!
