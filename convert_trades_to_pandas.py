import pandas
import pandas as pd
import numpy as np


from help_functions import *


def main():
    trades = open_json(f'logs/processed_trades.json')

    columns = ['time', 'status', 'perc', 'type', 'entry_price', 'exit_price', 'entry_date', 'stop', 'move_stop_loss', 'id']
    df = pandas.DataFrame(columns=columns)

    skipped = 0

    for trade in trades:

        to_app = {
            'time':               trade['timestamp'],
            'symbol':             trade['symbol'],
            'status':             -1,   # 0 - exit, 1 - entry, 2 - ONLY MOVE STOP LOSS
            'perc':               0,
            'type':               trade['type'],
            'timeframe':          trade['timeframe'],
            'entry_price':        trade['entry_price'],
            'exit_price':         trade['exit_price'],
            'entry_date':         trade['date_opened_position'],
            'stop':               trade['stop'],
            'move_stop_loss':     0,
            'id':                 trade['alert_id']
        }

        allowed_perc = [25, 50, 75]

        if trade['status'] == 0:
            to_app['status'] = 0
            to_app['perc'] = 100
        elif trade['status'] == 1:
            to_app['status'] = 1
            to_app['perc'] = 100

            if trade['special']:
                if trade['special'][1] in allowed_perc and trade['special'][0] == 'Add':
                    to_app['perc'] = trade['special'][1]
        elif trade['status'] in [2, -69]:
            if trade['status'] == 2:
                to_app['move_stop_loss'] = 1
                to_app['status'] = 2
            if trade['special']:
                if trade['special'][1] in allowed_perc and trade['special'][0] == 'Add':
                    to_app['perc'] = trade['special'][1]
                    to_app['status'] = 1
                if trade['special'][1] in allowed_perc and trade['special'][0] == 'Reduce':
                    to_app['perc'] = trade['special'][1]
                    to_app['status'] = 0

            if to_app['status'] == -1:
                skipped += 1
                continue
        else:
            print('WHAT???')

        df = df.append(to_app, ignore_index=True)

    df.to_csv(f'all_trades_analysis/all_trades.csv')

    print(df)


if __name__ == '__main__':
    main()
