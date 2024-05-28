from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower
from keybert import KeyBERT
from ETL.ner_module import NamedEntityRecognizer

# Initialize Spark session
spark = SparkSession.builder \
    .appName("GitHubDataProcessing") \
    .config("spark.mongodb.input.uri", "mongodb://host.docker.internal:27017/github_db.developer_stats") \
    .config("spark.mongodb.output.uri", "mongodb://host.docker.internal:27017/developer.github_processed_data") \
    .getOrCreate()

# Read data from MongoDB
df = spark.read.format("mongo").load()

# Print schema to debug the structure of the DataFrame
df.printSchema()

# Example processing: Check if the 'description' column exists and process accordingly
if 'description' in df.columns:
    processed_df = df.withColumn("lowercase_description", lower(col("description").cast("string")))
else:
    print("Column 'description' not found in the DataFrame")
    processed_df = df  # or handle the absence of the column as needed

# Write the processed data back to MongoDB
processed_df.write.format("mongo").mode("overwrite").save()

# Perform additional processing like KeyBERT and NER using Python UDFs
kw_model = KeyBERT()
entity_model = NamedEntityRecognizer('allenai/scibert_scivocab_uncased')

def extract_keywords(text):
    if text:
        keywords = kw_model.extract_keywords(text)
        return [kw[0] for kw in keywords]
    return []

def extract_entities(description):
    if description is None:
        return []
    topics = entity_model.predict(description)
    return list(set(topics))

spark.udf.register("extract_keywords", extract_keywords)
spark.udf.register("extract_entities", extract_entities)

# Apply UDFs
if 'readme_text' in processed_df.columns:
    processed_df = processed_df.withColumn("keywords", extract_keywords(col("readme_text")))
    processed_df = processed_df.withColumn("entities", extract_entities(col("readme_text")))

# Write the fully processed data back to MongoDB
processed_df.write.format("mongo").mode("overwrite").save()
