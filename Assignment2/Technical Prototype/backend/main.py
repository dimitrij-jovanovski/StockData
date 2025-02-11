from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime, timedelta

from Technical_Indicators import get_SMA
from scrapingData import scrape_data

app = Flask(__name__)

def run_scraping():
    print("Starting scraping process...")
    scrape_data()

def get_db_connection():
    conn = sqlite3.connect('stock_data_PROTOTYPE.db')
    conn.row_factory = sqlite3.Row  # To fetch rows as dictionaries
    return conn

@app.route('/api/stocks/<string:issuer_code>', methods=['GET'])
def get_stock_data(issuer_code):
    period = request.args.get('period', 'ALL')  # Default to 'ALL' if no period is specified

    # Get the current date
    current_date = datetime.now()

    try:
        # Build SQL query based on period
        if period == '1D':
            # Query for the last day's data
            query = """
                SELECT * FROM stock_data_PROTOTYPE
                WHERE code = ? AND date >= date('now', '-1 day')
                """
            params = [issuer_code]
        elif period == '7D':
            # Query for the last 7 days of data
            query = """
                SELECT * FROM stock_data_PROTOTYPE
                WHERE code = ? AND date >= date('now', '-7 days')
                """
            params = [issuer_code]
        elif period == '1M':
            # Query for the last month of data
            query = """
                SELECT * FROM stock_data_PROTOTYPE
                WHERE code = ? AND date >= date('now', '-1 month')
                """
            params = [issuer_code]
        elif period == '1Y':
            # Query for the last year of data
            query = """
                SELECT * FROM stock_data_PROTOTYPE
                WHERE code = ? AND date >= date('now', '-1 year')
                """
            params = [issuer_code]
        else:  # 'ALL' period - All available data
            query = "SELECT * FROM stock_data_PROTOTYPE WHERE code = ?"
            params = [issuer_code]

        # Get data from the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        
        data = [dict(row) for row in rows]

        return jsonify(data)

    except sqlite3.DatabaseError as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500

    except Exception as e:
        return jsonify({"error": "Unexpected error", "message": str(e)}), 500

if __name__ == "__main__":
    run_scraping()  
    get_SMA('ADIN', 60)
    app.run(debug=True)
