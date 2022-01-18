import requests
import time
import json
import re
import traceback
import sys


from help_functions import *


class AlertFormatter:
    """
    Formats scrapped alerts for future analysis
    """

    wrong_entries = {
        '2757274': {'Trade Type': 'short'},
        '2756652': {'Trade Type': 'short'},
        '2756944': {'Trade Type': 'short'},
        '6490043': {'Entry Price': 3459.0, 'Exit Price': 3475.0},
        '5736747': {'Entry Price': 3328.0, 'Stop': 3322},
        '5730195': {'Entry Price': 3290.0},
        '5717514': {'Entry Price': 3282.0},
        '5695585': {'Entry Price': 3277.0},
        '5099529': {'Trade Type': 'short'},
        '4023453': {'Entry Price': 2437.0},
        '5166739': {'Entry Price': 2755.0},
        '5393196': {'Entry Price': 2990.0},
        '4826304': {'Exit Price': 2851.13},
        '7269573': {'Exit Price': 4329.5},
        '7480229': {'delete': 1},
        '4024064': {'delete': 1}
    }

    def __init__(self, test=0):
        self.debug = 0
        self.test = test

    def format_html(self, msg):
        temp_res = {}
        msg['entry'] = msg['entry'].replace('"', "'")
        for row in msg['entry'].split("<div class='tr-leftTrade'>"):
            if "class='tr-rightTrade'>" in row:
                key = row.split(r'</div>')[0]
                val = row.split("class='tr-rightTrade'>")[1].split(r'</div>')[0]
                temp_res[key] = val
        return temp_res

    def replace_comma(self, a):
        """ Replace 1,444 to 1444; but not 1,44 """

        res = []

        c = re.findall(r'\d+,\d+', a)
        for q in c:
            res.append(a.split(q)[0])
            res.append(q)
            a = a.replace(f'{a.split(q)[0]}{q}', '')
        res.append(a)

        res_str = ''
        for i in range(len(res)):
            if i % 2 == 1:
                pt1, pt2 = res[i].split(',')
                if len(pt1) in [1, 2, 3] and len(pt2) == 3:
                    res[i] = res[i].replace(',', '')

            res_str += res[i]

        return res_str

    def fix_wrong_entries(self, alert_id, key):

        if alert_id in self.wrong_entries and key in self.wrong_entries[alert_id]:
            return self.wrong_entries[alert_id][key]

    def html_find(self, alert_id, html_format, key, necessary=0, is_number=0, additional_options=None):

        fixed_entry = self.fix_wrong_entries(alert_id, key)
        if fixed_entry:
            return fixed_entry

        if key not in html_format:
            if key + ':' in html_format:
                key = key + ':'
            if additional_options:
                for opt in additional_options:
                    if opt in html_format:
                        key = opt
                        break
                    elif opt + ':' in html_format:
                        key = opt + ':'
                        break

        if not necessary and key not in html_format:
            return ''
        if is_number:
            html_format[key] = re.sub(r'</?(.*?)>', '', html_format[key])
            temp = self.replace_comma(html_format[key])
            temp = re.sub(r'[ s]', '', temp)

            if necessary:
                temp = temp.replace(',', '')
                if '/' in temp:
                    temp = temp.split('/')[0]
                return float(temp)
            else:
                for sign in ['/', ',', '-']:
                    if sign in temp:  # 4300, 4320,4340
                        res = []
                        for i in temp.split(sign):
                            try:
                                res.append(float(i))
                            except ValueError:
                                pass

                        return res
                try:
                    return float(temp)
                except ValueError:
                    return temp

        return html_format[key]

    def handle_special_message(self, msg, temp_res):

        def are_words_in(words_arr):
            yes = 0
            for words in words_arr:
                for word in words:
                    if word not in txt:
                        break
                else:
                    yes = 1
                    break
            return yes

        def is_banned():
            for ban in banned_words:
                if ban in tx:
                    return True

        def is_partially_banned():
            for ban in partially_banned:
                if ban in tx:
                    return True

        # txt_of_interest = re_find('<p>', '</p>', msg['entry']).lower()
        txt_of_interest = msg['entry'].split('</div>')[-1].split('<p>')
        res = []
        for tt in txt_of_interest:
            if '<li>' in tt:
                res.extend(tt.split('<li>'))
            else:
                res.append(tt)
        banned_words = ['NQ', 'RTY', 'PL', 'GC', 'ZW', 'CL', 'ZS', 'SPY', 'NFLX', 'MSFT', 'TSLA', 'Z', 'AAPL',
                        'ooking to', 'OCO', 'ne cancels other']
        partially_banned = []

        # if '2021-07-08 11:22:30' in msg['postDate']:
        #     print(res)

        for tx in res:

            txt = tx.lower()

            reduce_trade_words = [['scale'], ['reduce'], ['cover', 'half'], ['cover', '%'], ['take', ' off'], ['bank', 'half'], ['bank', '%'], ['taking', 'off'], ['filled'], ['trim', ' off'], ['took', ' off'], ['out', 'half'], ['out', '%'], ['take profit'], ['took', 'profit'], ['trim'], ['scalp', 'out']]
            add_words = [['entry made in the '], ['reload'], ['scale in'], ['accumulat'], ['add'], ['scaling'], ['hop back'], ['in other half']]

            is_reduce = are_words_in(reduce_trade_words)
            is_add = are_words_in(add_words)

            if (is_reduce or is_add) and (not is_banned() or 'ES' in tx):
                perc = ''

                if re.findall(r'\d+%', txt):
                    perc = float(re.findall(r'\d+%', txt)[0][:-1])
                elif 'half' in txt and not 'hold half' in txt:
                    perc = 50
                elif 'rest' in txt:
                    perc = 'rest'

                price_at = ''
                if re.findall(r'at \d\d\d\d', txt):
                    price_at = re.findall(r'(at \d+\.\d+)|(at \d+)', txt)[0]
                elif re.findall(r'\d\d\d\d', txt):
                    price_at = re.findall(r'(\d\d\d\d\.\d+)|(\d\d\d\d)', txt)[0]
                elif re.findall(r'for [+-](\d+)|(\d+\.\d+) p', txt):
                    price_at = re.findall(r'for [+-](\d+)|(\d+\.\d+) p', txt)[0]
                if price_at:
                    price_at = price_at[0] if price_at[0] else price_at[1]
                    price_at = float(price_at.replace('at ', ''))
                    if price_at > 9999:
                        price_at = ''

                # if '2021-07-08 11:22:30' in msg['postDate']:
                #     print('is_reduce:', is_reduce)
                #     print('is_add:', is_add)
                #     print('price_at:', price_at)
                #     print('perc:', perc)

                if not perc and not price_at:
                    debug_msg(f'INCOMPLETE REDUCE STATUS msg: {msg}', self.debug)
                else:

                    if temp_res['status'] not in [0, 1] and not price_at:
                        debug_msg(f'INCOMPLETE REDUCE STATUS msg: {msg}', self.debug)
                    else:
                        # if '2021-07-08 11:22:30' in msg['postDate']:
                        #     print('RETURNING')
                        return ['Add' if is_add else 'Reduce', perc, price_at]

    def get_formatted_alerts(self, resp):

        res = []

        for msg in resp:
            try:
                if 'tr-stocktradeBlock' in msg['entry'] and msg['userId'] == 11114:
                    debug_msg(msg, self.debug)
                    html_format = self.format_html(msg)
                    debug_msg(html_format, self.debug)

                    # format opened position date
                    opened_position = self.html_find(msg['id'], html_format, 'Time/Date')
                    if not opened_position:
                        opened_position = self.html_find(msg['id'], html_format, 'Entry Date')

                    date_opened_position = datetime.datetime.strptime(opened_position, '%d-%b-%y').strftime('%d-%b-%y')

                    if int(msg['sectionId']) == 248:
                        timeframe = 'scalp'
                    elif int(msg['sectionId']) == 250:
                        timeframe = 'swing'
                    else:
                        print('NO TIMEFRAME')
                        raise NotImplementedError

                    temp_res = {
                        'alert_id':              msg['id'],
                        'symbol':                self.html_find(msg['id'], html_format, 'Symbol', 1),  # ES
                        'type':                  self.html_find(msg['id'], html_format, 'Trade Type', 1).lower(),  # Short / Long
                        'timestamp':             msg['updated_at'],
                        'eastern_date':          msg['postDate'],
                        'timeframe':             timeframe,  # Scalp / Swing
                        'entry_price':           self.html_find(msg['id'], html_format, 'Entry Price', 1, 1, additional_options=['Enter Price']),
                        'target':                self.html_find(msg['id'], html_format, 'Target', 0, 1),
                        'special':               '',
                        'stop':                  self.html_find(msg['id'], html_format, 'Stop', 0, 1),
                        'exit_price':            self.html_find(msg['id'], html_format, 'Exit Price', 0, 1),
                        'date_opened_position':  date_opened_position
                    }

                    # 0 = EXIT, 1 = OPEN, 2 = CHANGE STOP, 3 = CHANGE TARGET

                    if re.search('([Ee]xit made in the)|(This is an ES exit)', msg['entry']) and 'exit_price' in temp_res:
                        temp_res['status'] = 0
                    elif re.search('([eE]?ntry made in the)|(This is an ES entry)', msg['entry']) and 'target' in temp_res and 'stop' in temp_res:
                        temp_res['status'] = 1
                    elif re.search(r'[Ss]top(.*?) updated (in|from) ', msg['entry']) and 'stop' in temp_res:
                        temp_res['status'] = 2
                    else:
                        # print('\n\n\n---------\n\n\n')
                        # print(msg['postDate'], msg['entry'])
                        temp_res['status'] = -69

                    special_message = self.handle_special_message(msg, temp_res)

                    # if '2021-07-08 11:22:30' in msg['postDate']:
                    #     print('special message:', special_message)
                    if special_message:
                        temp_res['special'] = special_message
                        debug_msg(f"SPECIAL STATUS EXISTS BUT RATHER CHECK {msg}", self.debug)

                    # if '2021-07-08 11:22:30' in msg['postDate']:
                    #
                    #     print('temp res:', temp_res['special'])

                    # if temp_res['status'] == -69 and not temp_res['special']:
                    #     # if '2021-07-08 11:22:30' in msg['postDate']:
                    #     #     print('HUUUUUH????')
                    #     print('\n\n\n---------\n\n\n')
                    #     print(msg['postDate'], msg['entry'])
                    # else:
                    #     debug_msg(f"I DON'T KNOW IF IT'S ENTRY OR EXIT, PLEASE CHECK {msg}")
                    #     continue
                    if msg['id'] in self.wrong_entries and 'delete' in self.wrong_entries[msg['id']] and self.wrong_entries[msg['id']]['delete']:
                        print('deleted:', msg['id'])
                        continue

                    res.append(temp_res)

                    debug_msg(msg['entry'], self.debug)
                    debug_msg(temp_res, self.debug)
                    debug_msg('', self.debug)
            except:
                traceback.print_exc()
                print('entry:', msg['entry'])
                print('msg:', msg)

                # print('resp:', resp)
        return res


def main():

    scr = AlertFormatter()
    resp_raw = open_json(f'logs/raw_trades.json')
    resp = scr.get_formatted_alerts(resp_raw)
    json_dump(f'logs/processed_trades.json', resp, indent=4)


if __name__ == '__main__':
    main()
