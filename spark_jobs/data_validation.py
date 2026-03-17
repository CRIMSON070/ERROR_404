"""
Data Validation and Quality Checks for IPL Dataset
Ensures data quality, detects outliers, validates schema consistency.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when, isnan, isnull, mean, stddev, min, max, approxQuantile
import json
from datetime import datetime

def create_spark_session():
    """Create Spark session"""
    spark = SparkSession.builder \
        .appName("IPL_Data_Validation") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark

def load_data(spark, input_path):
    """Load feature-engineered data"""
    print(f"Loading data from {input_path}...")
    df = spark.read.parquet(input_path)
    print(f"Loaded {df.count()} records")
    return df

def check_schema_consistency(df, expected_columns):
    """Validate schema has required columns"""
    print("\n=== Schema Consistency Check ===")
    
    actual_columns = set(df.columns)
    missing_columns = set(expected_columns) - actual_columns
    extra_columns = actual_columns - set(expected_columns)
    
    if missing_columns:
        print(f"❌ Missing columns: {missing_columns}")
    else:
        print("✅ All required columns present")
    
    if extra_columns:
        print(f"ℹ️  Extra columns: {extra_columns}")
    
    return len(missing_columns) == 0

def check_null_values(df):
    """Check for null/missing values"""
    print("\n=== Null Value Analysis ===")
    
    null_counts = {}
    total_rows = df.count()
    
    for col_name in df.columns:
        null_count = df.filter(col(col_name).isNull()).count()
        null_percentage = (null_count / total_rows) * 100 if total_rows > 0 else 0
        
        if null_count > 0:
            null_counts[col_name] = {
                "count": null_count,
                "percentage": round(null_percentage, 2)
            }
            print(f"⚠️  {col_name}: {null_count} nulls ({null_percentage:.2f}%)")
    
    if not null_counts:
        print("✅ No null values found")
    
    return null_counts

def check_duplicates(df, key_columns):
    """Check for duplicate records"""
    print("\n=== Duplicate Check ===")
    
    total_count = df.count()
    unique_count = df.select(key_columns).distinct().count()
    
    duplicates = total_count - unique_count
    
    if duplicates > 0:
        print(f"⚠️  Found {duplicates} duplicate records")
    else:
        print("✅ No duplicates found")
    
    return duplicates

def detect_outliers_iqr(df, numeric_columns):
    """Detect outliers using IQR method"""
    print("\n=== Outlier Detection (IQR Method) ===")
    
    outliers_summary = {}
    
    for col_name in numeric_columns:
        if col_name not in df.columns:
            continue
        
        try:
            # Calculate quartiles
            quantiles = df.approxQuantile(col_name, [0.25, 0.75], 0.01)
            q1 = quantiles[0]
            q3 = quantiles[1]
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            # Count outliers
            outlier_count = df.filter(
                (col(col_name) < lower_bound) | (col(col_name) > upper_bound)
            ).count()
            
            total_count = df.count()
            outlier_percentage = (outlier_count / total_count) * 100 if total_count > 0 else 0
            
            if outlier_count > 0:
                outliers_summary[col_name] = {
                    "count": outlier_count,
                    "percentage": round(outlier_percentage, 2),
                    "bounds": [round(lower_bound, 2), round(upper_bound, 2)]
                }
                print(f"⚠️  {col_name}: {outlier_count} outliers ({outlier_percentage:.2f}%)")
        
        except Exception as e:
            print(f"Error analyzing {col_name}: {e}")
    
    return outliers_summary

def calculate_statistics(df, numeric_columns):
    """Calculate descriptive statistics for numeric columns"""
    print("\n=== Descriptive Statistics ===")
    
    stats_summary = {}
    
    for col_name in numeric_columns:
        if col_name not in df.columns:
            continue
        
        try:
            stats = df.select(
                mean(col(col_name)).alias("mean"),
                stddev(col(col_name)).alias("stddev"),
                min(col(col_name)).alias("min"),
                max(col(col_name)).alias("max")
            ).first()
            
            stats_summary[col_name] = {
                "mean": round(stats["mean"], 2) if stats["mean"] else 0,
                "stddev": round(stats["stddev"], 2) if stats["stddev"] else 0,
                "min": round(stats["min"], 2) if stats["min"] else 0,
                "max": round(stats["max"], 2) if stats["max"] else 0
            }
            
            print(f"{col_name}: μ={stats_summary[col_name]['mean']}, σ={stats_summary[col_name]['stddev']}, "
                  f"range=[{stats_summary[col_name]['min']}, {stats_summary[col_name]['max']}]")
        
        except Exception as e:
            print(f"Error calculating stats for {col_name}: {e}")
    
    return stats_summary

def validate_data_ranges(df, range_checks):
    """Validate that values are within expected ranges"""
    print("\n=== Range Validation ===")
    
    violations = {}
    
    for col_name, (min_val, max_val) in range_checks.items():
        if col_name not in df.columns:
            continue
        
        violation_count = df.filter(
            (col(col_name) < min_val) | (col(col_name) > max_val)
        ).count()
        
        if violation_count > 0:
            violations[col_name] = violation_count
            print(f"⚠️  {col_name}: {violation_count} values outside [{min_val}, {max_val}]")
    
    if not violations:
        print("✅ All values within expected ranges")
    
    return violations

def check_cardinality(df, categorical_columns):
    """Check cardinality of categorical columns"""
    print("\n=== Categorical Cardinality ===")
    
    cardinality_summary = {}
    
    for col_name in categorical_columns:
        if col_name not in df.columns:
            continue
        
        unique_count = df.select(col(col_name)).distinct().count()
        total_count = df.count()
        
        cardinality_summary[col_name] = {
            "unique_values": unique_count,
            "total_records": total_count,
            "ratio": round(unique_count / total_count, 4) if total_count > 0 else 0
        }
        
        print(f"{col_name}: {unique_count} unique values (ratio: {cardinality_summary[col_name]['ratio']})")
    
    return cardinality_summary

def generate_quality_report(validation_results, output_path):
    """Generate comprehensive data quality report"""
    print("\n=== Generating Quality Report ===")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_records": validation_results.get("total_records", 0),
        "schema_check": validation_results.get("schema_check", False),
        "null_analysis": validation_results.get("null_analysis", {}),
        "duplicate_count": validation_results.get("duplicate_count", 0),
        "outliers": validation_results.get("outliers", {}),
        "statistics": validation_results.get("statistics", {}),
        "range_violations": validation_results.get("range_violations", {}),
        "cardinality": validation_results.get("cardinality", {})
    }
    
    # Calculate overall quality score
    quality_score = 100.0
    
    if not validation_results.get("schema_check", False):
        quality_score -= 20
    
    null_penalty = len(validation_results.get("null_analysis", {})) * 5
    quality_score -= min(null_penalty, 20)
    
    duplicate_penalty = min(validation_results.get("duplicate_count", 0) / 10, 10)
    quality_score -= duplicate_penalty
    
    outlier_penalty = len(validation_results.get("outliers", {})) * 2
    quality_score -= min(outlier_penalty, 15)
    
    violation_penalty = len(validation_results.get("range_violations", {})) * 3
    quality_score -= min(violation_penalty, 15)
    
    report["quality_score"] = max(0, min(100, quality_score))
    
    # Save report
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n{'='*50}")
    print(f"OVERALL DATA QUALITY SCORE: {report['quality_score']:.1f}/100")
    print(f"{'='*50}")
    
    if report["quality_score"] >= 80:
        print("✅ Data quality is GOOD")
    elif report["quality_score"] >= 60:
        print("⚠️  Data quality is ACCEPTABLE")
    else:
        print("❌ Data quality needs IMPROVEMENT")
    
    print(f"\nReport saved to: {output_path}")
    
    return report

def main():
    """Main validation pipeline"""
    spark = create_spark_session()
    
    try:
        # Paths
        input_path = "data/features/engineered_features"
        report_path = "data/analytics/data_quality_report.json"
        
        # Load data
        df = load_data(spark, input_path)
        
        # Define expected columns
        expected_columns = [
            "player_name_raw", "team", "role", "base_price", "sold_price",
            "batting_average", "strike_rate", "wickets_taken", "economy_rate"
        ]
        
        # Numeric columns for analysis
        numeric_columns = [
            "batting_average", "strike_rate", "wickets_taken", "economy_rate",
            "consistency_rating", "overall_impact", "value_for_money"
        ]
        
        # Categorical columns
        categorical_columns = ["role", "team"]
        
        # Expected ranges
        range_checks = {
            "strike_rate": (50.0, 250.0),
            "economy_rate": (4.0, 15.0),
            "batting_average": (0.0, 100.0),
            "consistency_rating": (0.0, 100.0)
        }
        
        # Run validations
        validation_results = {
            "total_records": df.count()
        }
        
        validation_results["schema_check"] = check_schema_consistency(df, expected_columns)
        validation_results["null_analysis"] = check_null_values(df)
        validation_results["duplicate_count"] = check_duplicates(df, ["player_name_raw"])
        validation_results["outliers"] = detect_outliers_iqr(df, numeric_columns)
        validation_results["statistics"] = calculate_statistics(df, numeric_columns)
        validation_results["range_violations"] = validate_data_ranges(df, range_checks)
        validation_results["cardinality"] = check_cardinality(df, categorical_columns)
        
        # Generate report
        quality_report = generate_quality_report(validation_results, report_path)
        
        return quality_report
        
    except Exception as e:
        print(f"Error in validation: {e}")
        raise
    
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
