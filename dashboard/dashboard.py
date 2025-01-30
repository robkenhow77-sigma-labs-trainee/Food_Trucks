"""Streamlit app for the project."""
from os import environ as ENV

from dotenv import load_dotenv
import pymysql
import streamlit as st
import altair as alt
import pandas as pd


# Get database connection
def initialise_connection():
    """Gets the connection to the database."""
    return pymysql.connect(host=ENV["DB_HOST"],
                           user=ENV["DB_USER"],
                           password=ENV["DB_PASSWORD"],
                           database=ENV["DB_NAME"],
                           charset='utf8mb4',
                           port=int(ENV["DB_PORT"]),
                           cursorclass=pymysql.cursors.DictCursor)


# Query function
def query(sql_query: str, conn: pymysql.Connection):
    """A function for querying to the database."""
    cur = conn.cursor()
    cur.execute(sql_query)
    output = cur.fetchall()
    cur.close()
    return output


# Get maps
def get_payment_method_map(conn: pymysql.Connection) -> dict:
    """Gets the payment method type and the payment method id"""
    output = query("select * from Payment_Method;", conn)
    return {str(row["payment_method_id"]): str(row["payment_method"]) for row in output}


def get_truck_name_map(conn: pymysql.Connection) -> dict:
    """Gets the truck name and the truck id."""
    output = query("select truck_id, truck_name from Truck;", conn)
    return {str(row["truck_id"]): str(row["truck_name"]) for row in output}


# Dashboard setup
def initialise_dashboard() -> None:
    """Set up the dashboard."""
    st.set_page_config(layout="wide")
    st.title("Truck Sales Dashboard")
    st.write("This dashboard is displaying the sales performance of the food trucks.")
    st.sidebar.title("Options")


def padding(n: int, col) -> None:
    """Add n lines of padding."""
    if col:
        with col:
            for _ in range(n):
                st.write(" ")
    else:
        for _ in range(n):
            st.write(" ")


# Create graphs
def total_sales_graph(conn: pymysql.Connection, col) -> None:
    """Creates a graph of total sales over the last day, week, month or year."""
    _, _, _, d = col.columns(4)
    timeframe = d.selectbox("Select a timeframe",
                                 ["day", "week", "month", "year"], key="total_sales")
    timeframe_map = {
        'day': 'DATE',
        'week': 'WEEK',
        'month': 'MONTH',
        'year': 'YEAR'
    }
    timeframe = timeframe_map[timeframe]
    if timeframe not in ["DATE", "WEEK", "MONTH", "YEAR"]:
        raise ValueError("Invalid timeframe provided")
    cur = conn.cursor()
    cur.execute(f"""
        select sum(total) as total, {timeframe}(at) as time
        from Transaction
        group by {timeframe}(at);
        """)
    output = cur.fetchall()
    cur.close()
    df = pd.DataFrame(output)
    col.line_chart(df, x="time", y="total", use_container_width=True, x_label="Time",
                  y_label="Total Sales £")


def sales_per_truck_graph(conn: pymysql.Connection, col) -> None:
    """Sales per truck over the last day, week, month or year."""
    timeframe = col.selectbox("Select a timeframe", ["day", "week", "month", "year"],
                             key="best_performing_truck")
    timeframe_map = {
        'day': 1,
        'week': 7,
        'month': 31,
        'year': 365
    }
    timeframe = timeframe_map[timeframe]
    if timeframe not in [1, 7, 31, 365]:
        raise ValueError("Invalid timeframe provided")

    cur = conn.cursor()
    cur.execute(f"""
        SELECT SUM(total) AS total, truck_id
        FROM Transaction
        WHERE at > DATE_SUB(NOW(), INTERVAL {timeframe} DAY)
        GROUP BY truck_id;
        """)
    output = cur.fetchall()
    cur.close()
    df = pd.DataFrame(output)
    if len(df.columns) > 1:
        mapping = get_truck_name_map(conn)
        mapped_output = [{'total': row["total"],
                    'truck_name': mapping[str(row['truck_id'])]} for row in output]
        mapped_df = pd.DataFrame(mapped_output)
        chart = alt.Chart(mapped_df).mark_bar().encode(
            alt.X("total", title="Truck sales"),
            alt.Y("truck_name", sort="-x", title="Truck Name"),
            color=alt.Color('truck_name', legend=None)
        )
        col.altair_chart(chart, use_container_width=True)


