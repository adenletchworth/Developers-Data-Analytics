import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.types import StringType
import base64
from pyspark.ml.feature import CountVectorizer, Tokenizer
from pyspark.ml.clustering import LDA

os.environ['PYSPARK_PYTHON'] = 'python'

def decode_base64(encoded_str):
    return base64.b64decode(encoded_str).decode('utf-8')

decode_base64_udf = udf(decode_base64, StringType())

class MongoModels:
    def __init__(self, uri, database, collection):
        self.spark = SparkSession.builder \
            .appName("MongoSparkConnector") \
            .config("spark.mongodb.input.uri", uri) \
            .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:10.3.0") \
            .config("spark.executor.memory", "4g") \
            .config("spark.driver.memory", "4g") \
            .getOrCreate()
        
        self.df = self.spark.read.format("mongodb") \
            .option("uri", uri) \
            .option("database", database) \
            .option("collection", collection) \
            .load()
        
        # Decompress the readmes and cache the DataFrame
        self.df = self.df.withColumn("readme", decode_base64_udf(col("compressed_readme"))).cache()

    def get_sample(self):
        return self.df.select("readme").limit(1)

    def lda_predict(self, data):
        try:
            tokenizer = Tokenizer(inputCol="readme", outputCol="words")
            words_data = tokenizer.transform(data).cache()
            
            vectorizer = CountVectorizer(inputCol="words", outputCol="features")
            cv_model = vectorizer.fit(words_data)
            vectorized_data = cv_model.transform(words_data).cache()

            if not hasattr(self, 'lda_model') or not self.lda_model:
                lda = LDA(k=3, maxIter=10, seed=1, optimizer="online")
                self.lda_model = lda.fit(vectorized_data)

            transformed = self.lda_model.transform(vectorized_data)

            topics = self.lda_model.describeTopics()
            vocab = cv_model.vocabulary

            topics_rdd = topics.rdd.map(lambda row: [vocab[idx] for idx in row['termIndices']])
            topics_words = topics_rdd.collect()

            return transformed, topics_words
        except Exception as e:
            print(f"Error during LDA prediction: {e}")
            return None, None
