from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from reddit_producer import reddit_producer
from dotenv import load_dotenv
import os

load_dotenv()

default_args = {
    'owner': 'airflow',
    'start_date': datetime.now() - timedelta(days=1),
    'retries': 1,
}

dag = DAG(
    'reddit_stream_to_kafka',
    default_args=default_args,
    description='Reddit Stream to Kafka DAG',
    schedule_interval='@daily',
)

extract_operator = PythonOperator(
    task_id='extract',
    python_callable=reddit_producer,
    execution_timeout=timedelta(hours=2),
    dag=dag,
)

extract_operator
