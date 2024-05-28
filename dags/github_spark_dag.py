from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'start_date': datetime.now() - timedelta(days=1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'github_spark_dag',
    default_args=default_args,
    description='GitHub Spark Processing DAG',
    schedule_interval=None, 
)

spark_task = BashOperator(
    task_id='spark_processing',
    bash_command='spark-submit --py-files /opt/airflow/dags/ETL.zip --packages org.mongodb.spark:mongo-spark-connector_2.12:3.0.1 /opt/airflow/dags/spark_processing.py',
    execution_timeout=timedelta(hours=2),
    dag=dag,
)
