"""Food trucks data pipeline: pipeline. 
This is a combination of the extract, transform, and load modules."""
# Native imports
from argparse import ArgumentParser
from os import environ as ENV, path, mkdir
from shutil import rmtree

# Third library imports
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pymysql

# Local imports
from extract import extract as extract_main
from transform import transform as transform_main


def initialise_args():
    """Gets the cli arguments"""
    parser = ArgumentParser()
    parser.add_argument("-a", "--all_files",  action='store_true',
        help="-a or --all is called to get all truck data from the s3 bucket not just the latest.")
    args = parser.parse_args()
    return args.all_files


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    all_files = initialise_args()
    connection = pymysql.connect(host=ENV["DB_HOST"],
        user=ENV["DB_USER"],
        password=ENV["DB_PASSWORD"],
        database=ENV["DB_NAME"],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)

    # Extract
    extract_main(all_files, connection)
    print("Extracted")

    # Transform
    trucks_df = transform_main()
    if trucks_df is not None:
        print("Transformed")

        # Load
        conn = create_engine(f"mysql+pymysql://{ENV["DB_USER"]}:{ENV["DB_PASSWORD"]}@{ENV["DB_HOST"]}:{ENV["DB_PORT"]}/{ENV["DB_NAME"]}")
        trucks_df.to_sql('Transaction', conn, if_exists='append', index=False)
        print("Loaded")

        # Deletes the csvs to save space
        if path.isdir('truck_data/data'):
            rmtree('truck_data/data')
            mkdir('truck_data/data')

    else:
        print("No new files")
