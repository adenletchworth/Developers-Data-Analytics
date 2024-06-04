from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from github_producer import github_producer
from dotenv import load_dotenv
import os

load_dotenv()

default_args = {
    'owner': 'airflow',
    'start_date': datetime.now() - timedelta(days=1),
    'retries': 1,
}

dag = DAG(
    'github_stream_to_kafka',
    default_args=default_args,
    description='GitHub Stream to Kafka DAG',
    schedule_interval='*/15 * * * *',  
)

extract_operator = PythonOperator(
    task_id='extract',
    python_callable=github_producer,
    execution_timeout=timedelta(hours=2),
    dag=dag,
)

extract_operator
