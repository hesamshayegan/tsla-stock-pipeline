from airflow.decorators import dag, task
from pendulum import datetime
import pandas as pd
import yfinance as yf
from sqlalchemy import create_engine
import psycopg2

@dag(
    start_date=datetime(2024, 11,1),
    schedule="@daily",
    tags=["extract"],
    catchup=False
)

def extract_load_data():
    @task
    def extract_stock_price():
        tsla = yf.Ticker("TSLA")
        df = tsla.history(start="2014-01-01", end=None)

        df.index = df.index.tz_localize(None)
        df = df.reset_index()
        
        return df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]

    @task
    def load_stock_price(df):
        db_url = 'postgresql+psycopg2://postgres@host.docker.internal:5432/metrodata'
        engine = create_engine(db_url)

        TABLE_NAME = 'stock_price'
        df.to_sql(name=TABLE_NAME, con=engine, index=False, if_exists='replace')

    # task dependencies
    stock_data = extract_stock_price()
    load_stock_price(stock_data)

extract_load_data()