"""
Weakness Detection Model
Analyzes team composition using DL outputs to identify gaps and weak departments
"""

import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


class WeaknessDetector:
    """
    Hybrid weakness detection combining rule-based analysis and anomaly detection
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.role_requirements = {
            'minimum_batsmen': 5,
            'minimum_bowlers': 5,
            'minimum_allrounders': 3,
            'minimum_wicketkeepers': 1,
            'maximum_overseas': 4
        }
    
    def analyze_team_composition(self, team_df):
        """Analyze basic team composition"""
        
        if 'role' not in team_df.columns:
            return {'error': 'Role column missing'}
        
        # Count roles
        role_counts = team_df['role'].value_counts().to_dict()
        
        total_players = len(team_df)
        
        analysis = {
            'batsmen': role_counts.get('Batsman', 0),
            'bowlers': role_counts.get('Bowler', 0),
            'allrounders': role_counts.get('All-rounder', 0),
            'wicketkeepers': role_counts.get('Wicket-keeper', 0),
            'total_players': total_players,
            'overseas_players': team_df.get('isOverseas', pd.Series([False]*len(team_df))).sum()
        }
        
        return analysis
    
    def detect_weaknesses(self, team_df, player_embeddings=None):
        """Detect weaknesses in team composition"""
        
        weaknesses = []
        severity_scores = []
        
        # 1. Role imbalance detection
        composition = self.analyze_team_composition(team_df)
        
        if composition['batsmen'] < self.role_requirements['minimum_batsmen']:
            weaknesses.append({
                'type': 'weakness',
                'category': 'batting',
                'message': f"Insufficient batsmen: {composition['batsmen']} (minimum required: {self.role_requirements['minimum_batsmen']})",
                'severity': 0.8
            })
            severity_scores.append(0.8)
        
        if composition['bowlers'] < self.role_requirements['minimum_bowlers']:
            weaknesses.append({
                'type': 'weakness',
                'category': 'bowling',
                'message': f"Insufficient bowlers: {composition['bowlers']} (minimum required: {self.role_requirements['minimum_bowlers']})",
                'severity': 0.8
            })
            severity_scores.append(0.8)
        
        if composition['allrounders'] < self.role_requirements['minimum_allrounders']:
            weaknesses.append({
                'type': 'weakness',
                'category': 'balance',
                'message': f"Lack of all-rounders: {composition['allrounders']} (minimum required: {self.role_requirements['minimum_allrounders']})",
                'severity': 0.6
            })
            severity_scores.append(0.6)
        
        if composition['wicketkeepers'] < self.role_requirements['minimum_wicketkeepers']:
            weaknesses.append({
                'type': 'critical',
                'category': 'wicketkeeping',
                'message': "No dedicated wicket-keeper",
                'severity': 0.9
            })
            severity_scores.append(0.9)
        
        # 2. Performance-based weakness detection
        if 'overall_impact' in team_df.columns:
            avg_impact = team_df['overall_impact'].mean()
            
            if avg_impact < 40:
                weaknesses.append({
                    'type': 'weakness',
                    'category': 'overall_performance',
                    'message': f"Low average team impact score: {avg_impact:.1f}",
                    'severity': 0.7
                })
                severity_scores.append(0.7)
        
        # 3. Consistency weakness
        if 'consistency_rating' in team_df.columns:
            avg_consistency = team_df['consistency_rating'].mean()
            
            if avg_consistency < 50:
                weaknesses.append({
                    'type': 'weakness',
                    'category': 'consistency',
                    'message': f"Team lacks consistency: average rating {avg_consistency:.1f}",
                    'severity': 0.5
                })
                severity_scores.append(0.5)
        
        # 4. Bowling variety analysis
        if 'economy_rate' in team_df.columns and 'role' in team_df.columns:
            bowlers_df = team_df[team_df['role'] == 'Bowler']
            
            if len(bowlers_df) > 0:
                avg_economy = bowlers_df['economy_rate'].mean()
                
                if avg_economy > 9.0:
                    weaknesses.append({
                        'type': 'weakness',
                        'category': 'bowling_economy',
                        'message': f"Bowling economy is expensive: {avg_economy:.2f}",
                        'severity': 0.6
                    })
                    severity_scores.append(0.6)
        
        # 5. Batting firepower analysis
        if 'strike_rate' in team_df.columns and 'role' in team_df.columns:
            batsmen_df = team_df[team_df['role'].isin(['Batsman', 'All-rounder'])]
            
            if len(batsmen_df) > 0:
                avg_strike_rate = batsmen_df['strike_rate'].mean()
                
                if avg_strike_rate < 130:
                    weaknesses.append({
                        'type': 'weakness',
                        'category': 'batting_firepower',
                        'message': f"Batting strike rate is low: {avg_strike_rate:.1f}",
                        'severity': 0.5
                    })
                    severity_scores.append(0.5)
        
        # 6. Anomaly detection using embeddings (if available)
        if player_embeddings is not None and len(player_embeddings) > 10:
            anomalies = self.detect_anomalous_players(player_embeddings)
            
            if len(anomalies) > 0:
                weaknesses.append({
                    'type': 'info',
                    'category': 'team_cohesion',
                    'message': f"{len(anomalies)} players may not fit team composition well",
                    'severity': 0.3
                })
                severity_scores.append(0.3)
        
        # Calculate overall weakness score
        overall_weakness_score = np.mean(severity_scores) if severity_scores else 0.0
        
        return {
            'weaknesses': weaknesses,
            'overall_weakness_score': overall_weakness_score,
            'composition': composition,
            'recommendations': self.generate_recommendations(weaknesses)
        }
    
    def detect_anomalous_players(self, player_embeddings):
        """Detect players who are outliers in the team context"""
        
        if len(player_embeddings) < 10:
            return []
        
        # Fit isolation forest
        self.isolation_forest.fit(player_embeddings)
        
        # Predict anomalies (-1 for anomaly, 1 for normal)
        predictions = self.isolation_forest.predict(player_embeddings)
        
        # Get anomalous indices
        anomalous_indices = np.where(predictions == -1)[0]
        
        return anomalous_indices.tolist()
    
    def generate_recommendations(self, weaknesses):
        """Generate recommendations based on detected weaknesses"""
        
        recommendations = []
        
        for weakness in weaknesses:
            category = weakness['category']
            
            if category == 'batting':
                recommendations.append({
                    'priority': 'high',
                    'action': 'Target quality batsmen in upcoming auction',
                    'details': 'Focus on players with high batting average and strike rate'
                })
            
            elif category == 'bowling':
                recommendations.append({
                    'priority': 'high',
                    'action': 'Strengthen bowling department',
                    'details': 'Look for bowlers with good economy rate and wicket-taking ability'
                })
            
            elif category == 'balance':
                recommendations.append({
                    'priority': 'medium',
                    'action': 'Add more all-rounders',
                    'details': 'All-rounders provide balance and flexibility in team composition'
                })
            
            elif category == 'wicketkeeping':
                recommendations.append({
                    'priority': 'critical',
                    'action': 'Acquire a wicket-keeper urgently',
                    'details': 'Essential for team balance'
                })
            
            elif category == 'bowling_economy':
                recommendations.append({
                    'priority': 'medium',
                    'action': 'Focus on economical bowlers',
                    'details': 'Target bowlers with economy rate < 8.0'
                })
            
            elif category == 'batting_firepower':
                recommendations.append({
                    'priority': 'medium',
                    'action': 'Add power hitters',
                    'details': 'Look for batsmen with strike rate > 150'
                })
        
        return recommendations
    
    def predict_department_strength(self, team_df, department):
        """Predict strength of specific department"""
        
        if department == 'batting':
            relevant_roles = ['Batsman', 'Wicket-keeper', 'All-rounder']
            metric = 'strike_rate'
        elif department == 'bowling':
            relevant_roles = ['Bowler', 'All-rounder']
            metric = 'economy_rate'
        else:
            return {'error': 'Invalid department'}
        
        dept_df = team_df[team_df['role'].isin(relevant_roles)]
        
        if len(dept_df) == 0:
            return {'strength': 0.0, 'players': 0}
        
        # Calculate department strength
        if metric in dept_df.columns:
            avg_metric = dept_df[metric].mean()
            
            # Normalize to 0-1 scale
            if department == 'batting':
                strength = min(avg_metric / 200.0, 1.0)
            else:  # bowling
                strength = max(0, 1 - (avg_metric - 6.0) / 6.0)
        else:
            strength = 0.5
        
        return {
            'strength': strength,
            'players': len(dept_df),
            'average_metric': avg_metric if metric in dept_df.columns else None
        }


def main():
    """Test weakness detection"""
    
    print("Testing Weakness Detection Model...")
    
    # Create sample team data
    sample_data = {
        'player_name': ['Player1', 'Player2', 'Player3', 'Player4', 'Player5'],
        'role': ['Batsman', 'Batsman', 'Bowler', 'Bowler', 'All-rounder'],
        'overall_impact': [75, 60, 55, 70, 65],
        'consistency_rating': [80, 70, 60, 75, 68],
        'strike_rate': [145, 138, 0, 0, 140],
        'economy_rate': [0, 0, 7.5, 8.2, 7.8]
    }
    
    team_df = pd.DataFrame(sample_data)
    
    # Initialize detector
    detector = WeaknessDetector()
    
    # Detect weaknesses
    results = detector.detect_weaknesses(team_df)
    
    print("\n=== Team Weakness Analysis ===")
    print(f"Overall Weakness Score: {results['overall_weakness_score']:.2f}")
    print(f"\nComposition: {results['composition']}")
    
    print("\nDetected Weaknesses:")
    for weakness in results['weaknesses']:
        print(f"  - [{weakness['severity']:.1f}] {weakness['message']}")
    
    print("\nRecommendations:")
    for rec in results['recommendations']:
        print(f"  [{rec['priority'].upper()}] {rec['action']}")
        print(f"      {rec['details']}")
    
    # Test department strength
    print("\n=== Department Strength ===")
    batting_strength = detector.predict_department_strength(team_df, 'batting')
    bowling_strength = detector.predict_department_strength(team_df, 'bowling')
    
    print(f"Batting: {batting_strength['strength']:.2f} ({batting_strength['players']} players)")
    print(f"Bowling: {bowling_strength['strength']:.2f} ({bowling_strength['players']} players)")
    
    print("\n✅ Weakness detection model ready!")


if __name__ == "__main__":
    main()
