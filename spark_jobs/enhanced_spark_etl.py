"""
Enhanced Spark ETL Pipeline for IPL Auction Strategy Platform
Merges auction data with historical performance, handles missing values,
normalizes features, and stores processed data in Parquet format.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, coalesce, lit, round as spark_round, concat_ws, upper, trim
from pyspark.sql.types import DoubleType, IntegerType, StringType
import os

def create_spark_session():
    """Create optimized Spark session"""
    spark = SparkSession.builder \
        .appName("IPL_Auction_ETL") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .config("spark.sql.parquet.compression.codec", "snappy") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    return spark

def load_auction_data(spark, file_path):
    """Load IPL 2025 auction players data"""
    print(f"Loading auction data from {file_path}...")
    df = spark.read.csv(file_path, header=True, inferSchema=True)
    print(f"Loaded {df.count()} auction players")
    return df

def load_historical_data(spark, file_path):
    """Load 2024 players historical performance data"""
    print(f"Loading historical data from {file_path}...")
    df = spark.read.csv(file_path, header=True, inferSchema=True)
    print(f"Loaded {df.count()} historical records")
    return df

def normalize_player_names(df):
    """Standardize player name formats"""
    return df.withColumn(
        "player_name",
        upper(trim(col("Players")))
    )

def encode_categorical_features(df):
    """Encode categorical variables to numerical"""
    # Role encoding
    role_mapping = {
        "BAT": "Batsman",
        "BOWL": "Bowler",
        "AR": "All-rounder",
        "WK": "Wicket-keeper"
    }
    
    for old, new in role_mapping.items():
        df = df.withColumn("role", when(col("Type") == old, lit(new)).otherwise(col("role")))
    
    # Experience encoding (based on matches played)
    df = df.withColumn(
        "experience",
        when(col("matches_played") < 10, lit("Rookie"))
        .when((col("matches_played") >= 10) & (col("matches_played") < 50), lit("Experienced"))
        .otherwise(lit("Veteran"))
    )
    
    return df

def handle_missing_values(df):
    """Handle missing values with smart imputation"""
    # Fill numeric columns with median
    numeric_cols = ["sold_price", "base_price", "runs_scored", "strike_rate", 
                    "wickets_taken", "economy_rate", "matches_played"]
    
    for col_name in numeric_cols:
        if col_name in df.columns:
            median_val = df.approxQuantile(col_name, [0.5], 0.01)[0]
            df = df.withColumn(col_name, coalesce(col(col_name), lit(median_val)))
    
    # Fill categorical with mode
    df = df.fillna({
        "role": "All-rounder",
        "team": "Unsold",
        "country": "India"
    })
    
    return df

def create_derived_features(df):
    """Create derived features for ML models"""
    # Batting metrics
    df = df.withColumn(
        "batting_average",
        when(col("innings_batted") > 0, col("runs_scored") / col("innings_batted"))
        .otherwise(lit(0.0))
    )
    
    # Bowling metrics
    df = df.withColumn(
        "bowling_average",
        when(col("overs_bowled") > 0, col("runs_conceded") / col("wickets_taken"))
        .otherwise(lit(99.99))
    )
    
    # Consistency score
    df = df.withColumn(
        "consistency_score",
        (col("strike_rate") / 100.0) * 0.6 + 
        (col("batting_average") / 50.0) * 0.4
    )
    
    # Value score (performance per crore)
    df = df.withColumn(
        "value_score",
        when(col("sold_price") > 0, 
             (col("runs_scored") + col("wickets_taken") * 10) / col("sold_price"))
        .otherwise(lit(0.0))
    )
    
    # Performance index
    df = df.withColumn(
        "performance_index",
        (col("runs_scored") * 0.5 + 
         col("wickets_taken") * 20 + 
         col("strike_rate") * 0.3 - 
         col("economy_rate") * 2)
    )
    
    return df

def merge_datasets(auction_df, historical_df):
    """Merge auction data with historical performance"""
    print("Merging auction and historical datasets...")
    
    # Normalize names in both datasets
    auction_df = auction_df.withColumnRenamed("Players", "player_name_raw")
    historical_df = historical_df.withColumnRenamed("player_name", "player_name_hist")
    
    # Simple merge on player name
    merged_df = auction_df.join(
        historical_df,
        auction_df.player_name_raw == historical_df.player_name_hist,
        how="left"
    ).drop("player_name_hist")
    
    print(f"Merged dataset has {merged_df.count()} records")
    return merged_df

def select_final_columns(df):
    """Select and order final columns for output"""
    final_columns = [
        "player_name_raw", "team", "role", "base_price", "sold_price",
        "country", "matches_played", "runs_scored", "strike_rate",
        "wickets_taken", "economy_rate", "batting_average", "bowling_average",
        "consistency_score", "value_score", "performance_index", "experience"
    ]
    
    available_cols = [c for c in final_columns if c in df.columns]
    return df.select(available_cols)

def save_to_parquet(df, output_path):
    """Save processed DataFrame to Parquet format"""
    print(f"Saving processed data to {output_path}...")
    
    # Ensure directory exists
    os.makedirs(output_path, exist_ok=True)
    
    df.write.mode("overwrite").parquet(output_path)
    print(f"Successfully saved {df.count()} records to Parquet")

def main():
    """Main ETL pipeline"""
    spark = create_spark_session()
    
    try:
        # File paths
        auction_file = "ipl_2025_auction_players.csv"
        historical_file = "data/raw/2024_players_details.csv"
        output_dir = "data/processed/auction_players"
        
        # Load data
        auction_df = load_auction_data(spark, auction_file)
        historical_df = load_historical_data(spark, historical_file)
        
        # Process auction data
        auction_df = normalize_player_names(auction_df)
        auction_df = auction_df.withColumnRenamed("Sold", "sold_price")
        auction_df = auction_df.withColumnRenamed("Base", "base_price")
        auction_df = auction_df.withColumnRenamed("Team", "team")
        auction_df = auction_df.withColumnRenamed("Type", "type")
        
        # Add placeholder columns if historical data not available
        auction_df = auction_df.withColumn("matches_played", lit(0).cast(IntegerType()))
        auction_df = auction_df.withColumn("runs_scored", lit(0).cast(DoubleType()))
        auction_df = auction_df.withColumn("strike_rate", lit(0.0).cast(DoubleType()))
        auction_df = auction_df.withColumn("wickets_taken", lit(0).cast(IntegerType()))
        auction_df = auction_df.withColumn("economy_rate", lit(0.0).cast(DoubleType()))
        auction_df = auction_df.withColumn("innings_batted", lit(0).cast(IntegerType()))
        auction_df = auction_df.withColumn("overs_bowled", lit(0.0).cast(DoubleType()))
        auction_df = auction_df.withColumn("runs_conceded", lit(0).cast(DoubleType()))
        auction_df = auction_df.withColumn("country", lit("India").cast(StringType()))
        
        # Create derived features
        auction_df = create_derived_features(auction_df)
        
        # Handle missing values
        auction_df = handle_missing_values(auction_df)
        
        # Select final columns
        final_df = select_final_columns(auction_df)
        
        # Save to Parquet
        save_to_parquet(final_df, output_dir)
        
        # Show sample
        print("\nSample processed data:")
        final_df.show(10, truncate=False)
        print(f"\nSchema:")
        final_df.printSchema()
        
    except Exception as e:
        print(f"Error in ETL pipeline: {e}")
        raise
    
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
