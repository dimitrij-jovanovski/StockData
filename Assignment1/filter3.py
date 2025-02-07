import time
import sqlite3
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Function to set up the Selenium driver
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless mode to avoid opening a window
    chrome_options.add_argument("--disable-gpu")

    # Path to your ChromeDriver (adjust the path to where your driver is located)
    service = Service(r"C:\webdrivers\chromedriver-win64\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    print("[INFO] Selenium WebDriver initialized.")
    return driver


# Function to fetch stock data for a specific issuer code
# Function to fetch stock data for a specific issuer code
def fetch_stock_data_for_issuer(issuer_code, start_date, end_date):
    # Initialize the driver
    driver = get_driver()

    # Open the MSE page for the issuer
    url = f"https://www.mse.mk/mk/stats/symbolhistory/{issuer_code}"
    print(f"[INFO] Opening URL: {url}")
    driver.get(url)

    # Wait for the page to load and the form elements to be available
    print("[INFO] Waiting for the page to load...")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'FromDate')))

    # Loop through date intervals of 365 days
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    all_data = []  # Store the extracted data

    while current_date < end_date:
        # Calculate the end of the 365-day range
        next_date = current_date + timedelta(days=365)
        if next_date > end_date:
            next_date = end_date  # Cap the next_date to the final date

        # Format dates in the required format (e.g., 10.10.2023)
        from_date_str = current_date.strftime("%d.%m.%Y")
        to_date_str = next_date.strftime("%d.%m.%Y")

        print(f"[INFO] Setting dates: From {from_date_str} to {to_date_str}")

        # Fill the From and To Date fields
        from_date_input = driver.find_element(By.ID, "FromDate")
        to_date_input = driver.find_element(By.ID, "ToDate")
        from_date_input.clear()
        from_date_input.send_keys(from_date_str)
        to_date_input.clear()
        to_date_input.send_keys(to_date_str)

        # Click the "Прикажи" button
        submit_button = driver.find_element(By.XPATH, '//input[@value="Прикажи"]')
        print("[INFO] Clicking the 'Прикажи' button...")
        submit_button.click()

        # Wait for the table to load
        print("[INFO] Waiting for the stock data table to load...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'resultsTable')))

        # Extract the stock data from the table
        table = driver.find_element(By.ID, 'resultsTable')
        rows = table.find_elements(By.TAG_NAME, 'tr')

        print(f"[INFO] Extracting data from {len(rows) - 1} rows...")  # Subtract 1 for the header row

        # Loop through the rows and extract the data
        for row in rows[1:]:  # Skipping the header row
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) > 1:
                # Extract the data and replace empty values with 0 (or None if appropriate)
                data = {
                    'date': cells[0].text.strip(),
                    'last_transaction_price': european_to_python_number(cells[1].text.strip()),
                    'max_price': european_to_python_number(cells[2].text.strip()),
                    'min_price': european_to_python_number(cells[3].text.strip()),
                    'average_price': european_to_python_number(cells[4].text.strip()),
                    'percentage_change': european_to_python_number(cells[5].text.strip()),
                    'quantity': european_to_python_number(cells[6].text.strip()),
                    'turnover_best_in_denars': european_to_python_number(cells[7].text.strip()),
                    'total_turnover_in_denars': european_to_python_number(cells[8].text.strip())
                }
                print(f"[DEBUG] Extracted data: {data}")
                all_data.append(data)

        # Update the current_date for the next iteration
        current_date = next_date

        # Wait before next iteration (to avoid overloading the server)
        time.sleep(2)

    # Close the driver after finishing the extraction
    print("[INFO] Data extraction complete. Closing the WebDriver.")
    driver.quit()

    return all_data

def european_to_python_number(value):
    # First, remove the thousands separator (dot)
    value = value.replace('.', '')
    # Then, replace the comma (decimal separator) with a dot
    value = value.replace(',', '.')
    return float(value) if value else 0.0


# Function to format prices with commas for thousands and two decimals
def format_price(value):
    if value is None:
        return "0.00"  # Return "0.00" for None values
    return f"{value:,.2f}"  # Format as string with commas for thousands and two decimals


# Function to insert the fetched data into the database
def insert_data_into_db(issuer_code, stock_data):
    conn = sqlite3.connect('stock_data.db')
    cursor = conn.cursor()

    print("[INFO] Inserting data into the database...")

    for entry in stock_data:
        date = entry['date']
        last_transaction_price = format_price(entry['last_transaction_price'])
        max_price = format_price(entry.get('max_price', 0.0))
        min_price = format_price(entry.get('min_price', 0.0))
        average_price = format_price(entry.get('average_price', 0.0))
        percentage_change = format_price(entry.get('percentage_change', 0.0))
        quantity = entry.get('quantity', 0)
        turnover_best_in_denars = format_price(entry.get('turnover_best_in_denars', 0.0))
        total_turnover_in_denars = format_price(entry.get('total_turnover_in_denars', 0.0))

        # Check if the record already exists in the database (based on date and issuer_code)
        cursor.execute('''
            SELECT * FROM stock_prices
            WHERE issuer_code = ? AND date = ?
        ''', (issuer_code, date))
        existing_data = cursor.fetchone()

        if existing_data:
            # If the record exists, update it instead of inserting
            cursor.execute('''
                UPDATE stock_prices SET
                    last_transaction_price = ?, max_price = ?, min_price = ?,
                    average_price = ?, percentage_change = ?, quantity = ?,
                    turnover_best_in_denars = ?, total_turnover_in_denars = ?
                WHERE issuer_code = ? AND date = ?
            ''', (
                last_transaction_price, max_price, min_price,
                average_price, percentage_change, quantity,
                turnover_best_in_denars, total_turnover_in_denars,
                issuer_code, date
            ))
            print(f"[INFO] Updated data for {issuer_code} on {date}.")
        else:
            # If the record does not exist, insert it
            cursor.execute('''
                INSERT INTO stock_prices (
                    issuer_code, date, last_transaction_price, max_price, min_price,
                    average_price, percentage_change, quantity, turnover_best_in_denars,
                    total_turnover_in_denars
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                issuer_code, date, last_transaction_price, max_price, min_price,
                average_price, percentage_change, quantity, turnover_best_in_denars,
                total_turnover_in_denars
            ))
            print(f"[INFO] Inserted new data for {issuer_code} on {date}.")

    conn.commit()
    conn.close()
    print("[INFO] Data inserted into the database successfully.")


def fill_missing_data_for_issuer(issuer_code, start_date):
    # Set the end date (today)
    end_date = datetime.now().strftime("%Y-%m-%d")

    # Fetch stock data from the source (MSE or API)
    print(f"[INFO] Fetching data for {issuer_code} from {start_date} to {end_date}...")
    stock_data = fetch_stock_data_for_issuer(issuer_code, start_date, end_date)

    if not stock_data:
        print(f"[ERROR] No data fetched for {issuer_code} from {start_date} to {end_date}.")
        return

    # Insert the fetched data into the database
    print(f"[INFO] Inserting data for {issuer_code} into the database...")
    insert_data_into_db(issuer_code, stock_data)

    print(f"[INFO] Data for {issuer_code} from {start_date} to {end_date} successfully filled in.")


# # Test the function with a single issuer (ADIN) and a start date
# if __name__ == "__main__":
#     # Hardcode the issuer code (e.g., "ADIN") for testing
#     issuer_code = "ADIN"
#
#     # For now, hardcode a start date (could be fetched from the database in a real case)
#     start_date = "2014-01-01"  # Example: start from January 1, 2014

    fill_missing_data_for_issuer(issuer_code, start_date)