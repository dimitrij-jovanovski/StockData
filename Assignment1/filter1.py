import requests
from bs4 import BeautifulSoup
import sqlite3

def get_issuer_codes():
    url = 'https://www.mse.mk/mk/stats/symbolhistory/REPL'
    response = requests.get(url)

    if response.status_code != 200:
        print("Stranicata nemozese da se prezemi")
        return []

    sp = BeautifulSoup(response.content, 'html.parser')

    select_element = sp.find('select', {'id': 'Code'})

    issuer_data = []
    if select_element:
        options = select_element.find_all('option')

        for option in options:
            issuer_name = option.text.strip()
            issuer_code = option['value'].strip()

            if issuer_name and issuer_code and not any(char.isdigit() for char in issuer_code):
                issuer_data.append({'name': issuer_name, 'code': issuer_code})

    # print(issuer_data)
    return issuer_data




# if __name__ == "__main__":
#
#     # Step 2: Fetch issuer codes
#     issuer_codes = get_issuer_codes()
#