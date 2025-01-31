"""Food trucks data pipeline: extract"""
# Standard library imports
from os import environ as ENV, path, makedirs
from shutil import rmtree
from argparse import ArgumentParser
from datetime import datetime

# Third-party imports
from boto3 import client
from dotenv import load_dotenv
import pymysql


def initialise_argsparse() -> bool:
    """Initialise CLI arguments"""
    parser = ArgumentParser()
    parser.add_argument("-s", "--single", action='store_true',
        help="-s or --single run the file on it's own or part of pipeline script.")
    parser.add_argument("-a", "--all_files",  action='store_true',
        help="-a or --all is called to get all truck data from the s3 bucket not just the latest.")
    args = parser.parse_args()
    return args.single, args.all_files


def initialise_folders(all_files: bool, conn: pymysql.Connection):
    """Creates a data/ folder if it does not exist. Resets the database downloaded files."""
    if all_files:

        if path.isdir('truck_data/data'):
            rmtree('truck_data/data')
        makedirs('truck_data/data')

        cur = conn.cursor()
        cur.execute("DELETE FROM uploaded_files;")
        conn.commit()
        cur.close()

    else:
        if not path.isdir('truck_data'):
            makedirs('truck_data')
        if not path.isdir('truck_data/data'):
            makedirs('truck_data/data')


def get_uploaded_files(conn: pymysql.Connection) -> list[str]:
    """Gets a list of the uploaded files."""
    sql = """SELECT * FROM uploaded_files;"""
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    cur.close()
    return [file["filename"] for file in result]


def get_s3_files(s3_client) -> list[str]:
    """Gets all the truck files in the s3 bucket."""
    objs = s3_client.list_objects(Bucket=ENV["BUCKET"])
    contents = objs["Contents"]
    return [obj["Key"] for obj in contents if 'trucks/' in obj["Key"]]


def get_files_for_transform(uploaded_files: datetime, s3_files: list[str]) -> list[str]:
    """Finds the files that have not been uploaded."""
    return [file for file in s3_files if file not in uploaded_files]


def download_truck_data_files(s3_client, files: list, conn: pymysql.Connection) -> list[str]:
    """Downloads relevant files from S3 to a data/ folder."""
    try:
        for file in files:
            s3_client.download_file(ENV["BUCKET"], file,
                    f'truck_data/data/{file.replace("/", "_")}')

        cur = conn.cursor()
        cur.executemany("""
            INSERT INTO uploaded_files (filename)
            VALUES (%s)
            """, files)
        conn.commit()
        cur.close()
    except:
        print("Error downloading S3 files.")


def extract(all_files: bool, conn: pymysql.Connection):
    """Main function for the extract module."""
    s3 = client('s3', aws_access_key_id=ENV["ACCESS_KEY"],
                aws_secret_access_key = ENV["SECRET_KEY"])
    initialise_folders(all_files, conn)
    s3_files = get_s3_files(s3)
    files_uploaded = get_uploaded_files(conn)
    if not all_files:
        files_for_transform = get_files_for_transform(files_uploaded, s3_files)
    else:
        files_for_transform = s3_files
    download_truck_data_files(s3, files_for_transform, conn)


if __name__ == "__main__":
    # Initialise
    single, download_all = initialise_argsparse()
    if single:
        load_dotenv()
    connection = pymysql.connect(host=ENV["DB_HOST"],
        user=ENV["DB_USER"],
        password=ENV["DB_PASSWORD"],
        database=ENV["DB_NAME"],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)
    
    # Extract
    extract(download_all, connection)
    connection.close()
