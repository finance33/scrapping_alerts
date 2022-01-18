import os


import scrapping_es_table
import scrapping_all_trades
import format_all_trades
import convert_trades_to_pandas
import pandas_merged_table
from help_functions import *


def create_dirs():
    check_make_dir('all_trades_analysis')
    check_make_dir('es_table_analysis')
    check_make_dir('merged_trades_analysis')


if __name__ == '__main__':
    """
    Check if we have all directories necessary, create new if we don't. The program scraps necessary
    data from the website, stores them into json files, and outputs csv - pandas friendly files for
    data analysis. Automatically detects your previous json outputs, and doesn't rewrite them.
    
    We have 3 different analysis:
    1. ES table analysis - analyses data from trade table present on website - simplest one
       * start by running es_trade_table function
       * Scraps data from the website, generates pandas csv file to directory es_table_analysis 
         ready for jupyter notebook
        * just a general overview, not many details
    2. All trades analysis - analyses data from all posts present, all entries, exits, moves of
       stop loss
       * start by running generate_all_trades_analysis
       * has too much information, more useful for backtesting against historical data
    3. Merged trades analysis - analyses all posts, finds all exits, entries and merges them together,
       * useful for time analysis, like weekly performance
       * start by running generate_merged_trades_analysis
    """

    scrapping_key = open_json('config.json')['scrapping_key']

    long_scrapping = 1  # scrapping of all entries from 2016-now, takes a few minutes
    options = [1, 2, 3]

    create_dirs()

    if 2 in options or 3 in options:
        if long_scrapping:
            debug_msg('Starting scrapping of all trades from 2016')
            scrapping_all_trades.store_all_trades()
        debug_msg('Formatting scrapped alerts')
        format_all_trades.main()

    if 1 in options:
        debug_msg('Scrapping and formatting ES trading table')
        scrapping_es_table.main(scrapping_key)
    if 2 in options:
        debug_msg('Generating CSV log - all alerts')
        convert_trades_to_pandas.main()
    if 3 in options:
        debug_msg('Generating CSV log - merged trades')
        pandas_merged_table.main()
