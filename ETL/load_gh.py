import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def load_data_into_db(data):
    dbname = "GITHUB-DB"
    user = "postgres"
    password = "tannaz"
    host = "localhost" 
    port = "5432"
    
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    for record in data:
        query = sql.SQL("""
            INSERT INTO developer_stats (repository_name, forks_count, stargazers_count, watchers_count, topics, languages)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (repository_name) DO NOTHING;  # Example conflict handling
        """)
        cursor.execute(query, (
            record['repository_name'], 
            record['forks_count'], 
            record['stargazers_count'], 
            record['watchers_count'], 
            record['topics'],  
            record['languages'], 
        ))

    # Close the connection
    cursor.close()
    conn.close()
