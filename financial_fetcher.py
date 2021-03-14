#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__description__ = \
    """
Fetches the data for all the tickers in a list.
Do remember to add .L suffix for LSE, .MI for LSE-MIB.
FTSE indices don't seem to work.
NB. Written for python 3, not tested under 2.
"""
__author__ = "Matteo Ferla. [Github](https://github.com/matteoferla)"
__email__ = "matteo.ferla@gmail.com"
__date__ = "Christmas day 2018"
__license__ = "Cite me!"
__version__ = "1.0"

import argparse
from datetime import date, datetime

import json, csv, os, re, collections, math, time, logging
import requests
import numpy as np
from collections import defaultdict
from datetime import date, timedelta, datetime

from typing import Union, Dict #TypedDict

'''
ShareDict = TypedDict('ShareDict', {'Meta Data': Dict, 'Weekly Adjusted Time Series': Dict})
ShareDict.__doc__ = """{'Meta Data': {'1. Information': 'Weekly Adjusted Prices and Volumes',
                   '2. Symbol': 'SPWR',
                   '3. Last Refreshed': '2019-04-18',
                   '4. Time Zone': 'US/Eastern'},
     'Weekly Adjusted Time Series': {'2019-04-18': {'1. open': '7.6300',
                                                    '2. high': '7.6400',
                                                    '3. low': '7.3500',
                                                    '4. close': '7.4300',
                                                    '5. adjusted close': '7.4300',
                                                    '6. volume': '4044034',
                                                    '7. dividend amount': '0.0000'},
                                    ...}
                            }
    }"""'''

