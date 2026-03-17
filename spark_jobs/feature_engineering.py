"""
Feature Engineering Pipeline for IPL Deep Learning Models
Generates advanced features including sequence features, interaction terms,
and aggregated statistics for model training.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lag, avg, stddev, when, round as spark_round, array, udf
from pyspark.sql.window import Window
from pyspark.ml.feature import VectorAssembler, StandardScaler, StringIndexer
import numpy as np

def create_spark_session():
    """Create Spark session for feature engineering"""
    spark = SparkSession.builder \
        .appName("IPL_Feature_Engineering") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark

def load_processed_data(spark, input_path):
    """Load processed Parquet data"""
    print(f"Loading processed data from {input_path}...")
    df = spark.read.parquet(input_path)
    print(f"Loaded {df.count()} records")
    return df

def create_batting_features(df):
    """Create advanced batting features"""
    # Boundary percentage
    df = df.withColumn(
        "boundary_percentage",
        when(col("runs_scored") > 0, 
             (col("strike_rate") - 100) * 0.5).otherwise(lit(0.0))
    )
    
    # Rotational strike ability
    df = df.withColumn(
        "rotational_strike",
        col("batting_average") * 0.7 + col("strike_rate") * 0.3
    )
    
    # Power play performance index
    df = df.withColumn(
        "powerplay_index",
        col("strike_rate") * 1.2 - col("batting_average") * 0.2
    )
    
    # Death overs specialty
    df = df.withColumn(
        "death_overs_index",
        col("strike_rate") * 1.5 + col("boundary_percentage") * 0.5
    )
    
    return df

def create_bowling_features(df):
    """Create advanced bowling features"""
    # Wicket-taking ability
    df = df.withColumn(
        "wicket_taking_index",
        col("wickets_taken") / when(col("matches_played") > 0, col("matches_played")).otherwise(lit(1))
    )
    
    # Economy control
    df = df.withColumn(
        "economy_control",
        10.0 - col("economy_rate")
    )
    
    # Dot ball pressure (estimated)
    df = df.withColumn(
        "dot_ball_pressure",
        (10.0 - col("economy_rate")) * 0.6 + col("wicket_taking_index") * 0.4
    )
    
    # Power play bowling index
    df = df.withColumn(
        "powerplay_bowling_index",
        col("economy_control") * 1.3 + col("wicket_taking_index") * 0.7
    )
    
    # Death overs bowling index
    df = df.withColumn(
        "death_bowling_index",
        col("economy_control") * 0.8 + col("wicket_taking_index") * 1.2
    )
    
    return df

def create_allrounder_features(df):
    """Create specialized all-rounder metrics"""
    # Dual threat score
    df = df.withColumn(
        "dual_threat_score",
        when((col("role") == "All-rounder"),
             col("batting_average") * 0.5 + col("wicket_taking_index") * 20.0)
        .otherwise(lit(0.0))
    )
    
    # Balance index
    df = df.withColumn(
        "balance_index",
        abs(col("batting_average") - col("wicket_taking_index") * 10)
    )
    
    return df

def create_consistency_features(df):
    """Create consistency and form features"""
    # Consistency rating (0-100)
    df = df.withColumn(
        "consistency_rating",
        spark_round(
            (col("consistency_score") / 2.0) * 100, 2
        ).cast("double")
    )
    
    # Recent form index (simulated)
    df = df.withColumn(
        "recent_form_index",
        col("performance_index") * 0.6 + col("consistency_rating") * 0.4
    )
    
    # Pressure performance index
    df = df.withColumn(
        "pressure_index",
        col("strike_rate") * 0.5 + col("economy_control") * 0.5
    )
    
    return df

def create_interaction_features(df):
    """Create interaction features between batting and bowling"""
    # Batting impact
    df = df.withColumn(
        "batting_impact",
        col("runs_scored") * col("strike_rate") / 100.0
    )
    
    # Bowling impact
    df = df.withColumn(
        "bowling_impact",
        col("wickets_taken") * (10.0 - col("economy_rate"))
    )
    
    # Overall impact score
    df = df.withColumn(
        "overall_impact",
        col("batting_impact") * 0.6 + col("bowling_impact") * 0.4
    )
    
    # Value for money
    df = df.withColumn(
        "value_for_money",
        col("overall_impact") / when(col("sold_price") > 0, col("sold_price")).otherwise(lit(1))
    )
    
    return df

def create_role_specific_features(df):
    """Create features specific to player roles"""
    # Opener suitability
    df = df.withColumn(
        "opener_suitability",
        when(col("role") == "Batsman",
             col("batting_average") * 0.7 + col("consistency_rating") * 0.3)
        .otherwise(lit(0.0))
    )
    
    # Finisher suitability
    df = df.withColumn(
        "finisher_suitability",
        when((col("role") == "Batsman") | (col("role") == "All-rounder"),
             col("strike_rate") * 1.5 + col("pressure_index") * 0.5)
        .otherwise(lit(0.0))
    )
    
    # Strike bowler suitability
    df = df.withColumn(
        "strike_bowler_suitability",
        when(col("role") == "Bowler",
             col("wicket_taking_index") * 0.6 + col("economy_control") * 0.4)
        .otherwise(lit(0.0))
    )
    
    # Economy bowler suitability
    df = df.withColumn(
        "economy_bowler_suitability",
        when(col("role") == "Bowler",
             col("economy_control") * 0.8 + col("consistency_rating") * 0.2)
        .otherwise(lit(0.0))
    )
    
    return df

def assemble_feature_vector(df):
    """Assemble all features into a single vector for DL models"""
    feature_columns = [
        "batting_average", "strike_rate", "wicket_taking_index", "economy_control",
        "consistency_rating", "recent_form_index", "pressure_index",
        "batting_impact", "bowling_impact", "overall_impact", "value_for_money",
        "boundary_percentage", "rotational_strike", "powerplay_index",
        "death_overs_index", "dot_ball_pressure", "powerplay_bowling_index",
        "death_bowling_index", "dual_threat_score", "balance_index",
        "opener_suitability", "finisher_suitability", "strike_bowler_suitability",
        "economy_bowler_suitability"
    ]
    
    # Filter available columns
    available_features = [c for c in feature_columns if c in df.columns]
    
    assembler = VectorAssembler(
        inputCols=available_features,
        outputCol="features_vector"
    )
    
    df = assembler.transform(df)
    
    return df

def normalize_features(df):
    """Normalize numerical features using StandardScaler"""
    feature_cols = [
        "batting_average", "strike_rate", "wicket_taking_index", "economy_control",
        "consistency_rating", "overall_impact", "value_for_money"
    ]
    
    available_cols = [c for c in feature_cols if c in df.columns]
    
    for col_name in available_cols:
        mean_val = df.agg({col_name: "mean"}).first()[0]
        std_val = df.agg({col_name: "stddev"}).first()[0] or 1.0
        
        df = df.withColumn(
            f"{col_name}_normalized",
            (col(col_name) - mean_val) / std_val
        )
    
    return df

def save_features(df, output_path):
    """Save engineered features to Parquet"""
    print(f"Saving features to {output_path}...")
    df.write.mode("overwrite").parquet(output_path)
    print(f"Saved {df.count()} records with engineered features")

def main():
    """Main feature engineering pipeline"""
    spark = create_spark_session()
    
    try:
        # Paths
        input_path = "data/processed/auction_players"
        output_path = "data/features/engineered_features"
        
        # Load processed data
        df = load_processed_data(spark, input_path)
        
        # Create feature categories
        print("Creating batting features...")
        df = create_batting_features(df)
        
        print("Creating bowling features...")
        df = create_bowling_features(df)
        
        print("Creating all-rounder features...")
        df = create_allrounder_features(df)
        
        print("Creating consistency features...")
        df = create_consistency_features(df)
        
        print("Creating interaction features...")
        df = create_interaction_features(df)
        
        print("Creating role-specific features...")
        df = create_role_specific_features(df)
        
        print("Assembling feature vectors...")
        df = assemble_feature_vector(df)
        
        print("Normalizing features...")
        df = normalize_features(df)
        
        # Save features
        save_features(df, output_path)
        
        # Show sample
        print("\nSample features:")
        df.select("player_name_raw", "role", "overall_impact", "value_for_money", 
                  "consistency_rating").show(10, truncate=False)
        
        print(f"\nTotal features created: {len(df.columns)}")
        
    except Exception as e:
        print(f"Error in feature engineering: {e}")
        raise
    
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
