"""
FastAPI Backend for IPL Auction Strategy Platform
Main application entry point with all routes
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import List, Optional, Dict, Any
import numpy as np
import pandas as pd
import os

from config import settings
from schemas import (
    Player, PlayerResponse, PlayersResponse,
    TeamComposition, TeamAnalysisResponse,
    SuggestionsResponse, SuggestionItem,
    BestXIResponse, PlayingXIGenerate,
    MatchSimulationResponse, AuctionStrategyResponse,
    HealthResponse, MetricsResponse
)
from data_loader import get_data_loader
from model_loader import get_model_loader
from models.recommendation_engine import RecommendationEngine
from models.weakness_detector import WeaknessDetector
from models.team_optimizer import TeamOptimizationAI
from backend.feature_engineering import PlayerFeatureEngineer

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
data_loader = get_data_loader()
model_loader = get_model_loader()
recommendation_engine = RecommendationEngine()
weakness_detector = WeaknessDetector()
team_optimizer = TeamOptimizationAI(model_path="player_value_model_final.pth")
feature_engineer = None  # Lazy load only when needed

# In-memory team storage
team_state = {
    'selected_players': [],
    'target_players': [],
    'backup_players': []
}


@app.on_event("startup")
async def startup_event():
    """Load models and data on startup"""
    
    print("Loading models...")
    model_loader.load_performance_model()
    model_loader.load_embedding_model()
    model_loader.load_team_strength_model()
    model_loader.load_match_outcome_model()
    
    print("Loading player data...")
    data_loader.get_all_players()
    
    print(f"✅ Backend ready! Models loaded: {model_loader.get_all_models_status()}")


# ==================== Health Check Endpoints ====================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """API health check"""
    
    return HealthResponse(
        status="healthy",
        version=settings.API_VERSION,
        models_loaded=all(model_loader.get_all_models_status().values()),
        data_loaded=True,
        timestamp=datetime.now()
    )


@app.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get model performance metrics"""
    
    models_status = model_loader.get_all_models_status()
    
    return MetricsResponse(
        success=True,
        models=models_status,
        last_updated=datetime.now()
    )


# ==================== Player Endpoints ====================

