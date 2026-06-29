import pandas as pd
import os
from sqlalchemy import create_engine

output_dir = "data/bronze/postgres"
os.makedirs(output_dir,exist_ok=True)

engine = create_engine("postgresql://postgres:postgres@localhost:5432/ai_powered_eco_db")

tables = {
    "customers": "select * from customers",
    "order_items": "select * from order_items",
    "orders": "select * from orders",
    "products": "select * from products",
    "reviews": "select * from reviews"

}

for table_name, query in tables.items():
    print(f"Extracting the tabel {table_name}...")
    df = pd.read_sql(query,engine)
    df.to_parquet(f"{output_dir}/{table_name}.parquet",index=False)
    print(f"Save {len(df)} to {output_dir}/{table_name}.parquet")

print("Extraction completed successfully.")