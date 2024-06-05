import os
import re
import nltk
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, to_date
from pyspark.sql.types import StringType, ArrayType
import base64
from pyspark.ml.feature import CountVectorizer, Tokenizer, StopWordsRemover
from pyspark.ml.clustering import LDA

nltk.download('words')
from nltk.corpus import words

os.environ['PYSPARK_PYTHON'] = 'python'

def decode_base64(encoded_str):
    return base64.b64decode(encoded_str).decode('utf-8')

english_vocab = set(words.words())

def filter_words(word_list):
    return [word for word in word_list if word in english_vocab and len(word) >= 2]

decode_base64_udf = udf(decode_base64, StringType())
filter_words_udf = udf(filter_words, ArrayType(StringType()))

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
        
        self.df = self.df.withColumn("readme", decode_base64_udf(col("compressed_readme"))).cache()

    def aggregate_by_date(self):
        return self.df.withColumn("date", to_date(col("date_field"))).groupBy("date").agg({"readme": "collect_list"})

    def fit_lda(self):
        try:
            tokenizer = Tokenizer(inputCol="readme", outputCol="words")
            words_data = tokenizer.transform(self.df).cache()

            remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")
            filtered_words_data = remover.transform(words_data).cache()

            filtered_words_data = filtered_words_data.withColumn("filtered_words", filter_words_udf(col("filtered_words"))).cache()

            vectorizer = CountVectorizer(inputCol="filtered_words", outputCol="features")
            cv_model = vectorizer.fit(filtered_words_data)
            vectorized_data = cv_model.transform(filtered_words_data).cache()

            lda = LDA(k=10, maxIter=10, seed=1, optimizer="online") 
            self.lda_model = lda.fit(vectorized_data)

            topics = self.lda_model.describeTopics()
            vocab = cv_model.vocabulary

            topics_rdd = topics.rdd.map(lambda row: [vocab[idx] for idx in row['termIndices']])
            topics_words = topics_rdd.collect()

            return topics_words
        except Exception as e:
            print(f"Error during LDA fitting: {e}")
            return None

