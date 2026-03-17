from pyspark.sql import SparkSession
from pyspark.sql.functions import sum

spark = SparkSession.builder \
    .appName("Team Runs Analysis") \
    .getOrCreate()

df = spark.read.parquet(
    "hdfs://localhost:9000/ipl/processed/ball_by_ball_cleaned"
)



team_runs = df.groupBy("BattingTeam").agg(
    sum("TotalRun").alias("TotalRuns")
).orderBy("TotalRuns", ascending=False)

team_runs.show(10)

team_runs.write.mode("overwrite").csv(
    "hdfs://localhost:9000/ipl/analytics/team_runs",
    header=True
)

spark.stop()
