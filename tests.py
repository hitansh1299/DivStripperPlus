import pandas as pd
import numpy as np
import json
import requests
from bs4 import BeautifulSoup
from io import StringIO
from lxml.html.soupparser import fromstring
# with open('request.txt','r') as fhand:
#     data = fhand.read()
#     df = pd.read_json(data)
#     print(df)

# results = requests.post('https://www.moneycontrol.com/stocks/marketinfo/dividends_declared/index.php',
# params={
#     'sel_year': 2020,
#     'x':15,
#     'y':9
# })

# with open('res.txt', 'r') as res:
#     soup = BeautifulSoup(res.read(), features='lxml')
# # print(soup.prettify())
# table = soup.find('table', class_='b_12 dvdtbl')
# # print(table)
# df = pd.read_html(str(table),
#                 skiprows=[0],
#                 header=0)[0]
# print(df)


# with open('request.txt','r') as f:
#     data = f.read()
#     formatted_data = json.dumps(json.loads(data), indent=4)
#     print(formatted_data)
#     with open('JSON_data_dividend.txt', 'w') as f2:
#         f2.write(formatted_data)

data = requests.get(
    url='https://api.bseindia.com/BseIndiaAPI/api/StockPriceCSVDownload/w',
    params={
        'pageType': '0',
        'rbType': 'D',
        'Scode': '500325',
        'FDates':'01/01/2018',
        'TDates':'22/01/2023',
    },
    headers={
        'authority': 'api.bseindia.com',
            'method': 'GET',
            'scheme': 'https',
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'origin': 'https://www.bseindia.com',
            'referer': 'https://www.bseindia.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.55'
    },
    allow_redirects=True
)

with open('price_data.csv', 'wb') as d:
    d.write(data.content)


print(pd.read_csv('price_data.csv'))

# with open('price_data.txt', 'w') as price:
#     price.write(json.dumps(json.loads(data.text)))
