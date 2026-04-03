# 🏏 AI-Powered IPL Match Simulator and Player Analysis System

A hackathon-quality AI/ML-based web application for simulating IPL matches and analyzing player performance using machine learning.

---

## 🚀 Features

### 1. **Team Selection** 🔵🔴
- Select any two IPL teams (RCB, MI, CSK, etc.)
- Load all players from the dataset
- Interactive playing XI selection interface
- Real-time player statistics display

### 2. **Player Performance Prediction (AI/ML Core)** 🤖
- **Machine Learning Models:**
  - Random Forest Regressor for batting performance
  - Random Forest Regressor for bowling performance
- **Input Features:**
  - Batting average
  - Strike rate
  - Total runs
  - Wickets taken
  - Economy rate
  - Historical performance
- **Outputs:**
  - Expected runs for batsmen
  - Expected wickets for bowlers
  - Overall player performance score

### 3. **Team Strength Calculation** 💪
- Aggregate predicted player scores
- Calculate composite team strength
- Role-based weighting
- Experience factor consideration

### 4. **Match Simulation** 🎮
- Simulate match outcomes using ML-predicted team strengths
- Add realistic randomness (±15% variance)
- **Win Probability Calculation:**
  - Logistic Regression model
  - Sigmoid function for probability estimation
- **Outputs:**
  - Team A score
  - Team B score
  - Winner prediction
  - Win probability percentage
  - Victory margin

### 5. **Player Comparison Feature** ⚔️
- Head-to-head player comparison
- Compare across multiple metrics:
  - Batting score
  - Bowling score
  - Composite rating
- Visual radar charts
- Clear "better player" determination

### 6. **AI Insights Engine** 💡
- Automatic insight generation
- Examples:
  - "🔥 Explosive batting lineup with high strike rate"
  - "⚠️ Bowling economy needs improvement"
  - "💎 Excellent value for money pick"
  - "🎯 Economical bowler"
- Team composition analysis
- Strength/weakness identification

---

## 🛠️ Tech Stack

### Frontend
- **Streamlit** - Fast, interactive web UI
- **Plotly** - Beautiful, interactive charts
  - Bar charts for team comparison
  - Pie charts for win probability
  - Radar charts for player comparison
  - Histograms for distribution analysis

### Backend & ML
- **Python 3.8+**
- **scikit-learn**
  - RandomForestRegressor (player performance)
  - LogisticRegression (win probability)
- **NumPy** - Numerical computations
- **Pandas** - Data manipulation

### Data
- **ipl_2025_complete.json** - Primary player dataset (623 players)
- **advanced_ipl_analytics.json** - Advanced statistics

---

## 📁 Project Structure

```
match_simulator/
├── app.py                  # Main Streamlit application
├── utils.py                # Utility functions (optional)
├── models/                 # Trained ML models (saved)
│   ├── batting_model.pkl
│   └── bowling_model.pkl
├── data/
│   ├── processed/
│   │   └── ipl_2025_complete.json
│   └── analytics/
│       └── advanced_ipl_analytics.json
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Navigate to project directory:**
```bash
cd IPL-AUCTION-STARTEGIC-SYSTEM-main/IPL-AUCTION-STARTEGIC-SYSTEM-main/match_simulator
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
streamlit run app.py
```

4. **Open your browser:**
```
http://localhost:8501
```

---

## 🎮 How to Use

### Match Simulation Flow

#### Step 1: Select Teams
- Choose Team A (e.g., Royal Challengers Bangalore)
- Choose Team B (e.g., Chennai Super Kings)

#### Step 2: Select Playing XI
- Select 11 players for each team
- View player stats while selecting
- Ensure balanced team composition

#### Step 3: Simulate Match
- Click "🎮 Simulate Match" button
- Watch AI calculate predictions
- View results with visualizations

#### Step 4: Analyze Results
- See predicted scores
- Check win probabilities
- Read AI insights for both teams
- Review team strength comparison

### Player Comparison Flow

1. Navigate to "Player Comparison" tab
2. Select Player A
3. Select Player B
4. Click "🔍 Compare Players"
5. View detailed comparison with radar chart

---

## 🤖 Machine Learning Details

### Player Performance Prediction

**Model Architecture:**
```python
RandomForestRegressor(
    n_estimators=100,
    random_state=42
)
```

**Features Used:**
- Matches played
- Total runs
- Total wickets
- Strike rate
- Economy rate
- Historical performance score
- Value score

**Target Variables:**
- Batting: `(runs × strike_rate) / 100`
- Bowling: `wickets × (10 - economy)`

### Win Probability Model

**Logistic Regression:**
```python
P(Team A wins) = 1 / (1 + e^(-(strength_A - strength_B) / 50))
```

**Factors Considered:**
- Team strength differential
- Player form (via performance scores)
- Historical data patterns

---

## 📊 UI Components

### Navigation Sidebar
- Match Simulator (default)
- Player Comparison
- Team Analysis

### Match Simulator Page
- Team selection dropdowns
- Playing XI checkboxes (3-column grid)
- Player stats captions
- Simulate Match button
- Results dashboard with:
  - Score metrics
  - Win probability bars
  - Winner announcement
  - Team strength bar chart
  - Win probability pie chart
  - AI insights panels

### Player Comparison Page
- Dual player selectors
- Comparison button
- Side-by-side metrics
- Better player highlight
- Radar chart visualization

### Team Analysis Page
- Team selector
- Squad statistics
- Role distribution pie chart
- Performance histogram
- Top performers table

---

## 🎨 Design Features

### Color Scheme
- Primary: Blue (#1f77b4) for Team A
- Secondary: Orange (#ff7f0e) for Team B
- Success: Green for positive insights
- Warning: Yellow/orange for cautions
- Danger: Red for negative insights

### Animations
- Smooth transitions on hover
- Loading spinners during ML training
- Progress bar animations
- Chart rendering effects

### Responsive Layout
- Wide layout for desktop
- Column-based organization
- Mobile-friendly stacking

---

## 📈 Sample Outputs

### Match Simulation Result
```
🏆 Winner: Mumbai Indians by 23.5 runs

