import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import re
import os
from enchant.utils import levenshtein
from fastDamerauLevenshtein import damerauLevenshtein
from flask import Flask, render_template

TO_DATE = "20230101"
FROM_DATE = "20180101"
def get_dividend_data(scrip_code="", from_date="", to_date=TO_DATE, dummy=False) -> str:
    '''
    Format of from_date and to_date
    1st Feb 2020 -> 20200201
    '''

    if dummy:
        with open('JSON_data_dividend.txt') as res:
            data = res.read()
        return data

    data = requests.get('https://api.bseindia.com/BseIndiaAPI/api/DefaultData/w',
                        params={
                            'Fdate': from_date,
                            'Purposecode': 'P9',
                            'TDate': to_date,
                            'ddlcategorys': 'E',
                            'ddlindustrys': '',
                            'scripcode': str(scrip_code),
                            'segment': 0,
                            'strSearch': 'S',
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
                        }
                        )
    print(data.text)
    return data.text


def is_same_company():
    pass


def get_announcements_for_year(scrips: list, year: int) -> pd.DataFrame:
    res = requests.post('https://www.moneycontrol.com/stocks/marketinfo/dividends_declared/index.php',
                        params={
                            'sel_year': year,
                            'x': 15,
                            'y': 9
                        })

    soup = BeautifulSoup(res.text, features='lxml')

    table = soup.find('table', class_='b_12 dvdtbl')
    df = pd.read_html(str(table),
                      skiprows=[0],
                      header=0)[0]
    df = df.drop(['%', 'Type', 'Record'], axis=1)
    if not scrips is None:
        df = df[df['COMPANY NAME'].isin(scrips)]
    # print(df)
    return df


def get_dividend_df(scrip_code, from_date="", to_date=TO_DATE, dummy=False):
    data = get_dividend_data(scrip_code=scrip_code,
                             from_date=from_date, to_date=to_date)
    df = pd.read_json(data)
    df = df[['short_name', 'scrip_code', 'exdate', 'Purpose']]
    df['dividend'] = df['Purpose'].apply(
        lambda x: float(x[re.search(r'\d', x).start():]))
    df = df.drop(columns=['Purpose'])
    return df



def get_announcements(scrips: list, from_year: int = 2018, to_year: int = 2023) -> pd.DataFrame:
    df = pd.read_csv('Previous_Announcements.csv')
    df = df[df['COMPANY NAME'].isin(scrips)]
    df = df[(df['Announcement'].apply(lambda x: datetime.strptime(x, r'%d-%m-%Y')) >= datetime(from_year, 1, 1)) &
            (df['Announcement'].apply(lambda x: datetime.strptime(x, r'%d-%m-%Y')) <= datetime(to_year, 1, 1))]

    if to_year >= 2023:
        df = pd.concat(
            [df, get_announcements_for_year(scrips=scrips, year=to_year)])
    df['Announcement'] = df['Announcement'].apply(
        lambda x: datetime.strftime(datetime.strptime(str(x), r'%d-%m-%Y'), r'%Y%m%d'))
    df['Ex-Dividend'] = df['Ex-Dividend'].apply(lambda x: datetime.strftime(
        datetime.strptime(str(x), r'%d-%m-%Y'), r'%Y%m%d'))
    df.rename(columns={'Ex-Dividend': 'exdate'}, inplace=True)
    return df


