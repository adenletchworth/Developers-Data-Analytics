from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from ETL.extract_github import GithubExtractor
from ETL.load_github import load_data_into_mongodb
from ETL.transform_github import DataTransformer  
from dotenv import load_dotenv
import os

load_dotenv()

default_args = {
    'owner': 'airflow',
    'start_date': datetime.now() - timedelta(days=1),
    'retries': 1,
}

dag = DAG(
    'kafka_stream',
    default_args=default_args,
    description='Kafka Stream DAG',
    schedule_interval='@daily',
)

def extract_task(**kwargs):
    extractor = GithubExtractor()
    repos_info = extractor.get()
    return repos_info  

def transform_task(ti, **kwargs):
    data = ti.xcom_pull(task_ids='extract')
    transformer = DataTransformer()
    transformed_data = transformer.transform(data)
    return transformed_data

def load_task(ti, **kwargs):
    data = ti.xcom_pull(task_ids='transform')
    load_data_into_mongodb(data)

extract_operator = PythonOperator(
    task_id='extract',
    python_callable=extract_task,
    execution_timeout=timedelta(hours=2),
    dag=dag,
)

transform_operator = PythonOperator(
    task_id='transform',
    python_callable=transform_task,
    dag=dag,
)

load_operator = PythonOperator(
    task_id='load',
    python_callable=load_task,
    dag=dag,
)

extract_operator >> transform_operator >> load_operator
