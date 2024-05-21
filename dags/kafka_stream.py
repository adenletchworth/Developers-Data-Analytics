from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from ETL.extract_gh import GithubExtractor
from ETL.transform_gh import transform
from ETL.load_gh import load_data_into_mongodb
from ETL.ner_module import NamedEntityRecognizer
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
    entity_model = NamedEntityRecognizer('/opt/airflow/dags/NER/models/Transformers')
    
    data = ti.xcom_pull(task_ids='extract')
    transformed_data = transform(data, entity_model)
    return transformed_data

def load_task(ti, **kwargs):
    data = ti.xcom_pull(task_ids='transform')
    load_data_into_mongodb(data)


# def analyze_task():
#     # Implementation of data analysis
#     return None

# def report_task():
#     # Implementation of reporting results
#     return None

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

# analyze_operator = PythonOperator(
#     task_id='analyze',
#     python_callable=analyze_task,
#     dag=dag,
# )

# report_operator = PythonOperator(
#     task_id='report',
#     python_callable=report_task,
#     dag=dag,
# )

extract_operator >> transform_operator >> load_operator 
