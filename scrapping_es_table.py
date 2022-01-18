import datetime
import traceback

import requests
from bs4 import BeautifulSoup
from help_functions import *
import pandas as pd
import numpy as np


def store_new_table(scrapping_key):
    headers = {
        'authority': 'www.elliottwavetrader.net',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.elliottwavetrader.net/trading-room/product/14/post-type/initial',
        'accept-language': 'en-US,en;q=0.9',
    }

    cookies = {
        'fbUser': scrapping_key
    }

    response = requests.get('https://www.elliottwavetrader.net/es-trade-alerts', cookies=cookies, headers=headers)
#
    file_write('logs/scrapped_table.html', response.text)


def format_tables():

    response = open_file('logs/scrapped_table.html')

    soup = BeautifulSoup(response, 'lxml')

    all_trades = []
    other_tables = []

    all_tables = soup.find_all('tr')

    for tab in all_tables:
        for all_a in tab.find_all('a'):
            if '/advanced' in all_a['href']:
                all_trades.append(tab)
            else:
                other_tables.append(tab)

    return all_trades


def format_all_trades(all_trades):

    def format_row(idx):
        if len(rows) > idx:
            return rows[idx].text

    def handle_date(dt):
        if dt:
            dates = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}
            d, m, y = dt.split('-')
            return datetime.datetime(2000+int(y), int(dates[m.lower()]), int(d))

    def handle_num(nm):
        if nm:
            return float(nm.replace(',', ''))

    res = {i: [] for i in ['symbol', 'trade_type', 'time_opened', 'timeframe', 'entry_price', 'time_closed', 'exit_price', 'profit']}

    for trade in all_trades:

        try:
            rows = trade.find_all('td')

            if len(rows) >= 8:
                res['symbol'].append(format_row(0))
                res['trade_type'].append(format_row(1))
                res['time_opened'].append(handle_date(format_row(2)))
                res['timeframe'].append(format_row(3))
                res['entry_price'].append(handle_num(format_row(4)))
                res['time_closed'].append(handle_date(format_row(5)))
                res['exit_price'].append(handle_num(format_row(6)))
                res['profit'].append(handle_num(format_row(7)))
        except:
            traceback.print_exc()
            print(trade)

    if None in res['profit']:
        print('NONE')
    df = pd.DataFrame(res)
    df.to_csv('es_table_analysis/es_table.csv')
    print(df)


def main(scrapping_key):

    store_new_table(scrapping_key)  # comment if you dont want to do scrapping
    all_trades = format_tables()
    format_all_trades(all_trades)


if __name__ == '__main__':

    scrapping_key = open_json('config.json')['scrapping_key']

    store_new_table(scrapping_key)
    all_trades = format_tables()
    format_all_trades(all_trades)
