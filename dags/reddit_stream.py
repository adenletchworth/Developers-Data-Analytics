from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from ETL.extract_reddit import RedditExtractor
from ETL.load_reddit import load_data_into_mongodb 
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

default_args = {
    'owner': 'airflow',
    'start_date': datetime.now() - timedelta(days=1),
    'retries': 1,
}

dag = DAG(
    'reddit_stream',
    default_args=default_args,
    description='Reddit Stream DAG',
    schedule_interval='@daily',
)

def extract_task(**kwargs):
    extractor = RedditExtractor()
    subreddit_name = 'programming'
    posts = extractor.fetch_reddit_data(subreddit_name)
    # Ensure _id is converted to string
    for post in posts:
        if '_id' in post:
            post['_id'] = str(post['_id'])
    return posts

def load_task(ti, **kwargs):
    data = ti.xcom_pull(task_ids='extract')
    load_data_into_mongodb(data)

extract_operator = PythonOperator(
    task_id='extract',
    python_callable=extract_task,
    execution_timeout=timedelta(hours=2),
    provide_context=True,
    dag=dag,
)

load_operator = PythonOperator(
    task_id='load',
    python_callable=load_task,
    provide_context=True,
    dag=dag,
)

extract_operator >> load_operator
