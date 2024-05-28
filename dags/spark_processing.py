from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, udf
from keybert import KeyBERT
import logging
import os
import sys

# Add the zipped ETL module to the Python path
sys.path.insert(0, 'ETL.zip')
from ETL.ner_module import NamedEntityRecognizer

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log environment variables
logger.info("Logging environment variables...")
logger.info(f"JAVA_HOME: {os.getenv('JAVA_HOME')}")
logger.info(f"SPARK_HOME: {os.getenv('SPARK_HOME')}")
logger.info(f"PATH: {os.getenv('PATH')}")

# Initialize Spark session
logger.info("Initializing Spark session...")
spark = SparkSession.builder \
    .appName("GitHubDataProcessing") \
    .config("spark.mongodb.input.uri", "mongodb://host.docker.internal:27017/Developer.github_repos_raw") \
    .config("spark.mongodb.output.uri", "mongodb://host.docker.internal:27017/Developer.github_repos") \
    .getOrCreate()

# Log Spark version and configuration
logger.info(f"Spark version: {spark.version}")
logger.info("Spark configuration:")
for key, value in spark.sparkContext.getConf().getAll():
    logger.info(f"{key}: {value}")

# Read data from MongoDB
logger.info("Reading data from MongoDB...")
df = spark.read.format("mongo").load()

# Print schema to debug the structure of the DataFrame
logger.info("DataFrame Schema:")
df.printSchema()

# Initialize KeyBERT and NER models
kw_model = KeyBERT()
entity_model = NamedEntityRecognizer('adenletchworth/CS-NER')

def extract_keywords(text):
    if text:
        keywords = kw_model.extract_keywords(text)
        return [kw[0] for kw in keywords]
    return []

def extract_entities(description):
    if description:
        topics = entity_model.predict(description)
        return list(set(topics))
    return []

# Register UDFs
logger.info("Registering UDFs...")
extract_keywords_udf = udf(extract_keywords)
extract_entities_udf = udf(extract_entities)

# Process 'description' column if it exists
if 'description' in df.columns:
    logger.info("Processing 'description' column...")
    df = df.withColumn("lowercase_description", lower(col("description").cast("string")))
    df = df.withColumn("keywords_from_description", extract_keywords_udf(col("description")))
    df = df.withColumn("entities_from_description", extract_entities_udf(col("description")))

# Process 'readme' column if it exists
if 'readme' in df.columns:
    logger.info("Processing 'readme' column...")
    df = df.withColumn("keywords_from_readme", extract_keywords_udf(col("readme")))
    df = df.withColumn("entities_from_readme", extract_entities_udf(col("readme")))

# Write the processed data back to MongoDB
logger.info("Writing processed data back to MongoDB...")
df.write.format("mongo").mode("overwrite").save()
logger.info("Data written to MongoDB successfully.")

# Stop Spark session
spark.stop()
