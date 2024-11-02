from airflow.decorators import dag, task
from pendulum import datetime
import pandas as pd
import yfinance as yf
from sqlalchemy import create_engine

@dag(
    start_date=datetime(2024, 11,1),
    schedule="@daily",
    tags=["transform"],
    catchup=False,
)

def transform_data():
    @task
    def get_db_connection_params():
        return {
            'url': 'postgresql+psycopg2://postgres@host.docker.internal:5432/metrodata'
        }

    @task
    def transform_stock_price(db_params):
        engine = create_engine(db_params['url'])

        table_sql_transform = pd.read_sql(
            sql='''
            SELECT *, (sp."High" - sp."Low") as "Price Range"
            FROM stock_price sp
            WHERE 1=1
            ''',
            con=engine
        )

        TABLE_NAME = 'aggregate_stock_price'
        table_sql_transform.to_sql(name=TABLE_NAME, con=engine, index=False, if_exists='replace')

    @task.bash
    def success():
        return 'echo "The DAG is running well"'

    transform_stock_price(get_db_connection_params()) >> success()

transform_data()