from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_NAME = os.getenv("POSTGRES_DB")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}"

def load_csv_to_postgres(table_name, csv_path):
    print(f"Loading {table_name}...")
    df = pd.read_csv(csv_path)
    engine = create_engine(DATABASE_URL)
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print(f"✅ {table_name} loaded successfully with {len(df)} rows.")

if __name__ == '__main__':
    base_path = "/data/olist_raw/"

    # Map CSV files to Table Names
    datasets = {
        "customers": "olist_customers_dataset.csv",
        "orders": "olist_orders_dataset.csv",
        "order_items": "olist_order_items_dataset.csv",
        "products": "olist_products_dataset.csv",
        "reviews": "olist_order_reviews_dataset.csv"
    }

    for table, filename in datasets.items():
        load_csv_to_postgres(table, os.path.join(base_path, filename))

    print("🎉 All datasets loaded into PostgreSQL.")

