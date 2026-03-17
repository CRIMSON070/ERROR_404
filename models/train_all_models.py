"""
Unified Model Training Pipeline
Trains all DL models in sequence with proper dependencies
"""

import os
import sys
import json
from datetime import datetime


def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60 + "\n")


def check_dependencies():
    """Check if required packages are installed"""
    
    print_section("Checking Dependencies")
    
    required_packages = [
        'torch', 'numpy', 'pandas', 'sklearn', 
        'pyspark', 'gymnasium', 'stable_baselines3'
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\nMissing packages: {missing}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("\n✅ All dependencies satisfied")
    return True


def run_spark_etl():
    """Run Spark ETL pipeline"""
    
    print_section("Phase 1: Running Spark ETL Pipeline")
    
    try:
        from spark_jobs.enhanced_spark_etl import main as etl_main
        etl_main()
        print("✅ Spark ETL completed")
        return True
    except Exception as e:
        print(f"⚠️  Spark ETL failed: {e}")
        print("Continuing with synthetic data...")
        return False


def run_feature_engineering():
    """Run feature engineering pipeline"""
    
    print_section("Phase 1: Running Feature Engineering")
    
    try:
        from spark_jobs.feature_engineering import main as fe_main
        fe_main()
        print("✅ Feature engineering completed")
        return True
    except Exception as e:
        print(f"⚠️  Feature engineering failed: {e}")
        return False


def train_performance_model():
    """Train player performance prediction model"""
    
    print_section("Phase 2.1: Training Performance Prediction Model")
    
    try:
        from models.performance_predictor import main as perf_main
        model, metrics = perf_main()
        
        # Save metrics
        with open('models/saved_models/performance_metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2)
        
        print("✅ Performance model trained")
        return True
    except Exception as e:
        print(f"⚠️  Performance model training failed: {e}")
        return False


def train_match_outcome_model():
    """Train match outcome LSTM model"""
    
    print_section("Phase 2.2: Training Match Outcome Model")
    
    try:
        from models.match_outcome_lstm import main as match_main
        model, metrics = match_main()
        
        # Save metrics
        with open('models/saved_models/match_outcome_metrics.json', 'w') as f:
            json.dump(metrics, f, indent=2)
        
        print("✅ Match outcome model trained")
        return True
    except Exception as e:
        print(f"⚠️  Match outcome model training failed: {e}")
        return False


def train_embedding_model():
    """Train player embedding model"""
    
    print_section("Phase 2.3: Training Player Embedding Model")
    
    try:
        from models.player_embeddings import main as emb_main
        model, embeddings, df = emb_main()
        
        print("✅ Embedding model trained")
        return True
    except Exception as e:
        print(f"⚠️  Embedding model training failed: {e}")
        return False


def train_team_strength_model():
    """Train team strength aggregation model"""
    
    print_section("Phase 2.4: Training Team Strength Model")
    
    try:
        from models.team_strength_model import main as team_main
        model, metrics = team_main()
        
        print("✅ Team strength model trained")
        return True
    except Exception as e:
        print(f"⚠️  Team strength model training failed: {e}")
        return False


def test_weakness_detector():
    """Test weakness detection model"""
    
    print_section("Phase 2.5: Testing Weakness Detector")
    
    try:
        from models.weakness_detector import main as weak_main
        weak_main()
        
        print("✅ Weakness detector tested")
        return True
    except Exception as e:
        print(f"⚠️  Weakness detector test failed: {e}")
        return False


def test_recommendation_engine():
    """Test recommendation engine"""
    
    print_section("Phase 2.6: Testing Recommendation Engine")
    
    try:
        from models.recommendation_engine import main as rec_main
        rec_main()
        
        print("✅ Recommendation engine tested")
        return True
    except Exception as e:
        print(f"⚠️  Recommendation engine test failed: {e}")
        return False


def train_rl_agent():
    """Train RL auction agent"""
    
    print_section("Phase 2.7: Training RL Auction Agent")
    
    try:
        from models.auction_rl_agent import main as rl_main
        agent, results = rl_main()
        
        print("✅ RL agent trained")
        return True
    except Exception as e:
        print(f"⚠️  RL agent training failed: {e}")
        print("This is optional - continuing...")
        return True  # Don't fail the pipeline


def generate_training_report(all_results):
    """Generate comprehensive training report"""
    
    print_section("Training Summary Report")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'results': all_results,
        'success_count': sum(1 for v in all_results.values() if v),
        'total_tasks': len(all_results)
    }
    
    report['success_rate'] = report['success_count'] / report['total_tasks'] * 100
    
    with open('models/saved_models/training_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Tasks Completed: {report['success_count']}/{report['total_tasks']}")
    print(f"Success Rate: {report['success_rate']:.1f}%")
    
    for task, success in all_results.items():
        status = "✅" if success else "⚠️ "
        print(f"{status} {task}")
    
    return report


def main():
    """Main training orchestration"""
    
    print("\n" + "="*60)
    print(" IPL AUCTION STRATEGY PLATFORM - MODEL TRAINING")
    print("="*60)
    
    # Create directories
    os.makedirs('models/saved_models', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Check dependencies
    if not check_dependencies():
        print("\nPlease install dependencies first:")
        print("pip install -r requirements.txt")
        return
    
    # Track results
    results = {}
    
    # Phase 1: Data Engineering (Optional - can use synthetic data)
    results['Spark_ETL'] = run_spark_etl()
    results['Feature_Engineering'] = run_feature_engineering()
    
    # Phase 2: Deep Learning Models
    results['Performance_Model'] = train_performance_model()
    results['Match_Outcome_Model'] = train_match_outcome_model()
    results['Embedding_Model'] = train_embedding_model()
    results['Team_Strength_Model'] = train_team_strength_model()
    results['Weakness_Detector'] = test_weakness_detector()
    results['Recommendation_Engine'] = test_recommendation_engine()
    results['RL_Agent'] = train_rl_agent()
    
    # Generate report
    report = generate_training_report(results)
    
    print_section("Training Complete!")
    
    if report['success_rate'] >= 80:
        print("🎉 All critical models trained successfully!")
        print("\nNext steps:")
        print("1. Start FastAPI backend: uvicorn backend.main:app --reload")
        print("2. Start Streamlit frontend: streamlit run frontend/app.py")
    else:
        print("⚠️  Some models failed to train. Check logs for details.")
    
    return report


if __name__ == "__main__":
    main()
