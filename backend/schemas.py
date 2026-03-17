"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


# ==================== Player Schemas ====================

class PlayerBase(BaseModel):
    """Base player schema"""
    player_name: str
    role: str
    team: Optional[str] = None
    sold_price: float
    base_price: Optional[float] = None
    country: Optional[str] = "India"


class Player(PlayerBase):
    """Complete player schema"""
    id: Optional[str] = None
    matches_played: Optional[int] = 0
    runs_scored: Optional[float] = 0
    strike_rate: Optional[float] = 0
    wickets_taken: Optional[float] = 0
    economy_rate: Optional[float] = 0
    batting_average: Optional[float] = 0
    consistency_rating: Optional[float] = 0
    overall_impact: Optional[float] = 0
    value_score: Optional[float] = 0
    is_selected: bool = False
    isOverseas: bool = False


class PlayerResponse(BaseModel):
    """Player response schema"""
    success: bool
    data: Optional[Player] = None
    message: Optional[str] = None


class PlayersResponse(BaseModel):
    """Multiple players response"""
    success: bool
    data: List[Player]
    total: int
    filters_applied: Optional[Dict] = None


# ==================== Team Schemas ====================

class TeamComposition(BaseModel):
    """Team composition analysis"""
    batsmen: int
    bowlers: int
    allrounders: int
    wicketkeepers: int
    overseas_players: int
    total_players: int
    budget_spent: float
    remaining_budget: float
    balance_score: float


class TeamAnalysisRequest(BaseModel):
    """Request for team analysis"""
    selected_players: List[str]  # List of player IDs


class TeamAnalysisResponse(BaseModel):
    """Team analysis response"""
    success: bool
    composition: TeamComposition
    strengths: List[str]
    weaknesses: List[Dict]
    recommendations: List[Dict]
    overall_score: float


# ==================== Suggestion Schemas ====================

class SuggestionRequest(BaseModel):
    """Request for AI suggestions"""
    selected_players: List[str]
    budget_remaining: float
    top_k: int = 10


class SuggestionItem(BaseModel):
    """Individual suggestion"""
    player_name: str
    role: str
    team: str
    price: float
    fit_score: float
    reasoning: str
    confidence: float


class SuggestionsResponse(BaseModel):
    """Suggestions response"""
    success: bool
    data: List[SuggestionItem]
    team_needs: Dict
    message: Optional[str] = None


# ==================== Best XI Schemas ====================

class BestXIRequest(BaseModel):
    """Request for best XI generation"""
    selected_players: List[str]


class PlayingXIGenerate(BaseModel):
    """Generated playing XI"""
    player_name: str
    role: str
    predicted_performance: float
    position: int


class BestXIResponse(BaseModel):
    """Best XI response"""
    success: bool
    playing_xi: List[PlayingXIGenerate]
    bench: List[PlayingXIGenerate]
    team_strength: float
    balance_score: float


# ==================== Simulation Schemas ====================

class MatchSimulationRequest(BaseModel):
    """Match simulation request"""
    team1_players: List[str]
    team2_players: List[str]
    simulations: int = 1000


class MatchSimulationResponse(BaseModel):
    """Match simulation response"""
    success: bool
    team1_win_probability: float
    team2_win_probability: float
    key_performers: List[Dict]
    predicted_score_team1: Optional[float] = None
    predicted_score_team2: Optional[float] = None


# ==================== Auction Strategy Schemas ====================

class AuctionStrategyRequest(BaseModel):
    """Auction strategy request"""
    selected_players: List[str]
    remaining_budget: float
    remaining_slots: int


class PriorityPlayer(BaseModel):
    """Priority player in auction strategy"""
    player_name: str
    role: str
    priority: str  # CRITICAL, HIGH, MEDIUM, LOW
    max_bid: float
    reason: str


class AuctionStrategyResponse(BaseModel):
    """Auction strategy response"""
    success: bool
    priority_queue: List[PriorityPlayer]
    budget_allocation: Dict[str, float]
    strategy_notes: List[str]


# ==================== Analytics Schemas ====================

class AnalyticsResponse(BaseModel):
    """Analytics data response"""
    success: bool
    data: Dict[str, Any]
    timestamp: datetime


# ==================== Health Check Schemas ====================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    models_loaded: bool
    data_loaded: bool
    timestamp: datetime


class MetricsResponse(BaseModel):
    """Model metrics response"""
    success: bool
    models: Dict[str, Dict]
    last_updated: datetime
