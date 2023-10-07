import requests
import math
import pickle
import os
import datetime as dt
import yfinance as yf
import pandas as pd
from bs4 import BeautifulSoup

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

def get_adj_close():
    '''
    parse stocks data resulting in pd.DataFrame in form
    Date Adj-Close
    in a ticker.csv
    '''
    tickers = grab_tickers()
    if not os.path.exists('stocks_dfs_AdjClose'):
        os.makedirs('stocks_dfs_AdjClose')

    for ticker in tickers:
        if not os.path.exists(f'stocks_dfs_AdjClose/{ticker}.csv'): # edit
            df = pd.read_csv(f'stocks_dfs/{ticker}.csv')
            df.set_index('Date', inplace=True)
            df.drop(['Open', 'High', 'Low', 'Close', 'Volume'], axis=1, inplace=True)
            df.rename(columns = {'Adj Close':'price'}, inplace=True)
            df.to_csv(f'stocks_dfs_AdjClose/{ticker}.csv')
        else:
            # if files already exists then we have nothing to do
            pass

'''
format for final df
ticker price one-year-return shares to buy
'''
def final_df():
    if not os.path.exists('stocks_dfs_AdjClose'):
        print('Error, No files with Adj close prices')
        return
    tickers = grab_tickers()
    data = []  # List to store data for DataFrame
    for ticker in tickers:
        df = pd.read_csv(f'stocks_dfs_AdjClose/{ticker}.csv', parse_dates=True, index_col=0)
        df.index = pd.to_datetime(df.index)
        df = df.resample('Y').mean()

        try:
            yearly_return = df['price'].pct_change().iloc[-1]  # Calculate yearly return
            price = df['price'].iloc[-1]  # Get the price at the end of the year
            data.append({'Ticker': ticker, 'Price': price, 'Yearly_Return': yearly_return})
        except ValueError:
            pass

    final_df = pd.DataFrame(data)
    final_df.sort_values('Yearly_Return', ascending=False, inplace=True)
    final_df = final_df[:51]
    final_df.reset_index(drop=True, inplace=True)
    final_df['Shares_to_Buy'] = None

    return final_df

def portfolio_input(final_df):
    portfolio_size = input("Enter the value of your portfolio:")
    try:
        val = float(portfolio_size)
    except ValueError:
        print("That's not a number! \n Try again:")
        portfolio_size = input("Enter the value of your portfolio:")
    position_size = float(portfolio_size) / len(final_df.index)
    for i in range(0, len(final_df['Ticker'])):
        final_df.loc[i, 'Shares_to_Buy'] = math.floor(position_size / final_df['Price'][i])
    return final_df

# get_data_for_ticker(reload_data=True)

def main():
    reload = input('Do you want to reload tickers y/n').lower()
    flag = True if reload == 'y' else False
    get_data_for_ticker(reload_tickers=flag)
    get_adj_close()
    df = portfolio_input(final_df)
    print(df)
