# ticker_fetcher_app

This web app is just a rudimentary wrapper for a script I wrote for someone —I refused to write an Excel Macro, so I agreed on a web app (tells you a lot about VBA...).

The script downloads historical ticker stock values using the free service `AlphaVantage`, which has a limit to 1 every 30 seconds —I would strongly recommend using the paid service Quandl, which is infinitely better, but this is free.
This password protected app simply allows one to download past datasets, retrieve new one and list the tickers.

The site is not publicly accessible and requires a key.

API route:

    r = requests.get('https://finance.matteoferla.com/retrieve',
                      params={'key': '👾👾👾', 
                           'tickers': '\n'.join(tickers),
                           'name': f'sensible_name'})