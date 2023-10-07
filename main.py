import requests
from bs4 import BeautifulSoup
import pickle


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
