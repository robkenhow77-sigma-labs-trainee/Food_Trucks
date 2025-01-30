"""A script to generate a report of the previous days financial data."""
# Native imports
from os import environ as ENV, path, remove

# Third-party imports
import pymysql
import pandas as pd
from dotenv import load_dotenv

# CSS
TABLE_STYLE = """
    <style>
        table {
            font-family: Arial, Helvetica, sans-serif;
            border-collapse: collapse;
            width: 65%;
            margin-left: auto;
            margin-right: auto;

        }
        table td, table th {
            border: 1px solid #ddd;
            padding: 8px;
        }
        table tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        table tr:hover {
            background-color: #ddd;
        }
        table th {
            padding-top: 12px;
            padding-bottom: 12px;
            text-align: left;
            background-color: #ff8800;
            color: white;
        }
    </style>
    """

H1_STYLE = """
    <style>
        h1 {
            font-family: Arial, Helvetica, sans-serif;
            border-collapse: collapse;
            width: 100%;
            text-align: center;
        }
    </style>
    """

H2_STYLE = """
    <style>
        h2 {
            font-family: Arial, Helvetica, sans-serif;
            border-collapse: collapse;
            width: 100%;
            text-align: center;
        }
    </style>
    """

H3_STYLE = """
    <style>
        h3 {
            font-family: Arial, Helvetica, sans-serif;
            border-collapse: collapse;
            width: 100%;
            text-align: center;
        }
    </style>
    """


# Functions
def get_data(conn: pymysql.Connection):
    """Gets yesterdays data from the database."""
    sql = """
        SELECT * FROM Transaction
        WHERE DATE(at) = DATE(DATE(NOW()) - 2);
    """
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    cur.close()
    return result


def generate_html(total_transaction_value: str,
    transaction_value_per_truck: pd.DataFrame, transactions_per_truck: pd.DataFrame) -> str:
    """Generates the html for the report"""
    return f"""
    {TABLE_STYLE}
    {H1_STYLE}
    {H2_STYLE}
    {H3_STYLE}
    <h1>Daily Trucks Data Report<h1/>
    <h2> Total transaction value: {total_transaction_value} <h2/>
    <h3> Total transaction value per Truck:<h3/>
    {transaction_value_per_truck.to_html()}
    <h3> Total transactions per Truck:<h3/>
    {transactions_per_truck.to_html()}
    """


def create_html_file(html: str) -> None:
    """Generates the html file."""
    if path.exists('report.html'):
        remove('report.html')
    with open('report.html', 'x', encoding='UTF-8') as file:
        file.write(html)


def lambda_handler(event=None, context=None):
    html = main()
    return {"message": html}


def main():
    # Initialise
    load_dotenv()
    conn = pymysql.connect(host=ENV["DB_HOST"],
            user=ENV["DB_USER"],
            password=ENV["DB_PASSWORD"],
            database=ENV["DB_NAME"],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor)
    
    # Get the data
    data = get_data(conn)

    # Create data frame and get relevant data
    df = pd.DataFrame(data)
    value_total_transaction = f'£{round(df['total'].round(2).sum(), 2)}'
    per_truck_transaction_value = df[['total', 'truck_id']].groupby('truck_id').sum().reset_index().rename(columns = {"total": "total - £"})
    per_truck_transactions = df[['total', 'truck_id']].groupby('truck_id').count().reset_index()

    # Generate html
    return generate_html(value_total_transaction, per_truck_transaction_value, per_truck_transactions)


if __name__ == "__main__":
    html = main()
    create_html_file(html)
