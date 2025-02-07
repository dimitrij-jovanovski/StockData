import sqlite3
from datetime import datetime, timedelta


def get_last_date_from_db(issuer_code):
    conn = sqlite3.connect('stock_data.db')
    cursor = conn.cursor()

    cursor.execute('''SELECT MAX(date) FROM stock_prices WHERE issuer_code = ?''', (issuer_code,))
    last_date = cursor.fetchone()[0]

    conn.close()
    return last_date if last_date else None


def determine_start_date(last_date):
    if not last_date:
        # No data exists, start 10 years ago
        start_date = datetime.now() - timedelta(days=365 * 10)
    else:
        # If last_date is in 'DD.MM.YYYY' format, convert it to 'YYYY-MM-DD'
        try:
            # Try to parse the date if it's in 'DD.MM.YYYY' format
            last_date_parsed = datetime.strptime(last_date, "%d.%m.%Y")
        except ValueError:
            # If the date is already in the format '%Y-%m-%d' (or another valid format), pass
            last_date_parsed = datetime.strptime(last_date, "%Y-%m-%d")

        start_date = last_date_parsed

    return start_date.strftime("%Y-%m-%d")
def process_issuer_codes(issuer_codes):
    issuer_dates = {}
    for issuer in issuer_codes:
        last_date = get_last_date_from_db(issuer['code'])
        start_date = determine_start_date(last_date)
        issuer_dates[issuer['code']] = start_date
        # print(f"[DEBUG] Issuer: {issuer['name']} - Code: {issuer['code']} - Start Date: {start_date}")

    return issuer_dates


if __name__ == "__main__":
    issuer_codes = [
        {'name': 'Issuer 1', 'code': 'REPL'},
        {'name': 'Issuer 2', 'code': 'OTHER'}
    ]

    issuer_dates = process_issuer_codes(issuer_codes)