def payment_proportions_graph(conn: pymysql.Connection, col) -> None:
    """Proportions of payment types."""
    sql = """select count(*) as count, payment_method_id
    from Transaction
    group by payment_method_id;"""
    output = query(sql, conn)
    mapping = get_payment_method_map(conn)
    mapped_output = [{'count': row['count'],
                    'payment_method': mapping[str(row['payment_method_id'])]} for row in output]
    df = pd.DataFrame(mapped_output)
    proportions = alt.Chart(df,
        title=alt.Title("Proportions of payment types", anchor="middle")).mark_arc().encode(
        theta='count',
        color="payment_method"
    )
    col.altair_chart(proportions, use_container_width=True)


def popular_times_graph(conn: pymysql.Connection, col) -> None:
    """Popular times graph"""
    sql = """select hour(at) as hour, count(truck_id) as count
        from Transaction
        group by HOUR(at);"""
    output = query(sql, conn)
    df = pd.DataFrame(output)
    popular_times = alt.Chart(df).mark_bar(size=20).encode(
        alt.X("hour",title="Hour of day"),
        alt.Y("count",title='Number of transactions')
    )
    col.altair_chart(popular_times, use_container_width=True)


# Create metrics
def total_sales_metric(conn: pymysql.Connection, col) -> None:
    """Gets the total sales."""
    sql = """select round(sum(total), 2) as total_sales from Transaction;"""
    total_sales_value = query(sql, conn)[0]['total_sales']
    col.metric(label="Total Sales", value=f'£{total_sales_value}', border =True)


def best_performing_truck_metric(conn: pymysql.Connection, col) -> None:
    """Gets the best performing truck on the day."""
    sql = """select round(sum(total), 2) as total, truck_id
    from Transaction
    where date(at) = (select(max(date(at))) from Transaction) 
    group by truck_id
    order by total desc
    limit 1
    """
    output = query(sql, conn)[0]
    mapping = get_truck_name_map(conn)
    mapped_output = {'total': output["total"], 'truck_name': mapping[str(output['truck_id'])]}
    col.metric(label = f'Truck {mapped_output['truck_name']} is doing best today',
              value=f'£{mapped_output['total']}', border =True)


def todays_sale_metric(conn: pymysql.Connection, col) -> None:
    """"Gets todays total sales."""
    sql = """select round(sum(total), 2) as total from Transaction
    where date(at) = ( select max(date(at)) from Transaction ) ;
    """
    output = query(sql, conn)[0]
    col.metric(label="Total Sales Today", value=f'£{output['total']}', border =True)


def percentage_increase_metric(conn: pymysql.Connection, col) -> None:
    """"Gets the sales percentage change from the previous day."""
    sql = """select sum(total) as total, date(at) as date
    from Transaction 
    group by date(at)
    order by date desc
    limit 2;"""
    output = query(sql, conn)
    today, yesterday = output[0]['total'], output[1]['total']
    percentage_increase = ((today - yesterday) / yesterday) * 100
    col.metric(label="Percentage Increase", value=f'{round(percentage_increase)}%', border =True)


def homepage(conn: pymysql.Connection):
    """Creates the dashboard homepage, see: food_truck_wireframe.png
    columns are in the form: position_row_subcolumn,
    subcolumn a is left b is right. 
    Eg. right_col_3_a is the right hand side column on the third row,
    on the left hand side of the subcolumn
    """
    # Initalise dashboard
    initialise_dashboard()

    # Row 1: Total sales vs time graph
    middle_col_1 = st.columns(1)[0]
    total_sales_graph(conn, middle_col_1)

    # Row 2: Total sales for each truck and payment proportions
    left_col_2, right_col_2 = st.columns(2, border=True)

    # Left column
    sales_per_truck_graph(conn, left_col_2)

    # Right column
    padding(3, right_col_2)
    payment_proportions_graph(conn, right_col_2)

    # Row 3: Popular times graph and metrics
    left_col_3, right_col_3 = st.columns(2, border=True)

    # Left column
    popular_times_graph(conn, left_col_3)

    # Right column
    padding(3, right_col_3)
    right_col_3_a, right_col_3_b = right_col_3.columns(2)
    total_sales_metric(conn, right_col_3_a)
    best_performing_truck_metric(conn, right_col_3_a)
    todays_sale_metric(conn, right_col_3_b)
    percentage_increase_metric(conn, right_col_3_b)


if __name__ == '__main__':
    load_dotenv()
    connection = initialise_connection()
    homepage(connection)
    connection.close()
