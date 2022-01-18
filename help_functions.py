import re
import datetime
import traceback
import os

import pytz
import time
import json


def re_find(pt1, pt2, txt):
    return re.findall(pt1 + r'(.*?)' + pt2, txt)[0]


def convert_timestamp(tm, timezone=0, raw=0):
    """ Converts timestamp to datetime in SK """
    if not timezone:
        tim = 'Europe/Bratislava'
    elif timezone == 1:
        tim = 'US/Eastern'
    else:
        tim = timezone

    res = datetime.datetime.fromtimestamp(tm, tz=pytz.timezone(tim))
    if raw:
        return res
    return res.strftime('%Y-%m-%d %H:%M:%S.%f')


def get_time(raw=False, also_hours=True, get_milis=False, timezone=''):
    """
    gets current time

    :param raw: string or raw datetime format
    :param also_hours: show hours or only date
    :return:
    """

    p_n = datetime.datetime.utcnow()

    if timezone:

        utc_now = pytz.utc.localize(datetime.datetime.utcnow())
        p_n = utc_now.astimezone(pytz.timezone(timezone))

    if also_hours:
        date_format = '%Y-%m-%d %H:%M:%S'
        if get_milis:
            date_format += '.%f'
        date_now = p_n.strftime(date_format)
        p_n = datetime.datetime.strptime(date_now, date_format)
    else:
        date_now = p_n.strftime('%Y-%m-%d')
        p_n = datetime.datetime.strptime(date_now, '%Y-%m-%d')

    if raw:
        return p_n

    return date_now


def debug_msg(msg, debug=1, also_milis=False, return_=False):
    str_ = f'[{get_time(get_milis=also_milis)}] {msg}'
    if return_:
        return str_
    if debug:
        print(str_)


def error_msg(msg):
    str_ = f'[ERROR {get_time(get_milis=True)}] {msg} {traceback.format_exc()}'
    print(str_)


def store_dump(msg):
    # json_dump('alerts_logs.json', msg)
    print(msg)


def json_dump(path, content, indent=False):
    """ handling of writing into json file faster and more effectively """

    for _ in range(30):
        try:
            with open(f'{path}', 'w', encoding='utf-8') as f:
                if indent:
                    json.dump(content, f, indent=indent)
                else:
                    f.write(json.dumps(content))
            break
        except Exception:
            if _ == 29:
                traceback.print_exc()


def file_append(path, content):
    with open(f'{path}', 'a', encoding='utf-8') as f:
        f.write(f"{content}\n")


def file_write(path, content):
    with open(f'{path}', 'w', encoding='utf-8') as f:
        f.write(content)


def time_diff(tm1, tm2, r=2):
    return round(tm2 - tm1, r)


def open_json(path, default=None, create_new=False):
    """
    Handling of opening json files and exceptions

    :param path: path to file
    :param default: default value for when json cant be opened
    :param create_new: whether we want to create a new file in case open wasnt successful
    """

    if default is not None:
        res = default
    else:
        res = {}
    for _ in range(30):
        try:
            with open(f'{path}', 'r', encoding='utf-8') as f:
                res = json.load(f)
            break
        except FileNotFoundError:
            if create_new:
                with open(f'{path}', 'w', encoding='utf-8') as f:
                    json.dump(res, f)
            # else:
            #     print('open json FILENOTFOUND:', path)
            break
        except Exception:
            pass
        time.sleep(0.1)
    else:
        print('open json failed:', path)
    return res


def open_file(path, default=False):
    res = ''
    if default:
        res = default

    for _ in range(30):
        try:
            with open(f'{path}', 'r', encoding='utf-8') as f:
                res = f.read()
            break
        except FileNotFoundError:
            break
        except Exception:
            pass
        time.sleep(0.1)

    else:
        print('open file failed:', path)

    return res


def format_borders(msg):
    brd = "-"*60
    return f'\n{brd}\n{msg}\n{brd}\n'


def arr_avg(arr):
    if len(arr) == 0:
        return 0
    return round(sum(arr)/len(arr), 3)


def check_make_dir(path):
    """ Checks if folder already exists and if not, creates a new one """
    if not os.path.exists(f'{path}'):
        os.mkdir(f'{path}')
        time.sleep(0.05)