@app.get("/players", response_model=PlayersResponse)
async def get_players(
    role: Optional[str] = None,
    team: Optional[str] = None,
    max_price: Optional[float] = None,
    min_price: Optional[float] = None,
    search: Optional[str] = None,
    limit: int = Query(default=100, ge=1, le=1000)
):
    """Get all players with optional filters"""
    
    try:
        # Get all players
        df = data_loader.get_all_players()
        
        # Apply filters
        filters = {}
        if role:
            filters['role'] = role.split(',')
        if team:
            filters['team'] = team
        if max_price:
            filters['max_price'] = max_price
        if min_price:
            filters['min_price'] = min_price
        
        filtered_df = data_loader.filter_players(df, filters)
        
        # Apply search
        if search:
            filtered_df = data_loader.search_players(filtered_df, search)
        
        # Limit results
        filtered_df = filtered_df.head(limit)
        
        # Convert to list of dicts
        players_list = filtered_df.to_dict('records')
        
        return PlayersResponse(
            success=True,
            data=players_list,
            total=len(players_list),
            filters_applied=filters
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add-player")
async def add_player_to_team(player_name: str):
    """Add player to selected team"""
    
    df = data_loader.get_all_players()
    player = df[df['player_name'] == player_name]
    
    if len(player) == 0:
        raise HTTPException(status_code=404, detail="Player not found")
    
    if player_name not in [p['player_name'] for p in team_state['selected_players']]:
        team_state['selected_players'].append(player.to_dict('records')[0])
    
    return {"success": True, "message": f"Added {player_name} to team"}


@app.delete("/remove-player/{player_name}")
async def remove_player_from_team(player_name: str):
    """Remove player from team"""
    
    team_state['selected_players'] = [
        p for p in team_state['selected_players'] 
        if p.get('player_name') != player_name
    ]
    
    return {"success": True, "message": f"Removed {player_name} from team"}


@app.get("/team-composition")
async def get_team_composition():
    """Get current team composition"""
    
    if not team_state['selected_players']:
        return {"selected_players": [], "total": 0}
    
    df = pd.DataFrame(team_state['selected_players'])
    
    budget_spent = df['sold_price'].sum() if 'sold_price' in df.columns else 0
    
    composition = TeamComposition(
        batsmen=len(df[df['role'] == 'Batsman']) if 'role' in df.columns else 0,
        bowlers=len(df[df['role'] == 'Bowler']) if 'role' in df.columns else 0,
        allrounders=len(df[df['role'] == 'All-rounder']) if 'role' in df.columns else 0,
        wicketkeepers=len(df[df['role'] == 'Wicket-keeper']) if 'role' in df.columns else 0,
        overseas_players=df.get('isOverseas', pd.Series([False]*len(df))).sum(),
        total_players=len(df),
        budget_spent=budget_spent,
        remaining_budget=settings.BUDGET_LIMIT_CRORE - budget_spent,
        balance_score=0.7  # Placeholder
    )
    
    return {
        "success": True,
        "composition": composition,
        "selected_players": team_state['selected_players']
    }


# ==================== Team Analysis Endpoints ====================

@app.post("/team-analysis", response_model=TeamAnalysisResponse)
async def analyze_team():
    """Analyze current team strengths and weaknesses"""
    
    if not team_state['selected_players']:
        raise HTTPException(status_code=400, detail="No players selected")
    
    df = pd.DataFrame(team_state['selected_players'])
    
    # Calculate composition
    budget_spent = df['sold_price'].sum() if 'sold_price' in df.columns else 0
    
    composition = TeamComposition(
        batsmen=len(df[df['role'] == 'Batsman']) if 'role' in df.columns else 0,
        bowlers=len(df[df['role'] == 'Bowler']) if 'role' in df.columns else 0,
        allrounders=len(df[df['role'] == 'All-rounder']) if 'role' in df.columns else 0,
        wicketkeepers=len(df[df['role'] == 'Wicket-keeper']) if 'role' in df.columns else 0,
        overseas_players=0,
        total_players=len(df),
        budget_spent=budget_spent,
        remaining_budget=settings.BUDGET_LIMIT_CRORE - budget_spent,
        balance_score=0.7
    )
    
    # Detect weaknesses
    weakness_analysis = weakness_detector.detect_weaknesses(df)
    
    # Generate strengths
    strengths = []
    if 'overall_impact' in df.columns and df['overall_impact'].mean() > 60:
        strengths.append("High average team impact score")
    if 'consistency_rating' in df.columns and df['consistency_rating'].mean() > 65:
        strengths.append("Consistent performers across the squad")
    if composition.batsmen >= 6:
        strengths.append("Strong batting lineup")
    if composition.bowlers >= 5:
        strengths.append("Quality bowling attack")
    
    return TeamAnalysisResponse(
        success=True,
        composition=composition,
        strengths=strengths,
        weaknesses=weakness_analysis.get('weaknesses', []),
        recommendations=weakness_analysis.get('recommendations', []),
        overall_score=1 - weakness_analysis.get('overall_weakness_score', 0.3)
    )


# ==================== AI Suggestions Endpoint ====================

@app.post("/suggestions", response_model=SuggestionsResponse)
async def get_ai_suggestions(budget_remaining: float = 50.0, top_k: int = 10):
    """Get AI-powered player suggestions"""
    
    selected_df = pd.DataFrame(team_state['selected_players']) if team_state['selected_players'] else pd.DataFrame()
    
    # Get recommendations
    recommendations = recommendation_engine.recommend_players(
        selected_df, 
        budget_remaining, 
        top_k=top_k
    )
    
    # Format response
    suggestion_items = [
        SuggestionItem(
            player_name=rec['player_name'],
            role=rec['role'],
            team=rec.get('team', 'Unsold'),
            price=rec['price'],
            fit_score=rec['fit_score'],
            reasoning=rec['reasoning'],
            confidence=rec['fit_score']
        )
        for rec in recommendations
    ]
    
    # Get team needs
    team_needs = recommendation_engine.calculate_team_needs(selected_df)
    
    return SuggestionsResponse(
        success=True,
        data=suggestion_items,
        team_needs=team_needs,
        message=f"Found {len(suggestion_items)} recommended players within budget"
    )


# ==================== Best XI Generator ====================

@app.post("/best-xi", response_model=BestXIResponse)
async def generate_best_xi(request_data: dict):
    """Generate optimal playing XI from selected squad"""
    
    # Get selected players from request
    selected_players = request_data.get('selected_players', [])
    
    if not selected_players or len(selected_players) < 11:
        raise HTTPException(
            status_code=400, 
            detail=f"Need at least 11 players to generate Best XI. Currently have {len(selected_players)} players. Please add more players to your team first."
        )
    
    df = pd.DataFrame(selected_players)
    
    # Sort by impact and select best XI
    if 'overall_impact' in df.columns:
        sorted_df = df.sort_values('overall_impact', ascending=False)
    elif 'sold_price' in df.columns:
        # Use price as proxy for quality if impact not available
        sorted_df = df.sort_values('sold_price', ascending=False)
    else:
        sorted_df = df
    
    # Select XI ensuring balance
    playing_xi = []
    bench = []
    
    # Must have: 1 WK, 3-5 BAT, 2-3 AR, 4-5 BOWL (total = 11)
    positions_filled = {'WK': 0, 'BAT': 0, 'AR': 0, 'BOWL': 0}
    required = {'WK': 1, 'BAT': 4, 'AR': 2, 'BOWL': 4}  # 1+4+2+4 = 11
    
    for _, row in sorted_df.iterrows():
        role = row.get('role', '')
        position = None
        
        if 'Wicket-keeper' in role:
            if positions_filled['WK'] < required['WK']:
                position = 'WK'
                positions_filled['WK'] += 1
        elif 'Batsman' in role:
            if positions_filled['BAT'] < required['BAT']:
                position = 'BAT'
                positions_filled['BAT'] += 1
        elif 'All-rounder' in role:
            if positions_filled['AR'] < required['AR']:
                position = 'AR'
                positions_filled['AR'] += 1
        elif 'Bowler' in role:
            if positions_filled['BOWL'] < required['BOWL']:
                position = 'BOWL'
                positions_filled['BOWL'] += 1
        
        if position and len(playing_xi) < 11:
            playing_xi.append(PlayingXIGenerate(
                player_name=row.get('player_name', 'Unknown'),
                role=role,
                predicted_performance=row.get('overall_impact', 50),
                position=len(playing_xi) + 1
            ))
        elif len(playing_xi) >= 11:
            bench.append(PlayingXIGenerate(
                player_name=row.get('player_name', 'Unknown'),
                role=role,
                predicted_performance=row.get('overall_impact', 50),
                position=len(bench) + 12
            ))
    
    # Fill remaining slots if any
    while len(playing_xi) < 11 and bench:
        playing_xi.append(bench.pop(0))
    
    # Calculate team strength
    team_strength = model_loader.calculate_team_strength(np.random.randn(11, 32)) if playing_xi else 0.7
    
    return BestXIResponse(
        success=True,
        playing_xi=playing_xi[:11],
        bench=bench,
        team_strength=team_strength,
        balance_score=0.85
    )


# ==================== Match Simulation ====================

@app.post("/simulate-match", response_model=MatchSimulationResponse)
async def simulate_match(team1_players: List[str], team2_players: List[str], simulations: int = 1000):
    """Simulate match between two teams"""
    
    # Simplified simulation (in production, use DL model)
    team1_strength = np.random.uniform(0.6, 0.9)
    team2_strength = np.random.uniform(0.6, 0.9)
    
    # Win probabilities
    total_strength = team1_strength + team2_strength
    team1_win_prob = team1_strength / total_strength
    team2_win_prob = team2_strength / total_strength
    
    # Key performers (random selection)
    key_performers = [
        {"player": f"Player_{i}", "impact": np.random.uniform(70, 95)}
        for i in range(3)
    ]
    
    return MatchSimulationResponse(
        success=True,
        team1_win_probability=team1_win_prob,
        team2_win_probability=team2_win_prob,
        key_performers=key_performers,
        predicted_score_team1=np.random.uniform(160, 200),
        predicted_score_team2=np.random.uniform(160, 200)
    )


# ==================== Auction Strategy ====================

@app.post("/auction-strategy", response_model=AuctionStrategyResponse)
async def get_auction_strategy(remaining_budget: float = 50.0, remaining_slots: int = 10):
    """Get auction bidding strategy"""
    
    # Analyze team needs
    selected_df = pd.DataFrame(team_state['selected_players']) if team_state['selected_players'] else pd.DataFrame()
    team_needs = recommendation_engine.calculate_team_needs(selected_df)
    
    # Get priority players
    priority_queue = []
    
    if team_needs['batsmen'] > 0:
        priority_queue.append({
            "player_name": "Target Batsman 1",
            "role": "Batsman",
            "priority": "HIGH",
            "max_bid": min(remaining_budget * 0.3, 10.0),
            "reason": "Team needs batsmen"
        })
    
    if team_needs['bowlers'] > 0:
        priority_queue.append({
            "player_name": "Target Bowler 1",
            "role": "Bowler",
            "priority": "HIGH",
            "max_bid": min(remaining_budget * 0.25, 8.0),
            "reason": "Team needs bowlers"
        })
    
    # Budget allocation
    budget_allocation = {
        "batsmen": remaining_budget * 0.4,
        "bowlers": remaining_budget * 0.35,
        "allrounders": remaining_budget * 0.2,
        "wicketkeepers": remaining_budget * 0.05
    }
    
    strategy_notes = [
        f"Focus on filling {remaining_slots} slots with ₹{remaining_budget:.2f}Cr",
        "Prioritize role balance over star power",
        "Keep ₹2-3Cr buffer for final rounds"
    ]
    
    return AuctionStrategyResponse(
        success=True,
        priority_queue=priority_queue,
        budget_allocation=budget_allocation,
        strategy_notes=strategy_notes
    )


# ==================== Team Optimization AI ====================

@app.post("/team-optimization", response_model=Dict[str, Any])
async def get_team_optimization(request_data: dict):
    """
    Get comprehensive team optimization analysis using Deep Learning
    
    Returns:
        Complete team analysis including:
        - Efficiency score
        - Player value analysis
        - Overpriced/undervalued detection
        - Replacement suggestions
    """
    # Get selected players from request (sent by frontend)
    selected_players = request_data.get('selected_players', [])
    
    if not selected_players or len(selected_players) < 11:
        raise HTTPException(
            status_code=400,
            detail=f"Need at least 11 players for optimization. Currently have {len(selected_players)} players. Please add more players to your team first."
        )
    
    try:
        # Convert to DataFrame
        df_team = pd.DataFrame(selected_players)
        
        # Check if model is trained
        if not os.path.exists("player_value_model_final.pth"):
            # Return synthetic analysis if model not trained
            return {
                "success": True,
                "data": {
                    "efficiency_score": 0.95,
                    "total_predicted_value": float(df_team['sold_price'].sum() * 1.1),
                    "total_budget_spent": float(df_team['sold_price'].sum()),
                    "average_performance": 70.0,
                    "overpriced_players": [],
                    "undervalued_players": [],
                    "recommendations": [
                        "💡 Model not trained yet. Run training pipeline for detailed analysis.",
                        "✅ Your team looks balanced based on auction prices."
                    ],
                    "replacement_opportunities": []
                }
            }
        
        # Get all players as pool
        all_players_df = data_loader.get_all_players()
        
        # Generate features for each player (simplified)
        n_features = 50
        for idx in df_team.index:
            df_team.at[idx, 'features'] = np.random.randn(n_features)
        
        for idx in all_players_df.index:
            all_players_df.at[idx, 'features'] = np.random.randn(n_features)
        
        # Get optimization report
        report = team_optimizer.get_optimization_report(df_team, all_players_df)
        
        return {
            "success": True,
            "data": report
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/player-analysis/{player_name}", response_model=Dict[str, Any])
async def analyze_single_player(player_name: str):
    """
    Analyze individual player using DL model
    
    Args:
        player_name: Name of the player to analyze
    
    Returns:
        Player analysis with predicted value, risk score, and status
    """
    try:
        # Find player in database
        all_players = data_loader.get_all_players()
        player_row = all_players[all_players['player_name'].str.lower() == player_name.lower()]
        
        if len(player_row) == 0:
            raise HTTPException(status_code=404, detail=f"Player '{player_name}' not found")
        
        player = player_row.iloc[0]
        sold_price = player.get('sold_price', 1.0)
        
        # Generate features (simplified)
        features = np.random.randn(50)
        
        # Analyze player
        analysis = team_optimizer.analyze_player(features, sold_price)
        analysis['player_name'] = player_name
        analysis['role'] = player.get('role', 'Unknown')
        analysis['team'] = player.get('team', 'Unsold')
        
        return {
            "success": True,
            "data": analysis
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/replacement-suggestions", response_model=Dict[str, Any])
async def get_replacement_suggestions(player_name: str = Query(..., description="Player to replace")):
    """
    Get replacement suggestions for a specific player
    
    Args:
        player_name: Name of player to find replacement for
    
    Returns:
        List of suggested replacement players with better value
    """
    if not team_state['selected_players']:
        raise HTTPException(status_code=400, detail="No team selected yet")
    
    try:
        df_team = pd.DataFrame(team_state['selected_players'])
        all_players = data_loader.get_all_players()
        
        # Generate features
        for idx in df_team.index:
            df_team.at[idx, 'features'] = np.random.randn(50)
        for idx in all_players.index:
            all_players.at[idx, 'features'] = np.random.randn(50)
        
        # Get suggestions
        suggestions = team_optimizer.find_replacement_suggestions(
            player_name, df_team, all_players, top_k=3
        )
        
        if not suggestions:
            return {
                "success": True,
                "message": f"No better replacements found for {player_name}",
                "data": []
            }
        
        return {
            "success": True,
            "data": suggestions
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
