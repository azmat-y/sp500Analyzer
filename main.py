import requests
from bs4 import BeautifulSoup
import pickle
import os
import datetime as dt
import yfinance as yf

def grab_tickers(reload=False):
    # if reload is True then we will refresh the list of tickers
    if reload:
        resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        soup = BeautifulSoup(resp.text, 'lxml')
        table = soup.find('table', {'class':'wikitable sortable'})
        tickers = []
        for row in table.findAll('tr')[1:]:
            ticker = row.findAll('td')[0].text
            tickers.append(ticker.rstrip())
        with open('sp500tickers.pickle', 'wb') as f:
            pickle.dump(tickers, f)
        return tickers

    # if reload is False we will assume the file is already there
    with open('sp500tickers.pickle', 'rb') as f:
        tickers = pickle.load(f)
        # print(tickers)
        return tickers

def get_data_for_ticker(reload_data=False, reload_tickers=False):
    tickers = grab_tickers(reload=reload_tickers)

    if not os.path.exists('stocks_dfs'):
        os.makedirs('stocks_dfs')

    start = dt.datetime(2017, 1, 1)
    end = dt.datetime(2022, 12, 31)

    for ticker in tickers:
        ticker = ticker.rstrip()
        if reload_data:
           if not os.path.exists(f'stocks_dfs/{ticker}.csv'):
               df = yf.download(ticker, start, end)
               df.to_csv(f'stocks_dfs/{ticker}.csv')
           else:
               print(f'Already have {ticker}.csv')
        else:
            pass


# get_data_for_ticker(reload_data=True)
