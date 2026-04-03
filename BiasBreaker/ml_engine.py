"""
ml_engine.py
XGBoost model + SHAP explainability for BiasBreaker.
Produces the "AI Whisper" that powers the AI Mentor panel.
"""

import streamlit as st
import numpy as np
import pandas as pd
import shap
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from data_engine import generate_resumes, POSITIVE_GAPS

FEATURE_COLS = ["experience", "skills_count", "education", "gap_years"]

FEATURE_LABELS = {
    "experience":   "Years of Experience",
    "skills_count": "Skill Breadth",
    "education":    "Education Level",
    "gap_years":    "Career Gap Length",
}


@st.cache_resource
def train_model():
    df = generate_resumes(400, seed=42)
    X, y = df[FEATURE_COLS], df["outcome"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    model = xgb.XGBClassifier(
        n_estimators=200, max_depth=4, learning_rate=0.08,
        subsample=0.85, colsample_bytree=0.85,
        eval_metric="logloss", random_state=42,
    )
    model.fit(Xtr, ytr)
    acc = accuracy_score(yte, model.predict(Xte))
    explainer = shap.TreeExplainer(model)
    return model, explainer, round(acc, 3)


def predict(model, explainer, row: dict) -> tuple[float, int, list]:
    X = pd.DataFrame([{c: row[c] for c in FEATURE_COLS}])
    prob = float(model.predict_proba(X)[0][1])
    pred = int(model.predict(X)[0])
    shap_vals = explainer.shap_values(X)[0]
    return prob, pred, shap_vals


def build_whisper(prob: float, pred: int, shap_vals, row: dict) -> dict:
    """
    Returns a structured whisper dict:
      recommendation, confidence, lines (list of text), prob, pred
    """
    pairs = sorted(zip(FEATURE_COLS, shap_vals), key=lambda x: abs(x[1]), reverse=True)
    lines = []

    for feat, sv in pairs[:3]:
        if abs(sv) < 0.04:
            continue
        label = FEATURE_LABELS[feat]
        if sv > 0:
            lines.append(f"✅ Strong {label} boosts hire probability")
        else:
            lines.append(f"⚠️ Weak {label} lowers hire probability")

    # Gap context
    gap_reason = row.get("gap_reason", "")
    gap_years  = row.get("gap_years", 0)
    if gap_years > 0.5:
        if gap_reason in POSITIVE_GAPS:
            lines.append(f"💡 Gap reason '{gap_reason}' is low-risk — avoid bias!")
        else:
            lines.append(f"🔴 Gap '{gap_reason}' may indicate risk — weigh carefully")

    confidence = "High confidence" if abs(prob - 0.5) > 0.25 else "Borderline — trust your gut"
    rec = "✅ HIRE" if pred == 1 else "⛔ REJECT"

    return {
        "recommendation": rec,
        "confidence":     confidence,
        "lines":          lines,
        "prob":           prob,
        "pred":           pred,
    }


# ── Active Learning ───────────────────────────────────────────────────────────
def retrain_with_decisions(player_decisions: list, base_df=None):
    """
    Active Learning: merge player decisions with base training data,
    retrain a lightweight XGBoost on the last 200 rows.

    player_decisions: list of dicts with FEATURE_COLS + 'outcome'
    Returns (model, explainer) or None on failure.
    """
    if len(player_decisions) < 3:
        return None  # not enough data yet

    player_df = pd.DataFrame(player_decisions)[FEATURE_COLS + ["outcome"]]

    if base_df is not None:
        combined = pd.concat(
            [base_df[FEATURE_COLS + ["outcome"]], player_df],
            ignore_index=True,
        )
    else:
        combined = player_df

    # Performance guardrail: keep last 200 rows only
    combined = combined.tail(200).reset_index(drop=True)

    if combined["outcome"].nunique() < 2:
        return None  # can't train on single-class data

    X, y = combined[FEATURE_COLS], combined["outcome"]

    # Lightweight 50-tree model for fast retrain
    model = xgb.XGBClassifier(
        n_estimators=50, max_depth=3, learning_rate=0.1,
        subsample=0.8, eval_metric="logloss", random_state=0,
    )
    model.fit(X, y)
    explainer = shap.TreeExplainer(model)
    return model, explainer
