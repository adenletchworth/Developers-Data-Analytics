from pyspark.sql import SparkSession
from pyspark.ml.clustering import LDA

class MongoModels:
    def __init__(self, uri, database, collection):
        self.spark = SparkSession.builder \
            .appName("MongoSparkConnector") \
            .config("spark.mongodb.input.uri", uri) \
            .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:10.3.0") \
            .getOrCreate()
        
        self.df = self.spark.read.format("mongodb") \
            .option("uri", uri) \
            .option("database", database) \
            .option("collection", collection) \
            .load()

    def get_sample(self):
        return self.df.take(1)

    def lda_predict(self, data):
        if not hasattr(self, 'lda_model') or not self.lda_model:
            lda  = LDA(k=3, maxIter=10, seed=1, optimizer="em")
            self.lda_model = lda.fit(self.df)
        model = self.lda_model
        transformed = model.transform(data)
        return transformed

# Update with your actual database and collection names
database_name = "Developer"
collection_name = "github_repos"
models = MongoModels("mongodb://localhost:27017", database_name, collection_name)
print(models.lda_predict(models.get_sample()))
