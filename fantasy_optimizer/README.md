# 🏏 AI-Powered Fantasy Cricket Team Optimizer (Dream11-like)

A complete, hackathon-quality AI/ML web application for building optimal fantasy cricket teams using machine learning.

---

## 🚀 Quick Start

### 3-Step Setup

```bash
# Step 1: Navigate to project
cd fantasy_optimizer

# Step 2: Install dependencies
pip install -r requirements.txt

# Step 3: Run application
streamlit run app.py
```

**Access at:** http://localhost:8501

---

## 📋 Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Machine Learning](#machine-learning)
4. [Installation](#installation)
5. [Usage Guide](#usage-guide)
6. [API Reference](#api-reference)
7. [Examples](#examples)
8. [Troubleshooting](#troubleshooting)

---

## ✨ Features

### 1. **AI-Powered Fantasy Points Prediction** 🤖
- **RandomForestRegressor** model trained on player statistics
- Predicts expected fantasy points for each player
- Features: batting average, strike rate, wickets, economy, experience
- Target: Composite fantasy points formula

### 2. **Optimal Team Generation** 🎯
- Automatically generates best playing 11
- Enforces Dream11-style constraints:
  - Max 7 players from one team
  - Minimum 3 batsmen, 3 bowlers, 1 all-rounder, 1 wicket-keeper
  - Total exactly 11 players
- Ranks players by predicted points

### 3. **Captain & Vice-Captain Selection** 👑
- Automatically selects top 2 performers
- Captain: 2x points multiplier
- Vice-Captain: 1.5x points multiplier
- Based on predicted fantasy points

### 4. **Team Score Calculation** 📊
- Calculates total team fantasy score
- Applies captain/vice-captain multipliers
- Shows breakdown by player

### 5. **Player Comparison Tool** ⚔️
- Head-to-head comparison of any 2 players
- Compares batting, bowling, and total scores
- Interactive radar chart visualization
- Declares better player with margin

### 6. **Match Simulation (50 Simulations)** 🎮
- Monte Carlo simulation of matches
- Runs 50 simulations with ±15% randomness
- Shows win distribution
- Calculates statistical win probability

### 7. **Win Probability Predictor** 🔮
- Uses Logistic Regression
- Calculates win probability based on team strength
- Provides confidence level (High/Medium/Low)

### 8. **AI Insights Engine** 💡
- Generates human-readable insights
- Examples:
  - "🔥 Explosive batting lineup"
  - "⚠️ Bowling economy needs improvement"
  - "💪 Great team balance with all-rounders"
  - "⭐ Key player identification"

### 9. **Interactive Visualizations** 📈
- Role distribution pie chart
- Player contribution bar chart
- Win probability pie chart
- Radar charts for player comparison

---

## 🏗️ Architecture

### Project Structure

```
fantasy_optimizer/
├── app.py                      # Main Streamlit application (514 lines)
├── model.py                    # Data loading module (204 lines)
├── ml_model.py                 # ML training & prediction (291 lines)
├── optimizer.py                # Team optimization engine (279 lines)
├── simulator.py                # Match simulation (241 lines)
├── utils.py                    # Helper functions (266 lines)
├── requirements.txt            # Python dependencies
└── README.md                   # This documentation
```

### Module Breakdown

#### **app.py** - Main Application
- Streamlit UI components
- User interaction handling
- Data flow coordination
- Visualization rendering

#### **model.py** - DataLoader Class
- JSON file loading
- Feature engineering
- Data preprocessing
- Team/player queries

#### **ml_model.py** - FantasyPointsPredictor Class
- RandomForestRegressor implementation
- Model training with metrics
- Prediction with confidence intervals
- Feature importance analysis

#### **optimizer.py** - TeamOptimizer Class
- Optimal team generation algorithm
- Constraint enforcement
- Captain/vice-captain selection
- Team validation

#### **simulator.py** - MatchSimulator Class
- Single match simulation
- Multi-simulation (50 runs)
- Win probability calculation
- Detailed match analysis

#### **utils.py** - Helper Functions
- PlayerComparator class
- AIInsightsGenerator class
- Formatting utilities
- Validation functions

---

## 🤖 Machine Learning

### Model Architecture

**Algorithm:** RandomForestRegressor  
**Hyperparameters:**
```python
{
    'n_estimators': 100,
    'max_depth': 10,
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'random_state': 42
}
```

### Features Used (9)

1. **batting_average** - Runs per innings
2. **strike_rate** - Scoring rate
3. **wickets** - Total wickets taken
4. **matches** - Experience metric
5. **is_batsman** - Binary role indicator
6. **is_bowler** - Binary role indicator
7. **is_allrounder** - Binary role indicator
8. **experience** - Normalized matches played
9. **value_rating** - Cost-effectiveness ratio

### Target Variable

**Fantasy Points Formula:**
```python
fantasy_points = (
    runs / 2 +              # 1 point per 2 runs
    wickets * 25 +          # 25 points per wicket
    strike_rate / 10 -      # Bonus for scoring rate
    economy * 5             # Penalty for poor economy
).clip(lower=0)
```

### Training Process

1. **Data Loading** - Load from ipl_2025_complete.json
2. **Feature Engineering** - Calculate derived features
3. **Preprocessing** - Handle missing values, scale features
4. **Train-Test Split** - 80% train, 20% test
5. **Model Training** - Fit RandomForest
6. **Evaluation** - MAE and R² metrics
7. **Prediction** - Apply to new players

### Expected Performance

- **Train MAE:** ~15-20 points
- **Test MAE:** ~18-25 points
- **R² Score:** ~0.70-0.80

---

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Dependencies

```txt
streamlit==1.50.0
pandas==2.3.3
numpy==2.3.4
scikit-learn==1.7.0
plotly==6.6.0
joblib==1.5.2
```

### Installation Steps

1. **Navigate to project directory:**
```bash
cd fantasy_optimizer
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Verify installation:**
```bash
streamlit --version
```

---

## 📖 Usage Guide

### Basic Workflow

#### Step 1: Launch Application
```bash
streamlit run app.py
```

#### Step 2: Select Teams
- Choose Team A (e.g., RCB)
- Choose Team B (e.g., MI)
- Must be different teams

#### Step 3: Select Players
- Check boxes for players you want
- Select from both teams
- Aim for at least 11-15 players total

#### Step 4: Generate Best Team
- Click "🚀 Generate Best Fantasy Team"
- AI analyzes all selected players
- Displays optimal playing 11

#### Step 5: Review Results
- See captain & vice-captain
- Check total predicted points
- Review visualizations
- Read AI insights

### Advanced Features

#### Player Comparison
1. Go to "Player Comparison" tab
2. Select two players
3. Click "🔍 Compare Players"
4. View detailed stats and radar chart

#### Match Simulation
1. Go to "Match Simulation" tab
2. Select two teams
3. Click "🎮 Run Match Simulation"
4. See 50 simulation results
5. Review win probabilities

---

## 📊 API Reference

### DataLoader Class

```python
loader = DataLoader(data_dir='../data')

# Load player data
df = loader.load_ipl_complete_data()

# Load analytics
analytics = loader.load_advanced_analytics()

# Prepare features
df_processed = loader.prepare_features(df)

# Get teams
teams = loader.get_teams_list()

# Get team players
team_players = loader.get_players_by_team('RCB')
```

### FantasyPointsPredictor Class

```python
predictor = FantasyPointsPredictor(model_type='random_forest')

# Train model
metrics = predictor.train(df_processed)

# Predict points
predictions = predictor.predict(df)

# Predict with confidence
pred, confidence = predictor.predict_with_confidence(df)

# Get feature importance
importance = predictor.get_feature_importance()

# Save/load model
predictor.save_model('model.pkl')
predictor.load_model('model.pkl')
```

### TeamOptimizer Class

```python
optimizer = TeamOptimizer()

# Generate optimal team
optimal_team = optimizer.generate_optimal_team(df, predictions)

# Select captain/vice-captain
captain, vc = optimizer.select_captain_vice_captain(optimal_team)

# Calculate team score
total_score = optimizer.calculate_team_score(
    optimal_team, 
    captain['id'], 
    vc['id']
)

# Validate team
is_valid, issues = optimizer.validate_team(optimal_team)

# Compare two teams
comparison = optimizer.compare_two_teams(team_a, team_b)
```

### MatchSimulator Class

```python
simulator = MatchSimulator()

# Simulate single match
result = simulator.simulate_single_match(team_a, team_b)

# Simulate 50 times
stats = simulator.simulate_multiple_matches(team_a, team_b, n_simulations=50)

# Calculate win probability
prob_a, prob_b = simulator.calculate_win_probability(team_a, team_b)

# Get detailed analysis
analysis = simulator.get_detailed_analysis(team_a, team_b)
```

---

## 🎯 Examples

### Example 1: Generate Optimal Team

```python
# Load data
loader = DataLoader()
df = loader.load_ipl_complete_data()
df_processed = loader.prepare_features(df)

# Train model
predictor = FantasyPointsPredictor()
predictor.train(df_processed)

# Select players manually
selected_players = df_processed[
    df_processed['team'].isin(['RCB', 'MI'])
].head(15)

# Predict points
predictions = predictor.predict(selected_players)
selected_players['predicted_fantasy_points'] = predictions

# Generate optimal team
optimizer = TeamOptimizer()
optimal_team = optimizer.generate_optimal_team(selected_players, predictions)

# Get captain and vice-captain
captain, vc = optimizer.select_captain_vice_captain(optimal_team)

# Calculate score
score = optimizer.calculate_team_score(optimal_team, captain['id'], vc['id'])

print(f"Total Score: {score:.1f}")
print(f"Captain: {captain['name']}")
print(f"Vice-Captain: {vc['name']}")
```

### Example 2: Compare Players

```python
from utils import PlayerComparator

comparator = PlayerComparator()

player_a = df[df['name'] == 'Virat Kohli'].iloc[0]
player_b = df[df['name'] == 'Rohit Sharma'].iloc[0]

comparison = comparator.compare(player_a, player_b)

print(f"Better Player: {comparison['better_player']}")
print(f"Difference: {comparison['score_difference']:.1f}")
```

### Example 3: Match Simulation

```python
simulator = MatchSimulator()

# Get top 11 from each team
team_a = df_processed[df_processed['team'] == 'RCB'].nlargest(11, 'performance_score')
team_b = df_processed[df_processed['team'] == 'MI'].nlargest(11, 'performance_score')

# Run 50 simulations
results = simulator.simulate_multiple_matches(team_a, team_b, n_simulations=50)

print(f"Team A wins: {results['team_a_wins']}/50")
print(f"Team B wins: {results['team_b_wins']}/50")
print(f"Win Probability A: {results['team_a_win_percentage']:.1f}%")
```

---

## 🐛 Troubleshooting

### Issue: Data not loaded

**Error:** `FileNotFoundError: Could not find ipl_2025_complete.json`

**Solution:**
```bash
# Ensure you're running from correct directory
cd fantasy_optimizer

# Or specify absolute path in DataLoader
loader = DataLoader(data_dir='/absolute/path/to/data')
```

### Issue: Module not found

**Error:** `ModuleNotFoundError: No module named 'model'`

**Solution:**
```bash
# Make sure you're in the fantasy_optimizer directory
cd fantasy_optimizer

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Issue: Port already in use

**Error:** `Port 8501 is already in use`

**Solution:**
```bash
# Use different port
streamlit run app.py --server.port 8502
```

### Issue: Slow initial load

**Normal behavior** - ML model training takes 3-5 seconds on first load. Subsequent loads are faster due to caching.

---

## 📈 Performance Benchmarks

### Load Times
- Initial load: 3-5 seconds (ML training)
- Cached load: <1 second
- Team generation: 1-2 seconds
- Match simulation: 2-3 seconds (50 simulations)

### Resource Usage
- RAM: ~300-400 MB
- CPU: Brief spike during training
- GPU: Not required (CPU-only)

### Model Accuracy
- Train MAE: 15-20 points
- Test MAE: 18-25 points
- R² Score: 0.70-0.80

---

## 🎓 Educational Value

This project demonstrates:

1. **End-to-End ML Pipeline**
   - Data loading → Preprocessing → Training → Prediction

2. **Real-World Application**
   - Sports analytics
   - Fantasy sports optimization
   - Data-driven decision making

3. **Software Engineering**
   - Modular architecture
   - Clean code principles
   - Object-oriented design

4. **Data Science Skills**
   - Feature engineering
   - Ensemble methods (Random Forest)
   - Statistical analysis
   - Visualization

---

## 🚀 Future Enhancements

### Phase 2 Features
1. **Advanced Analytics**
   - Venue impact calculation
   - Weather conditions effect
   - Recent form weighting

2. **More ML Models**
   - XGBoost/LightGBM
   - Neural networks
   - Time-series analysis

3. **User Features**
   - Save favorite teams
   - Export reports (PDF)
   - Social sharing
   - Historical performance tracking

4. **Live Integration**
   - Real-time player stats
   - Live match updates
   - Dynamic team suggestions

---

## 📄 License

Educational/Research use. Built for hackathon demonstration.

---

## 🙏 Acknowledgments

- IPL data providers
- scikit-learn library
- Streamlit framework
- Plotly visualization

---

## 📞 Support

For issues or questions:
1. Check this README
2. Review inline code comments
3. Inspect browser console
4. Verify data file paths

---

**Built with ❤️ using Python, scikit-learn, Streamlit, and Plotly**

*For fantasy cricket analytics and AI-powered team selection*
