from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from kafka_consumer import consume_kafka_messages
from ETL.load_github import load_data_into_mongodb

default_args = {
    'owner': 'airflow',
    'start_date': datetime.now() - timedelta(days=1),
    'retries': 1,
}

dag = DAG(
    'github_kafka_consumer',
    default_args=default_args,
    description='GitHub Kafka Consumer DAG',
    schedule_interval='@daily',
)

def load_task(**kwargs):
    consume_kafka_messages('github_topic', load_data_into_mongodb)

load_operator = PythonOperator(
    task_id='load',
    python_callable=load_task,
    execution_timeout=timedelta(hours=2),
    dag=dag,
)

spark_task = BashOperator(
    task_id='spark_processing',
    bash_command='spark-submit --packages org.mongodb.spark:mongo-spark-connector_2.12:3.0.1 /opt/airflow/dags/spark_processing.py',
    dag=dag,
)

load_operator >> spark_task
