from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator  # Correct import for Airflow 2.x
from kafka_consumer import consume_kafka_messages
from ETL.load_github import load_data_into_mongodb

default_args = {
    'owner': 'airflow',
    'start_date': datetime.now(),
    'retries': 1,
}

dag = DAG(
    'github_kafka_consumer',
    default_args=default_args,
    description='GitHub Kafka Consumer DAG',
    schedule_interval='@hourly',  
)

def load_task(**kwargs):
    consume_kafka_messages('github_topic', load_data_into_mongodb, timeout=600)  

load_operator = PythonOperator(
    task_id='load',
    python_callable=load_task,
    execution_timeout=timedelta(hours=2),
    dag=dag,
)

trigger_second_dag = TriggerDagRunOperator(
    task_id='trigger_spark_processing_dag',
    trigger_dag_id='github_spark_dag', 
    dag=dag,
)

load_operator >> trigger_second_dag