Team A (MI): 187.3
- Win Probability: 68.4%
- Team Strength: 195.2

Team B (CSK): 163.8
- Win Probability: 31.6%
- Team Strength: 171.7

AI Insights:
✅ MI: Explosive batting lineup with high strike rate
✅ MI: Quality bowling attack
⚠️ CSK: Bowling economy needs improvement
🌟 CSK: Young and energetic team
```

### Player Comparison Result
```
🏆 Virat Kohli is better by 45.2 points

Virat Kohli:
- Batting Score: 234.5
- Bowling Score: 0.0
- Total: 234.5

Rohit Sharma:
- Batting Score: 189.3
- Bowling Score: 0.0
- Total: 189.3
```

---

## 🔧 Customization

### Add New Teams
Simply add players with new team names to the JSON dataset.

### Adjust ML Models
Modify hyperparameters in `PlayerPerformancePredictor` class:
```python
RandomForestRegressor(n_estimators=200, max_depth=10)
```

### Change Randomness Factor
Edit simulation variance:
```python
team_a_score = team_a_strength * np.random.uniform(0.85, 1.15)
# Change 0.85-1.15 to adjust variance
```

---

## 🐛 Troubleshooting

### Issue: Data not loading
**Solution:** Ensure `data/processed/ipl_2025_complete.json` exists

### Issue: Module not found
**Solution:** Run `pip install -r requirements.txt`

### Issue: Port already in use
**Solution:** Run on different port:
```bash
streamlit run app.py --server.port 8502
```

---

## 📊 Dataset Format

Expected structure in `ipl_2025_complete.json`:
```json
{
  "players": [
    {
      "id": "player_1",
      "name": "Player Name",
      "team": "RCB",
      "role": "Batsman",
      "runs": 1500,
      "wickets": 0,
      "strike_rate": 135.5,
      "economy": 0,
      "matches": 50,
      "performance_score": 45.2,
      "value_score": 3.8
    }
  ]
}
```

---

## 🎓 Educational Value

This project demonstrates:
- ✅ Real-world ML application
- ✅ Data preprocessing
- ✅ Feature engineering
- ✅ Model training and inference
- ✅ Interactive data visualization
- ✅ Full-stack development
- ✅ Sports analytics
- ✅ Predictive modeling

---

## 🚀 Future Enhancements

1. **Advanced ML Models:**
   - XGBoost/LightGBM
   - Neural networks
   - Time-series form analysis

2. **Additional Features:**
   - Venue impact calculation
   - Weather conditions
   - Head-to-head records
   - Recent form tracking

3. **Enhanced UI:**
   - Live match tracking
   - Commentary generation
   - Social sharing
   - Export reports

4. **Data Integration:**
   - Real-time API feeds
   - Historical database
   - Player images
   - Video highlights

---

## 👨‍💻 Development

### Running in Development Mode
```bash
streamlit run app.py --server.headless true
```

### Code Quality
- Type hints throughout
- Comprehensive docstrings
- Modular architecture
- Clean separation of concerns

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
4. Verify data format

---

**Built with ❤️ using Python, scikit-learn, and Streamlit**

*For IPL cricket analytics and match prediction*