class Finance():
    logger = logging.getLogger(__name__)

    def __init__(self, time: str, max_points: bool=None):
        """
        Set the settings.

        :param time: 'week adj'
        :type time: str
        :param max_points: massimo numero di punti
        :type max_points: Union[str, None]
        """
        if time == 'day':
            self.time = 'day'
            self.timequery = 'TIME_SERIES_DAILY&outputsize=full'
            self.timecolumn = 'Time Series (Daily)'
        elif time == 'week':
            self.time = 'week'
            self.timequery = 'TIME_SERIES_WEEKLY'
            self.timecolumn = 'Weekly Time Series'
        elif time == 'week adj':
            self.time = 'week'
            self.timequery = 'TIME_SERIES_WEEKLY_ADJUSTED'
            self.timecolumn = 'Weekly Time Series'
        else:
            raise NotImplementedError
        self.logger.warning('time query hardcoded to ``Weekly Adjusted Time Series``')
        self.max_points = max_points  # None or int
        self.shareball = {}
        self.errorball = []
        self.sideslice = None

    def ticker_fetcher(self, symbol:str, write_flag=True): # -> ShareDict:
        """
        Fetches the data for the ``symbol`` from ``alphavantage.co``.

        :param symbol: ticker
        :type symbol: str
        :param write_flag: Write to ``symbol + '_data.csv'``
        :type write_flag: bool
        :return: data
        :rtype: ShareDict
        """
        url = 'https://www.alphavantage.co/query'
        data = requests.get(url, params=dict(symbol=symbol,
                                             function=self.timequery,
                                             datatype='json',
                                             apikey=os.environ['ALPHA_KEY'])
                            ).json()
        self.logger.debug(data)
        if 'Information' in data:
            time.sleep(10)
            self.logger.info('Maxed out on time...')
            return self.ticker_fetcher(symbol, write_flag)
        if write_flag:
            w = csv.writer(open(symbol + '_data.csv', 'w'))
            # header
            w.writerow(data['Meta Data'].keys())
            w.writerow(data['Meta Data'].values())
            w.writerow('')
            # Time
            w.writerow(['Date', 'Open', 'High', 'Low', 'Close', 'Volumes'])
            for row in data[self.timecolumn]:
                w.writerow([row, *data[self.timecolumn][row].values()])
        return data

    def get_tickers(self, tickers):
        """
        Get all the data for the tickers.

        :param tickers: tickers to fetch
        :type tickers: List[str]
        :return: self
        """
        shareball = self.shareball #likely empty dict
        errorball = self.errorball #likely empty dict
        for symbol in tickers:
            try:
                data = self.ticker_fetcher(symbol, write_flag=False)
                time.sleep(15)
                shareball[symbol] = data
                self.logger.info('{} done'.format(symbol))
            except Exception as err: #
                self.logger.warning(symbol + str(err))
                errorball.append(symbol)
        self.shareball = shareball
        self.errorball = errorball
        self.fix_errors()
        return self

    def fix_errors(self):
        assert self.shareball, 'No share data. Have you fetched them?'
        newshareball = {}
        for symbol in self.shareball:
            if 'Weekly Adjusted Time Series' not in self.shareball[symbol]:
                self.logger.warning(f'{symbol} failed. '+\
                               f'Keys in `self.shareball["{symbol}"]`: {self.shareball[symbol].keys()}')
                continue
            try:

                self.shareball[symbol]['Weekly Adjusted Time Series'].keys()
                newshareball[symbol] = self.shareball[symbol]
            except Exception:
                if 'Error Message' in self.shareball[symbol]:
                    self.logger.warning(f'{symbol} removed due to error')
                else:
                    self.logger.warning(f'UNKNOWN ERROR with {symbol}')
        self.shareball = newshareball

    def side_slicer(self):
        """
        Restructures the shareball into the sideslice attribute.
        key = time, values = Dict[ticker: value]

        :return: self
        """
        # transpose data...
        sideslice = defaultdict(dict)
        for symbol in self.shareball:
            for when in self.shareball[symbol]['Weekly Adjusted Time Series']:
                sideslice[when][symbol] = list(self.shareball[symbol]['Weekly Adjusted Time Series'][when].values())
        self.sideslice = sideslice

    def deshifted_side_slicer(self):
        """
        Restructures the shareball into the sideslice attribute. But fixed the offset issue.
        key = time, values = Dict[ticker: value]

        :return: self
        """
        # transpose data...
        weekof=datetime.now().date()
        weekly=[]
        earliest = datetime.strptime(min([k for symbol in self.shareball for k in self.shareball[symbol]['Weekly Adjusted Time Series']]), "%Y-%m-%d").date()
        corrected = {}
        for symbol in self.shareball:
            weekof = datetime.now().date()
            sd = self.shareball[symbol]['Weekly Adjusted Time Series']
            while weekof > earliest:
                for day in range(7):
                    thisday = (weekof - timedelta(days=day)).isoformat()
                    if thisday in sd and sd[thisday] and sd[thisday] != '-':
                        w = weekof.isoformat()
                        if w not in corrected:
                            corrected[w] = {}
                        corrected[w][symbol] = sd[thisday]
                        self.debug(f'Matched {thisday}')
                weekof -= timedelta(days=7)
        self.sideslice = corrected

    def write_intercalate(self, outfile):
        assert self.shareball, 'No share data. Have you fetched them?'
        if not self.sideslice:
            #self.side_slicer()
            self.deshifted_side_slicer()
        # output!
        # start file...
        outfile = open(outfile, 'w')
        out = csv.writer(outfile)
        out.writerow(['WEEKLY'] + [symbol for symbol in self.shareball for i in range(7)])
        demosymbol = list(self.shareball.keys())[0]
        demodate = list(self.shareball[demosymbol]['Weekly Adjusted Time Series'].keys())[0]
        out.writerow(['Date'] + list(self.shareball[demosymbol]['Weekly Adjusted Time Series'][demodate].keys()) * len(self.shareball))
        # main...
        for when in sorted(self.sideslice.keys(), reverse=True):
            row = [when]
            for symbol in self.shareball:
                if symbol in self.sideslice[when]:
                    row.extend(self.sideslice[when][symbol])
                else:
                    row.extend(['-'] * 7)
            out.writerow(row)
        outfile.close()
        return self


    def write_values(self, outfile):
        if not self.sideslice:
            #self.side_slicer()
            self.deshifted_side_slicer()
        outfile = open(outfile, 'w')
        out = csv.writer(outfile)
        out.writerow(['WEEKLY'] + [symbol for symbol in self.shareball])
        # main
        for when in sorted(self.sideslice.keys(), reverse=True):
            row = [when]
            for symbol in self.shareball:
                if symbol in self.sideslice[when]:
                    row.append(float(self.sideslice[when][symbol]['4. close']))  # *volume[symbol]
                else:
                    row.append('-')
            out.writerow(row)
        outfile.close()
        return self

#########################
# Input
#########################

def main(infile, grouping):
    today = str(date.today()).replace('-', '')
    tickers = open(infile).read().split()
    print('parsing', grouping, len(tickers))
    API = Finance('week adj')
    API.get_tickers(tickers)
    API.write_intercalate(grouping + '_' + today + '.csv')
    API.write_values(grouping + '_values_' + today + '.csv')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument("input", help="the input file")
    parser.add_argument("grouping", help="the output file. formerly called the 'group' name.")
    parser.add_argument('--version', action='version', version=__version__)
    args = parser.parse_args()
    main(args.input, args.grouping)