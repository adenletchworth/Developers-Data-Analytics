import os
from google.cloud import bigquery
from typing import Generator, Optional, Union, Dict, List

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/adenletchworth/Downloads/studious-sign-417501-b1d1c2fe9312.json"

def query_bigquery_batched(query: str, parameters: Optional[List[bigquery.ScalarQueryParameter]] = None, batch_size: int = 1000) -> Generator[List[Union[tuple, Dict[str, any]]], None, None]:
    """
    Streams results from a BigQuery SQL query in batches.

    :param query: SQL query string to execute.
    :param parameters: List of bigquery.ScalarQueryParameter objects for query parameterization.
    :param batch_size: Number of results to fetch per batch.
    :yield: Batches of results, each as a list of tuples or dictionaries.
    """
    client = bigquery.Client()

    # Only set query_parameters in job_config if parameters are not None
    job_config = bigquery.QueryJobConfig()
    if parameters:
        job_config.query_parameters = parameters

    try:
        # Execute the query
        query_job = client.query(query, job_config=job_config)

        # Iterate over pages of the query results
        for page in query_job.result(page_size=batch_size).pages:
            batch = [(row.title, row.body) for row in page]
            yield batch
    except Exception as e:
        print(f"An error occurred during query execution: {e}")
        yield []

