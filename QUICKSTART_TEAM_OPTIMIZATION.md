# 🚀 Quick Start Guide - Team Optimization AI

## Step-by-Step Setup (5 minutes)

### Prerequisites
- Python 3.8+
- pip packages from `requirements.txt`
- IPL player data CSV file

---

## 🔧 Installation

### 1. Install Dependencies

```bash
cd IPL-AUCTION-STARTEGIC-SYSTEM-main
pip install -r requirements.txt
```

**Required packages:**
- torch
- pandas
- numpy
- scikit-learn
- fastapi
- uvicorn
- streamlit
- plotly
- requests

---

## 📊 Step 1: Train the Deep Learning Model

```bash
python models/training_pipeline.py
```

**What this does:**
1. Loads player data from `data/raw/2024_players_details.csv`
2. Engineers 50 features (stats, role, team, etc.)
3. Trains Multi-Task DNN for 100 epochs
4. Saves best model to `models/best_player_value_model.pth`

**Expected output:**
```
📂 Loading data from data/raw/2024_players_details.csv...
✅ Data loaded: 622 players, 50 features
🤖 Model initialized on cpu
   Input dim: 50
   Architecture: [128, 64, 32]

🚀 Starting training for 100 epochs...
Epoch   1: Train Loss=0.8234, Val Loss=0.7891
...
Epoch  42: Train Loss=0.3421, Val Loss=0.3156
⏹️ Early stopping at epoch 42
✅ Training completed! Best validation loss: 0.3156
✅ Model artifacts saved to models/best_player_value_model.pth
```

**Files created:**
- `models/best_player_value_model.pth` - Main model
- `models/best_player_value_model_scaler.pkl` - Feature scaler
- `models/best_player_value_model_encoders.json` - Label encoders

---

## 🖥️ Step 2: Start Backend Server

```bash
python run_backend.py
```

**What this does:**
1. Starts FastAPI server on `http://localhost:8000`
2. Loads trained DL models automatically
3. Exposes REST API endpoints

**Expected output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
Loading models...
Loading player data...
✅ Backend ready! Models loaded: {...}
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
```

**Test backend:**
Open browser → http://localhost:8000/health

Should show:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "models_loaded": true,
  "data_loaded": true
}
```

---

## 🎨 Step 3: Launch Frontend

**Open new terminal:**

```bash
streamlit run frontend/app.py
```

**What this does:**
1. Starts Streamlit app on `http://localhost:8501`
2. Loads dark-themed professional UI
3. Connects to backend API

**Expected output:**
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

**Browser will open automatically →** You'll see the IPL Auction Strategy Platform homepage.

---

## 🎯 Step 4: Use Team Optimization AI

### A. Build Your Team First

1. Click **"Players"** in sidebar
2. Add 11+ players to your squad (use filters/search)
3. Monitor budget in sidebar (max ₹120 Cr)

### B. Go to Team Optimization AI

1. Click **"Team Optimization AI"** in sidebar
2. You'll see:
   - Team size cards
   - Budget summary
   - "Run AI Optimization Analysis" button

### C. Run Analysis

1. Click **"🤖 Run AI Optimization Analysis"**
2. Wait 2-3 seconds for DL inference
3. View comprehensive report:

**Results include:**

📊 **Team Performance Metrics**
- Efficiency Score (target: >1.0)
- Predicted Team Value
- Average Performance (/100)

💰 **Value vs Cost Chart**
- Visual comparison of actual spend vs predicted value

🔴 **Overpriced Players**
- Red cards showing players you overpaid for
- Shows: actual price, predicted value, risk score

🟢 **Undervalued Players**
- Green cards showing bargain picks
- Shows: surplus value gained

🔁 **Replacement Suggestions**
- Better alternatives for overpriced players
- Similar role, lower price, better performance

💡 **AI Recommendations**
- Actionable insights
- Priority suggestions

---

## 📊 Analytics Page Enhancements

### Role Distribution Visualization

1. Go to **"Analytics"** page
2. See pie chart showing:
   - Batsmen % 
   - Bowlers %
   - All-rounders %
   - Wicket-keepers %
3. Exact percentages displayed below chart

**Example:**
```
Role Breakdown:
- Batsman: 6 players (40.0%)
- Bowler: 5 players (33.3%)
- All-rounder: 3 players (20.0%)
- Wicket-keeper: 1 players (6.7%)
```

---

## ⭐ Best XI Page Enhancements

### Current Squad + Best XI Comparison

1. Go to **"Best XI"** page
2. See your current squad table first
3. Click **"🎯 Generate Best XI"**
4. View optimal XI in two formats:
   - **Visual card layout** (11 columns)
   - **Detailed table** with positions

**DL Selection Logic:**
- Ensures balanced formation (1 WK, 4 BAT, 2 AR, 4 BOWL)
- Sorts by predicted performance
- Fills critical roles first

---

## 🐛 Troubleshooting

### Issue: "Model not found"

**Solution:**
```bash
python models/training_pipeline.py
```

Make sure `best_player_value_model.pth` exists in `models/` folder.

---

### Issue: "Backend not responding"

**Check:**
1. Backend is running: `http://localhost:8000/health`
2. No firewall blocking port 8000
3. Terminal shows "Uvicorn running on..."

**Restart backend:**
```bash
# Stop current process (Ctrl+C)
python run_backend.py
```

---

### Issue: "Need at least 11 players"

**Solution:**
1. Go to **"Players"** tab
2. Add minimum 11 players to your squad
3. Then access Team Optimization AI

---

### Issue: "Timeout error"

**Causes:**
- Backend busy with other requests
- Model loading takes time
- Network latency

**Solutions:**
1. Wait 10 seconds, try again
2. Check backend terminal for errors
3. Restart backend if needed

---

## ✅ Success Checklist

Before using Team Optimization AI:

- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Model trained (`python models/training_pipeline.py`)
- [ ] Backend running (`http://localhost:8000/health` shows healthy)
- [ ] Frontend running (`http://localhost:8501` accessible)
- [ ] 11+ players added to squad
- [ ] Budget under ₹120 Cr

---

## 🎓 Understanding the Output

### Efficiency Score

- **> 1.0**: Your team is undervalued (great job!)
- **= 1.0**: Fair market value
- **< 1.0**: You overpaid for some players

**Action:** Look for undervalued players to improve ratio.

### Predicted Value

- Based on historical performance, role, stats
- What the player should cost in fair market
- Used to detect overpricing

### Risk Score

- **0.0-0.3**: Low risk (consistent performer)
- **0.3-0.6**: Medium risk
- **0.6-1.0**: High risk (inconsistent/expensive)

### Replacement Algorithm

Uses **cosine similarity** on 32-dim embeddings to find:
- Similar playing style
- Lower price point
- Equal/better performance

---

## 💡 Pro Tips

1. **Build balanced squad first**
   - Minimum 1 WK, 4 BAT, 3 AR, 4 BOWL
   - Stay under budget (₹120 Cr)

2. **Use filters in Players tab**
   - Filter by role, team, max price
   - Search specific players

3. **Check Analytics before optimization**
   - See role distribution
   - Identify gaps in squad

4. **Review all recommendations**
   - Don't just look at top suggestion
   - Consider risk scores

5. **Re-run after each change**
   - Efficiency score updates dynamically
   - New opportunities may appear

---

## 📞 Support

If you encounter issues:

1. Check this README's troubleshooting section
2. Review backend terminal logs
3. Check frontend console (F12)
4. Verify all prerequisites met

---

## 🎉 You're Ready!

Enjoy AI-powered team optimization! 🏏🤖

Start building your dream IPL squad now!
