from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, udf, when, size, lit
from pyspark.sql.types import StringType, ArrayType
from keybert import KeyBERT
import logging
import os
import sys
import base64
from pymongo import MongoClient
import re
from markdown import markdown
from bs4 import BeautifulSoup
import nltk

# Ensure necessary NLTK data files are downloaded
nltk.download('punkt')

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

def preprocess_readme(readme):
    if readme:
        # Remove markdown tags
        html = markdown(readme)
        text = ''.join(BeautifulSoup(html, "html.parser").stripped_strings)
        
        # Tokenize
        tokens = nltk.word_tokenize(text)
        
        # Additional preprocessing (e.g., lowercasing, removing special characters)
        tokens = [re.sub(r'\W+', '', token).lower() for token in tokens if re.sub(r'\W+', '', token)]
        
        return ' '.join(tokens)
    return ''

def compress_readme(readme):
    if readme:
        compressed = base64.b64encode(readme.encode('utf-8')).decode('utf-8')
        return compressed
    return ''

# Register UDFs
logger.info("Registering UDFs...")
extract_keywords_udf = udf(extract_keywords, ArrayType(StringType()))
extract_entities_udf = udf(extract_entities, ArrayType(StringType()))
preprocess_readme_udf = udf(preprocess_readme, StringType())
compress_readme_udf = udf(compress_readme, StringType())

if 'description' in df.columns:
    logger.info("Processing 'description' column...")
    df = df.withColumn("keywords_from_description", extract_keywords_udf(col("description")))
    df = df.withColumn("entities_from_description", extract_entities_udf(col("description")))

    df = df.withColumn("keywords_from_description", when(size(col("keywords_from_description")) > 0, col("keywords_from_description")).otherwise(lit(None)))
    df = df.withColumn("entities_from_description", when(size(col("entities_from_description")) > 0, col("entities_from_description")).otherwise(lit(None)))

if 'readme' in df.columns:
    logger.info("Processing 'readme' column...")
    
    # Log some sample readme values before preprocessing
    logger.info("Sample readme values before preprocessing:")
    df.select("readme").show(5, truncate=False)
    
    df = df.withColumn("preprocessed_readme", preprocess_readme_udf(col("readme")))
    
    # Log some sample preprocessed_readme values
    logger.info("Sample preprocessed_readme values after preprocessing:")
    df.select("preprocessed_readme").show(5, truncate=False)
    
    df = df.withColumn("keywords_from_readme", extract_keywords_udf(col("preprocessed_readme")))
    df = df.withColumn("entities_from_readme", extract_entities_udf(col("preprocessed_readme")))
    df = df.withColumn("compressed_readme", compress_readme_udf(col("preprocessed_readme")))
    
    # Log some sample compressed_readme values
    logger.info("Sample compressed_readme values after compression:")
    df.select("compressed_readme").show(5, truncate=False)
    
    df = df.drop("preprocessed_readme", "readme")

    df = df.withColumn("keywords_from_readme", when(size(col("keywords_from_readme")) > 0, col("keywords_from_readme")).otherwise(lit(None)))
    df = df.withColumn("entities_from_readme", when(size(col("entities_from_readme")) > 0, col("entities_from_readme")).otherwise(lit(None)))

# Ensure no duplicates based on 'id'
if 'id' in df.columns:
    logger.info("Dropping duplicates based on 'id' column...")
    df = df.dropDuplicates(['id'])

# Write the processed data back to MongoDB
logger.info("Writing processed data back to MongoDB...")
df.write.format("mongo").mode("overwrite").save()
logger.info("Data written to MongoDB successfully.")

# Initialize MongoDB client to delete raw entries
logger.info("Deleting raw entries from MongoDB...")
client = MongoClient("mongodb://host.docker.internal:27017/")
raw_db = client.Developer.github_repos_raw

# Get list of processed IDs
processed_ids = df.select("id").rdd.flatMap(lambda x: x).collect()

# Delete entries in raw collection based on processed IDs
delete_result = raw_db.delete_many({"id": {"$in": processed_ids}})
logger.info(f"Deleted {delete_result.deleted_count} entries from the raw collection.")

# Stop Spark session
spark.stop()
