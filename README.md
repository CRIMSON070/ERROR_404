# ⚔️ BiasBreaker: The Hiring Arena

**BiasBreaker** is an AI-powered, gamified hiring simulator designed to challenge your decision-making and expose hidden biases. Step into the arena, review candidate "Monster Cards," and use Explainable AI (SHAP) to navigate the complexities of modern recruitment.

![BiasBreaker Splash](https://img.shields.io/badge/Tech-FastAPI%20%7C%20Tailwind%20%7C%20XGBoost%20%7C%20SHAP-blueviolet)

---

## 🚀 Features

### 🎮 Gamified Hiring Experience
- **Monster Cards**: Candidates are presented as RPG-style cards with stats like Experience (HP), Skills (Attack), and Education (Armor).
- **HUD System**: Track your Score, Lives (❤️), and Round progress in real-time.
- **Boss Battles**: The final round features a "Boss Candidate" with ambiguous stats—double points if you make the right call!

### 🤖 Explainable AI (XAI)
- **AI Whisper**: A limited resource powered by **XGBoost** and **SHAP** that reveals why the AI recommends a "Hire" or "Reject."
- **Bias Radar**: Real-time detection of potential hiring biases (e.g., career gap penalties).

### 🧠 Modern Tech Stack
- **Backend**: FastAPI for high-performance API routing.
- **Frontend**: Responsive Tailwind CSS with a cyberpunk-fantasy aesthetic.
- **Machine Learning**: XGBoost for candidate outcome prediction and SHAP for model interpretability.
- **AI Coaching**: Integration with **Ollama** for personalized career coaching and post-game feedback.

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+
- [Ollama](https://ollama.com/) (Optional, for AI Career Coach features)

### 1. Clone the Repository
```bash
git clone https://github.com/CRIMSON070/ERROR_404.git
cd ERROR_404
```

### 2. Install Dependencies
```bash
pip install -r BiasBreaker/requirements.txt
# Additional dependencies for FastAPI
pip install fastapi uvicorn
```

---

## 🚦 How to Run

### Option 1: FastAPI Web App (Recommended)
This runs the full interactive web experience with the modern UI.
```bash
cd BiasBreaker
python server.py
```
Then open your browser to **http://localhost:8000**.

### Option 2: Streamlit Version
A standalone version for rapid prototyping and data exploration.
```bash
cd BiasBreaker
streamlit run app.py
```

---

## 🎯 How to Play

1.  **Review**: Examine the candidate's Experience, Skills, Education, and Career Gaps.
2.  **AI Whisper**: If you're unsure, use an **AI Hint**. These are limited (3 per game) and cost -3 points, but provide crucial SHAP-based insights.
3.  **Decide**: Click **Hire** or **Reject**.
    - **Correct Decision**: +500 points (Standard) or +1000 (Boss).
    - **Wrong Decision**: Lose a life (❤️) and significant points.
4.  **Bias Shield**: Be careful! Penalizing a candidate for a justified career gap can trigger a **Bias Penalty**.
5.  **Victory**: Reach the final round and defeat the Boss to claim your place in the Hall of Fame!

---

## 📂 Project Structure

```text
BiasBreaker/
├── app.py              # Streamlit entry point
├── server.py           # FastAPI entry point
├── ml_engine.py        # XGBoost & SHAP logic
├── data_engine.py      # Synthetic data generation
├── game_state.py       # Game logic & scoring
├── ollama_client.py    # LLM integration
└── templates/          # Frontend HTML/JS
```

---

## 🤝 Contributing
Contributions are welcome! If you have ideas for new monster types, power-ups, or ML models, feel free to open a Pull Request.

---

## 📜 License
MIT License - See the project for details.
