"""Food trucks data pipeline: transform"""
# Standard library imports
from os import listdir, path, environ as ENV
from argparse import ArgumentParser

# Third-party imports
import pandas as pd
import pymysql

# Local module
from extract import extract as extract_main


def get_files():
    return listdir("truck_data/data")


def combine_transaction_data_files(files: list[str]) -> pd.DataFrame:
    """Loads and combines relevant files from the data/ folder.
    Produces a single pandas DataFrame."""
    trucks_dfs = []
    for file in files:
        df = pd.read_csv(f'truck_data/data/{file}')
        truck_id = int(file.split("_")[-2].replace("T", ""))
        df["truck_id"] = truck_id
        trucks_dfs.append(df)

    return pd.concat(trucks_dfs)


def clean_at_column(df: pd.DataFrame) -> pd.DataFrame:
    """Rename timestamp to at."""
    df = df.rename(columns={"timestamp": "at"})
    return df


def clean_truck_id_column(df: pd.DataFrame) -> pd.DataFrame:
    """Change truck_id to int"""
    df['truck_id'] = pd.to_numeric(df['truck_id'])
    df = df[df['truck_id'].notna()]
    return df


def clean_total_column(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans the total column and returns a dataframe with a clean total column."""
    df['total'] = pd.to_numeric(df['total'], errors='coerce')
    df = df.dropna()
    df["total"] = df['total'].apply(lambda x: abs(x) if abs(x) < 100 else round(abs(x)/100, 2))
    return df


def clean_type_column(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans the type column, 
    removes any type that isn't cash or card (crypto not accepted)."""
    df = df[(df['type'].str.lower() == 'cash') | (df['type'].str.lower() == 'card')]
    df['type'] = df['type'].str.lower()
    df = df.rename(columns={"type": "payment_method_id"})
    return df


def get_payment_mapping(conn: object) -> dict:
    """Reads mapping data from a file and returns it as a dictionary."""
    sql = """SELECT * FROM Payment_Method"""
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    cur.close()
    return {row['payment_method']: row['payment_method_id'] for row in result}


def apply_mapping(df: pd.DataFrame, payment_mapping: dict) -> pd.DataFrame:
    df['payment_method_id'] = df['payment_method_id'].apply(lambda x: payment_mapping[x])
    return df


def transform() -> pd.DataFrame:
    files = get_files()
    if len(files) != 0:
        trucks_df = combine_transaction_data_files(files)
        trucks_df = clean_at_column(trucks_df)
        trucks_df = clean_truck_id_column(trucks_df)
        trucks_df = clean_total_column(trucks_df)
        trucks_df = clean_type_column(trucks_df)
       
        conn = pymysql.connect(host=ENV["DB_HOST"],
                user=ENV["DB_USER"],
                password=ENV["DB_PASSWORD"],
                database=ENV["DB_NAME"],
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor)
        
        trucks_df = apply_mapping(trucks_df, get_payment_mapping(conn))
        conn.close()
        trucks_df.reset_index(drop=True)

        return trucks_df
    return None

if __name__ == "__main__":
    data_frame = transform()
       
    
    

    
    

