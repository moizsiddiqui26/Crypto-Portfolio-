import sqlite3

def save_to_db(df):

    conn = sqlite3.connect("crypto_trends.db")
    df.to_sql("investment_result", conn, if_exists="replace")
    conn.close()
