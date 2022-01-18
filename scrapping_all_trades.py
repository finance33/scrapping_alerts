import requests
import time
from calendar import monthrange
from help_functions import *

import requests


def get_dates(y_start, end=0):
    res = []
    now = datetime.datetime.now()

    r_l = now.year + 1
    if end:
        r_l = end

    years = range(y_start, r_l)
    months = range(1, 13)
    end = 0

    for y in years:
        for m in months:
            d = monthrange(y, m)[1]

            if datetime.datetime(y, m, d) > datetime.datetime.now():
                d = now.day
                end = 1

            m, d = str(m), str(d)
            if len(m) == 1: m = f'0{m}'
            if len(d) == 1: d = f'0{d}'

            res.append([f'{y}-{m}-01', f'{y}-{m}-{d}'])

            if end:
                return res

    return res


def do_req(i, dt, app):

    scrapping_key = open_json('config.json')['scrapping_key']

    cookies = {
        'fbUser': scrapping_key
    }

    headers = {
        'Host': 'www.elliottwavetrader.net',
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Chromium";v="97", " Not;A Brand";v="99"',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
        'sec-ch-ua-platform': '"Windows"',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://www.elliottwavetrader.net/trading-room/keyword//user/11114/post-type/initial/start-date/2021-12-01/end-date/2021-12-31/section/248/chart-duration//chart-category//advanced/match-any',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    params = (
        ('u[]', '11114'),
        ('matchtype', '2'),
        ('posttype', '2'),
        ('startdate', dt[0]),
        ('enddate', dt[1]),
        ('chartonly', 'false'),
        ('st', 'a'),
        ('favorites', 'false'),
        ('dayslimit', 'null'),
        ('threadId', '0'),
        ('roomId', '0'),
        ('independentusers', '0'),
        ('relationId', '0'),
        ('sections[]', '248' if app == 'scalp' else '250'),
        ('start', str(i * 20)),
        ('row_limit', '0'),
        ('s', str(time.time()).replace('.', '')[:13]),
    )

    response = requests.get('https://www.elliottwavetrader.net/api/v1/room', headers=headers, params=params, cookies=cookies).json()
    return response


def store_all_trades():
    dates = get_dates(2016)

    raw = open_json(f'logs/raw_trades.json')
    raw_dic = {str(i['id']): i for i in raw}

    for app in 'scalp', 'swing':
        debug_msg(f'SCRAPPING {app.upper()}S\n')

        for dt in reversed(dates):
            i = 0
            while True:
                debug_msg(f'scrapping of date: {dt}, num: {i}, timeframe: {app}')

                response = do_req(i, dt, app)

                if not response:
                    break

                for rsp in response:
                    if rsp['id'] not in raw_dic:
                        raw_dic[rsp['id']] = rsp
                        # print('NEW UPDATE:', rsp)

                time.sleep(0.5)
                i += 1

    json_dump(f'logs/raw_trades.json', [raw_dic[k] for k in raw_dic], indent=2)


if __name__ == '__main__':
    store_all_trades()
