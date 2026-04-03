"""
ollama_client.py
Connects to local Ollama (llama3) for natural-language AI Whisper
and post-decision narrative feedback.
Falls back to SHAP-only whisper if Ollama is unavailable.
"""

import requests
import streamlit as st

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"


def _call_ollama(prompt: str, timeout: int = 8) -> str | None:
    """Returns generated text or None if Ollama is unreachable."""
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=timeout,
        )
        if resp.status_code == 200:
            return resp.json().get("response", "").strip()
    except Exception:
        pass
    return None


def get_ai_whisper_llm(row: dict, shap_lines: list[str]) -> str | None:
    """
    Ask Ollama to rephrase the SHAP analysis into an engaging,
    character-style 'AI Mentor' speech.
    """
    shap_summary = "\n".join(shap_lines) if shap_lines else "No strong SHAP signals."
    prompt = (
        "You are the AI Mentor in a gamified hiring simulator. "
        "A player is reviewing a job candidate. "
        "Speak directly to the player in 2-3 short, punchy sentences. "
        "Be wise but edgy — like a wizard giving tactical advice before battle. "
        "Do NOT use markdown. Do NOT start with 'I'. "
        "Here is the candidate profile summary:\n"
        f"- Experience: {row.get('experience', 0):.1f} years\n"
        f"- Skills: {int(row.get('skills_count', 0))}\n"
        f"- Education level: {row.get('education', 1)}/5\n"
        f"- Career gap: {row.get('gap_years', 0):.1f} years ({row.get('gap_reason', 'No gap')})\n"
        f"Key AI signals:\n{shap_summary}\n"
        "Give your verdict as the AI Mentor character."
    )
    return _call_ollama(prompt)


def get_post_decision_feedback(action: str, correct: bool, row: dict) -> str | None:
    """
    After the player decides, Ollama generates a short post-decision
    narrative comment — win or lose.
    Kept short (4s timeout) so it never blocks the UI rerun.
    """
    result = "correct" if correct else "incorrect"
    prompt = (
        "You are the AI Mentor in a hiring strategy game. "
        f"The player just made a '{action}' decision on this candidate, and it was {result}. "
        f"Candidate had {row.get('experience', 0):.1f} yrs exp, "
        f"{int(row.get('skills_count', 0))} skills, "
        f"{row.get('gap_years', 0):.1f} yr gap ({row.get('gap_reason', 'No gap')}). "
        "Give ONE punchy sentence of feedback (max 25 words). No markdown, no quotes."
    )
    return _call_ollama(prompt, timeout=4)


def ollama_feedback(row: dict, decision: str) -> str | None:
    """
    Specifically analyzes the decision for potential bias using Ollama.
    """
    gap_years = row.get("gap_years", 0)
    gap_reason = row.get("gap_reason", "No gap")
    
    prompt = (
        "You are the AI Mentor in a hiring strategy game. "
        f"The player decided to {decision.upper()} a candidate who has a {gap_years:.1f}-year career gap "
        f"(Reason: {gap_reason}). "
        "Provide a short, 1-2 sentence feedback focusing on potential bias. "
        "If they rejected a candidate with a reasonable gap (like parental leave), mention it. "
        "Make it sound like a mentor guiding the player. Do NOT use markdown."
    )
    return _call_ollama(prompt, timeout=5)


@st.cache_data(ttl=60)
def ollama_available() -> bool:
    """Cached for 60s — avoids pinging Ollama on every Streamlit rerun."""
    try:
        r = requests.get("http://localhost:11434/", timeout=2)
        return r.status_code == 200
    except Exception:
        return False

def ollama_career_coach(strengths: str, weaknesses: str, bias_status: str, score: int) -> str | None:
    """
    Called at game over. Acts as an AI Career Coach analyzing the player's performance.
    """
    prompt = (
        "You are an AI Career Coach analyzing an HR manager's performance in a hiring simulation game. "
        "Speak directly to the player in 3-4 short, punchy sentences. Be encouraging but direct about areas to improve. "
        f"Their final score was {score}. "
        f"Their strengths: {strengths}. "
        f"Their weaknesses: {weaknesses}. "
        f"Bias radar: {bias_status}. "
        "Give them a personalized piece of advice to improve their evaluation skills or overcome their bias for the next rounds. "
        "Do not use markdown. Do not start with 'I'. "
    )
    return _call_ollama(prompt, timeout=10)
