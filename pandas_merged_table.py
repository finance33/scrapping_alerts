import datetime

import pandas
import pandas as pd
import numpy as np


from help_functions import *


def main():

    trades = open_json(f'logs/processed_trades.json')

    df = pandas.DataFrame()

    """ Sort by date, search through, pick up closest position open that has the same date as entry_date """
    trades.sort(key=lambda x: x['timestamp'])
    for i, close_trade in enumerate(trades):
        close_trade_entry = datetime.datetime.strptime(close_trade['date_opened_position'], '%d-%b-%y')
        if close_trade['status'] == 0:

            # if entry date couldn't be found, set time to 10 am

            to_app = {
                'time_exit':      close_trade['eastern_date'],
                'perc_entry':     0,
                'type':           close_trade['type'],
                'timeframe':      close_trade['timeframe'],
                'time_entry':     f"{close_trade_entry.year}-{close_trade_entry.month}-{close_trade_entry.day} 9:59:59",
                #'time_entry':     np.nan,
                'entry_price':    close_trade['entry_price'],
                'symbol_exit':    close_trade['symbol'],
                'exit_price':     close_trade['exit_price'],
                'entry_date':     close_trade['date_opened_position'],
                'stop':           np.nan,
                'id_exit':        close_trade['alert_id']
            }

            ignore_entry_price = 0
            already_added = 0

            for q in range(2):

                for j in range(i-1, -1, -1):
                    open_trade = trades[j]
                    if open_trade['status'] == 1:
                        dt_open = convert_timestamp(open_trade['timestamp'], 1, raw=1)

                        if [dt_open.year, dt_open.month, dt_open.day] == [close_trade_entry.year, close_trade_entry.month, close_trade_entry.day]:
                            if open_trade['type'] == close_trade['type'] and open_trade['timeframe'] == close_trade['timeframe']:
                                if open_trade['entry_price'] == close_trade['entry_price'] or ignore_entry_price:
                                    # found entry date of position

                                    to_app.update({
                                        'time_entry':          open_trade['eastern_date'],
                                        'symbol_entry':        open_trade['symbol'],
                                        'perc_entry':          0,
                                        'stop':                open_trade['stop'],
                                        'id_entry':            open_trade['alert_id'],
                                    })

                                    allowed_perc = [25, 50, 75]

                                    if open_trade['status'] == 1:
                                        to_app['perc_entry'] = 100

                                        if open_trade['special']:
                                            if open_trade['special'][1] in allowed_perc and open_trade['special'][0] == 'Add':
                                                to_app['perc_entry'] = open_trade['special'][1]

                                    df = df.append(to_app, ignore_index=True)
                                    already_added = 1
                                    break
                else:
                    if not ignore_entry_price:
                        ignore_entry_price = 1
                        print('ignored entry price:', close_trade)
                        continue
                    df = df.append(to_app, ignore_index=True)
                    print('match not found', close_trade)
                    break
                if already_added:
                    break
    print(df)

    # this exit wasnt in alerts
    to_app = {
        'time_exit': "2021-02-02 13:50",
        'perc_entry': 0,
        'type': 'short',
        'timeframe': 'scalp',
        # 'time_entry':     f"{close_trade_entry.year}-{close_trade_entry.month}-{close_trade_entry.day} 9:59:59",
        'time_entry': "2021-02-02 12:21:20",
        'entry_price': 3832.5,
        'symbol_exit': 'ES',
        'exit_price': 3831.5,
        'entry_date': '02-Feb-21',
        'stop': np.nan,
        'id_exit': '-1'
    }
    df = df.append(to_app, ignore_index=True)

    df.to_csv(f'merged_trades_analysis/merged_trades.csv')
    # df['time_entry'] = pd.to_datetime(df['time_entry'], unit='s')
    # df['time_entry'] = df['time_entry'].dt.tz_localize('utc')
    # df['time_entry'] = df['time_entry'].dt.tz_convert('US/Eastern')



if __name__ == '__main__':
    main()