def get_prices(scrip_code) -> pd.DataFrame:
    print('GETTING PRICES')
    try:
        with open(f'{scrip_code}.csv', 'r'):
            print('FILE FOUND AND OPENED')
            data = pd.read_csv(f'{scrip_code}.csv')
    except FileNotFoundError:
        print('File not found')
        data = requests.get(
            url='https://api.bseindia.com/BseIndiaAPI/api/StockPriceCSVDownload/w',
            params={
                'pageType': '0',
                'rbType': 'D',
                'Scode': scrip_code,
                'FDates': '01/01/2018',
                'TDates': '22/01/2023',
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
        with open(f'{scrip_code}.csv', 'wb') as d:
            d.write(data.content)
    finally:
        print('FINALLY RESOLVING')
        data = pd.read_csv(f'{scrip_code}.csv')
        print('PRINTING DATA')
        # print(data)
        data['Date'] = data['Date'].apply(lambda x: datetime.strftime(
            datetime.strptime(str(x), r'%d-%B-%Y'), r'%Y%m%d'))
        data = data[['Date', 'Close Price']]
        print(data)
        return data


def get_days_from_ref(date: str):
    date = datetime.strptime(str(date), r'%Y%m%d')
    days = (date - datetime(2018, 1, 1)).days
    return days


def get_prices_between(scrip_code, start_date, end_date, dummy=False):
    price_data = get_prices(scrip_code=scrip_code)
    res = price_data[(price_data.Date >= start_date)
                     & (price_data.Date <= end_date)]
    print(res)
    return res


def prepare_dataframe(scrip_code="", scrip_name=''):
    dividend_data = get_dividend_df(
        scrip_code=scrip_code, from_date=FROM_DATE, to_date=TO_DATE)
    announcements = get_announcements([scrip_name])
    dividend_data = dividend_data.sort_values(by=['exdate'])
    announcements = announcements.sort_values(by=['exdate','Announcement'])
    # print(dividend_data)
    # print(announcements)
    announcements = announcements.drop_duplicates(subset=['exdate'])
    try:
        announcements = announcements['Announcement']
        dividend_data['announcement'] = [str(min(announcements, key=lambda x: abs(int(x) - data) if (int(x) - data < 0) else (10000000))) for data in map(int, dividend_data['exdate'])]
    except Exception as e:
        raise e
        # print(announcements)
        # print(dividend_data)
    return dividend_data


def prepare_chart(scrip_code, start_date: datetime, end_date: datetime, exdate: datetime, announcement: datetime, dividend_amount, __new_stock=False, company_name="", figure_name=''):
    price_data = get_prices_between(scrip_code=scrip_code,
                                    start_date=datetime.strftime(start_date,r'%Y%m%d'),
                                    end_date=datetime.strftime(end_date,r'%Y%m%d' ))
    f = plt.figure(1, figsize=(10,6), dpi=720)
    f.suptitle(company_name + str(start_date.year) + ' | ' + 'Dividend: ₹'+str(dividend_amount) + ' | ' +'Price@Announcement: ₹'+ str(price_data[price_data.Date == datetime.strftime(announcement, r'%Y%m%d')]['Close Price'].values[0]) + ' | Price@ExDate: ₹'+str(price_data[price_data.Date == datetime.strftime(exdate, r'%Y%m%d')]['Close Price'].values[0]))

    # exdate = datetime.strptime(str(exdate), r'%Y%m%d')
    # announcement = datetime.strptime(str(announcement), r'%Y%m%d')
    # end_date = datetime.strptime(str(end_date), r'%Y%m%d')
    # start_date = datetime.strptime(str(start_date), r'%Y%m%d')
    # f.autofmt_xdate([start_date, end_date, exdate, announcement], [datetime.strftime(start_date, r'%d %b, %Y'), datetime.strftime(end_date, r'%d %b, %Y'), datetime.strftime(
    #     exdate, r'%d %b, %Y') + f'\nEx-Date\nDividend: {dividend_amount}', datetime.strftime(announcement, r'%d %b, %Y') + '\nAnnouncement Date'])
    f.autofmt_xdate()
    plt.plot(price_data['Date'].apply(lambda x: datetime.strptime(str(x), r'%Y%m%d')), price_data['Close Price'])
    # f.plot(exdate, price_data[price_data.Date == datetime.strftime(exdate, r'%Y%m%d')]['Close Price'], color='xkcd:mint', marker='o', label=f"Dividend amount: {dividend_amount}")
    plt.axvline(x=exdate, color='r',
                label=f"Ex-Date: {datetime.strftime(exdate,r'%d/%b/%Y' )}")
    plt.axvline(x=announcement, color='g',
                label=f"Announcement Date: {datetime.strftime(announcement, r'%d/%b/%Y')}")
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.grid(axis='y', color='gray')

    try: 
        os.mkdir(path=f'{company_name}')
    except FileExistsError:
        pass

    f.savefig(f'{company_name}/{figure_name}.png', bbox_inches='tight')
    f.clear()
    # plt.show()


def prepare_all_charts(scrip_code, scrip_name=''):
    data_frame = prepare_dataframe(scrip_code=scrip_code, scrip_name=scrip_name)
    print(data_frame)
    # return
    for idx, scrip in data_frame.iterrows():
        
        print(data_frame)
        print(scrip)
        announcement = datetime.strptime(str(scrip['announcement']), r'%Y%m%d')
        exdate = datetime.strptime(str(scrip['exdate']), r'%Y%m%d')
        start_date = announcement - timedelta(days=10)
        end_date = exdate + timedelta(days=10)

        print(announcement, exdate, start_date, end_date)

        prepare_chart(
            scrip_code=scrip_code,
            start_date=start_date,
            end_date=end_date,
            exdate=exdate,
            announcement=announcement,
            dividend_amount=scrip['dividend'],
            company_name=scrip_name,
            figure_name=idx
        )
        # break



if __name__ == '__main__':
    stock = input('Enter the SENSEX company you would like to look up: ')
    df = pd.read_csv('Sensex.csv')
    closest_guess = max(df['COMPANY'], key= lambda x: damerauLevenshtein(x, stock, similarity=True))
    print(closest_guess)
    print(df[df['COMPANY'] == closest_guess]['Scrip Code'].values[0])


    

