from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
import os

from data_engine import generate_resumes, make_boss_resume, pick_name, pick_skills
from ml_engine import train_model, predict, build_whisper, retrain_with_decisions
from ollama_client import get_ai_whisper_llm, ollama_available, ollama_feedback, ollama_career_coach
from game_state import compute_score, save_leaderboard, load_leaderboard, analyze_bias, evaluate_skill_gaps

app = FastAPI()

os.makedirs("templates", exist_ok=True)
templates = Jinja2Templates(directory="templates")

# Globals for server state
GAME_STATE = {
    "game_started": False,
    "game_over": False,
    "resumes": [],
    "round_idx": 0,
    "score": 0,
    "lives": 3,
    "skips_used": 0,
    "ai_uses": 3,
    "history": [],
    "decision_log": [],
    "player_name": "Challenger",
    "difficulty": "normal",
    "model": None,
    "explainer": None,
    "acc": 0,
    "current_whisper": None,
    "current_ai_pred": None,
    "current_prob": None,
    "hint_shown": False,
    "last_result": None
}

@app.on_event("startup")
def startup_event():
    model, explainer, acc = train_model()
    GAME_STATE["model"] = model
    GAME_STATE["explainer"] = explainer
    GAME_STATE["acc"] = acc

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

class StartReq(BaseModel):
    difficulty: str = "normal"

@app.post("/api/start")
def start_game_api(data: StartReq):
    GAME_STATE["game_started"] = True
    GAME_STATE["game_over"] = False
    GAME_STATE["round_idx"] = 0
    GAME_STATE["score"] = 0
    GAME_STATE["lives"] = 3
    GAME_STATE["ai_uses"] = 3
    GAME_STATE["history"] = []
    GAME_STATE["decision_log"] = []
    GAME_STATE["last_result"] = None
    GAME_STATE["hint_shown"] = False
    
    diff = data.difficulty
    cnt = 10
    resumes_df = generate_resumes(n=cnt, difficulty=diff)
    resumes = resumes_df.to_dict(orient="records")
    
    # We need to compute name and skills here so the frontend can display them easily
    for i, r in enumerate(resumes):
        r["name"] = pick_name(i)
        r["skills_list"] = pick_skills(int(r["skills_count"]), i)
        
    boss = make_boss_resume()
    if not isinstance(boss, dict):
        boss = boss.to_dict()
    boss["name"] = "Eldrin the Architect"
    boss["skills_list"] = pick_skills(int(boss.get("skills_count", 95)), 9)
    resumes[-1] = boss
    
    GAME_STATE["resumes"] = resumes
    
    return {"status": "ok"}

@app.get("/api/state")
def get_state():
    if not GAME_STATE["game_started"]:
        return {"state": "start", "acc": GAME_STATE["acc"]}
        
    if GAME_STATE["game_over"]:
        gaps = evaluate_skill_gaps(GAME_STATE["history"], GAME_STATE["resumes"])
        bias_res = analyze_bias(GAME_STATE["history"], GAME_STATE["resumes"])
        return {
            "state": "game_over", 
            "score": GAME_STATE["score"],
            "strengths": gaps["strengths"],
            "weaknesses": gaps["weaknesses"],
            "missions": gaps["missions"],
            "bias": bias_res["status"]
        }

    idx = GAME_STATE["round_idx"]
    row = GAME_STATE["resumes"][idx]
    
    prob, ai_pred, shap_vals = predict(GAME_STATE["model"], GAME_STATE["explainer"], row)
    whisper = build_whisper(prob, ai_pred, shap_vals, row)
    
    GAME_STATE["current_prob"] = prob
    GAME_STATE["current_ai_pred"] = ai_pred
    GAME_STATE["current_whisper"] = whisper
    
    return {
        "state": "playing",
        "round": idx + 1,
        "score": GAME_STATE["score"],
        "lives": GAME_STATE["lives"],
        "ai_uses": GAME_STATE["ai_uses"],
        "candidate": row,
        "hint_shown": GAME_STATE["hint_shown"],
        "whisper": whisper if GAME_STATE["hint_shown"] else None,
        "last_result": GAME_STATE["last_result"]
    }

class ActionReq(BaseModel):
    action: str

def api_compute_score(action: str, outcome: int, ai_pred: int, row, is_boss=False):
    delta = 0
    msgs = []
    correct = False

    hired = (action == "hire")
    if action == "skip":
        delta = -50
        msgs.append("⏭️ Skipped (-50)")
        return delta, "".join(msgs), False

    if hired and outcome == 1:
        correct = True
        delta = 500
        msgs.append("🎉 Good Hire!")
    elif hired and outcome == 0:
        correct = False
        delta = -200
        msgs.append("❌ Bad Hire!")
    elif not hired and outcome == 0:
        correct = True
        delta = 300
        msgs.append("🛑 Dodged bullet!")
    else:
        correct = False
        delta = -300
        msgs.append("📉 Missed Talent!")

    if not hired and row.get("gap_years", 0) < 1.0 and outcome == 1:
        delta -= 150
        msgs.append("⚠️ Bias Penalty -150")

    if is_boss and correct:
        delta *= 2
        msgs.append("👹 BOSS x2!")

    return delta, " | ".join(msgs), correct

@app.post("/api/action")
def take_action(req: ActionReq):
    action = req.action
    idx = GAME_STATE["round_idx"]
    row = GAME_STATE["resumes"][idx]
    outcome = int(row["outcome"])
    ai_pred = GAME_STATE["current_ai_pred"]
    is_boss = row.get("is_boss", False)
    
    delta, msg, correct = api_compute_score(action, outcome, ai_pred, row, is_boss=is_boss)
    
    if is_boss and correct:
        msg = "👹 BOSS DEFEATED — Double Points! 🏆\n" + msg
        
    GAME_STATE["score"] += delta
    if action != "skip" and not correct:
        GAME_STATE["lives"] -= 1
        
    followed_ai = (action == "hire") == (ai_pred == 1) if action != "skip" else False
    
    GAME_STATE["history"].append({
        "round": idx, "action": action, "outcome": outcome, "correct": correct, "followed_ai": followed_ai, "delta": delta
    })
    
    GAME_STATE["last_result"] = {
        "action": action, "delta": delta, "msg": msg, "correct": correct, "outcome": outcome
    }
    
    GAME_STATE["round_idx"] += 1
    GAME_STATE["hint_shown"] = False
    
    if GAME_STATE["lives"] <= 0 or GAME_STATE["round_idx"] >= len(GAME_STATE["resumes"]):
        GAME_STATE["game_over"] = True
        
    return {"status": "ok", "result": GAME_STATE["last_result"]}

@app.post("/api/hint")
def use_hint():
    if GAME_STATE["ai_uses"] > 0 and not GAME_STATE["hint_shown"]:
        GAME_STATE["ai_uses"] -= 1
        GAME_STATE["score"] -= 3
        GAME_STATE["hint_shown"] = True
        return {"status": "ok"}
    return {"status": "error"}

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
