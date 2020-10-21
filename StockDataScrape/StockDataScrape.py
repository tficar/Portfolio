#!/usr/bin/env python
# coding: utf-8

import requests
import re
import numpy as np
import pandas as pd
import xlsxwriter
import xlrd
from bs4 import BeautifulSoup
import datetime
import pymysql
import yfinance as yf
from sqlalchemy import create_engine

# create sqlalchemy engine
user = 'tficar'
pw = '****'
db = 'test_db'
engine = create_engine(f"mysql+pymysql://{user}:{pw}@localhost/{db}")

# IBD data is not updated on weekend, so we'll use older data
today = datetime.date.today()
weekday = datetime.datetime.today().weekday()
if weekday == 6 or weekday == 0:
    yesterday = today - datetime.timedelta(3)
else:
    yesterday = today - datetime.timedelta(1)
    
as_of_date = yesterday.strftime("%b-%d-%Y").lower()
# as_of_date = datetime.datetime.strptime('2020-07-06',"%Y-%m-%d").strftime("%b-%d-%Y").lower()
low_priced_url = "https://www.investors.com/data-tables/top-ranked-low-priced-stocks-"+as_of_date+"/"
top_composite_url = "https://www.investors.com/data-tables/top-200-composite-stocks-"+as_of_date+"/"

stock_list = pd.read_excel(r'C:\Users\tristan\Documents\Investing\CurrentWatchlist.xlsx',
                          index_col=0, skiprows=1, usecols="B:C")
# For scraping web
headers = {'user-agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "DNT": "1", "Connection": "close", "Upgrade-Insecure-Requests": "1"}

# Threshold for IBD ratings
comp_thresh = 80
eps_thresh = 70


def get_ibd_data(page_url):
    
    """Returns a cleaned df of ibd data for one of the data tables listed on the ibd website"""
    
    # Get html and parse
    result = requests.get(page_url,headers=headers)
    soup = BeautifulSoup(result.text, 'html.parser')
    table = soup.find("table", class_ = "table")
    table = table.find_all('td')
    
    # Iterate over html to format for df
    data = [table[i*10:(i*10)+10] for i in range(int(len(table)/10))]
    data = re.findall(r'>(.*?)<', str(data))
    
    # Remove elements that are unnecessary and clean
    data = [i for i in data if not i in (', ','], [','')]
    if len(re.findall('.composite.',page_url)) > 0:
        data[5] = 'Stock'
        data[6] = 'Symbol'
        data[8] = 'Price Chg'
    data = [i.replace('\xa0',' ') for i in data]
    data = [i.replace('&amp;','&') for i in data]
    data = [i.strip() for i in data]
    
    # Iterate again to format list for df
    data = [data[i*10:(i*10)+10] for i in range(int(len(data)/10))]
    if len(re.findall('.composite.',page_url)) > 0:
        data.pop(1)
    stock_df = pd.DataFrame(data[1:],columns=data[0])
    stock_df.set_index('Symbol', inplace = True)
    
    # Set column names in specified order and sort df
    if len(re.findall('.composite.',page_url)) > 0:
        cols = ['Stock','Closing','Price Chg','Vol%','Comp','EPS','Rel','Acc','52WK']
    else:
        cols = ['Name','Price','Price Chg','Vol% Chg','Cmp Rtg','Eps Rtg','Rel Str','Acc Dis','Yr Hi']
    stock_df = stock_df[cols]
    if len(re.findall('.composite.',page_url)) > 0:
        stock_df.sort_values(by=['Comp','EPS','Rel','Acc'], ascending = [False,False,False,True], inplace = True)
    else:
        stock_df.sort_values(by=['Cmp Rtg','Eps Rtg','Rel Str','Acc Dis'], ascending = [False,False,False,True], inplace = True)
    if len(re.findall('.composite.',page_url)) > 0:
        for col in stock_df.columns:
            if col in ['Stock','Acc']:
                continue
            else:
                stock_df[col] = pd.to_numeric(stock_df[col])
    else:
        for col in stock_df.columns:
    
            if col in ['Name','Acc Dis']:
                continue
            else:
                stock_df[col] = pd.to_numeric(stock_df[col])
    if len(re.findall('.composite.',page_url)) > 0:
        stock_df.columns = ['Name','Price','Price Chg','Vol% Chg','Cmp Rtg','Eps Rtg','Rel Str','Acc Dis','Yr Hi']
        
    # Only return top stocks
    stock_df = stock_df[(stock_df['Cmp Rtg'] >= comp_thresh) & (stock_df['Eps Rtg'] >= eps_thresh)]
        
    return(stock_df)

def get_zacks_data(stock_ticker):
    
    """Returns a df of Zacks stock data for a given stock"""
    
    zacks_url = "https://www.zacks.com/stock/quote/"+stock_ticker+"?q="+stock_ticker
    stock_result = requests.get(zacks_url,headers=headers)
    stock_result_soup = BeautifulSoup(stock_result.text, 'html.parser')
    
    zacks_rank = stock_result_soup.find("div", class_ = "zr_rankbox")
    
    try:
        if zacks_rank.find('p', class_ = 'rank_view').text.strip() == '':
            zacks_rank = '0'
        else:
            try:
                zacks_rank = zacks_rank.find('p', class_ = 'rank_view').text.strip().replace('\xa0 ','')[0]
            except:
                zacks_rank = zacks_rank.find('p', class_ = 'rank_view').text.strip()[0]
    except:
        zacks_rank = '0'
    
    if zacks_rank == '0':
        style_scores = ['NA','NA','NA','NA']
    else:
        style_scores = stock_result_soup.find("div", class_ = "zr_rankbox composite_group")
        style_scores = style_scores.find('p', class_ = 'rank_view').text.strip().replace('\xa0',' ').split('|')
        style_scores = [s.strip() for s in style_scores]
        style_scores = [s[0] for s in style_scores]
    
    zacks_data = pd.DataFrame([[stock_ticker] + list(zacks_rank) + style_scores],
                         columns = ['Stock','ZacksRank','ValueSS','GrowthSS','MomentumSS','VGMSS'])
    zacks_data.set_index('Stock', inplace=True)
    zacks_data['zacks_url'] = zacks_url
    
    return(zacks_data)

def get_finviz_data(stock_ticker):
    
    """Returns a df of finviz stock data for a given stock"""
    
    finviz_url = "https://finviz.com/quote.ashx?t="+stock_ticker+"&ty=c&ta=0&p=w"
    stock_result = requests.get(finviz_url,headers=headers)
    stock_result_soup = BeautifulSoup(stock_result.text, 'html.parser')
    
    finviz_data = stock_result_soup.find("table", class_ = "snapshot-table2")
    if finviz_data is None:
        cols = ['Index', 'P/E', 'EPS (ttm)', 'Insider Own', 'Shs Outstand', 'Perf Week',
                'Market Cap', 'Forward P/E', 'EPS next Y', 'Insider Trans', 'Shs Float',
                'Perf Month', 'Income', 'PEG', 'EPS next Q', 'Inst Own', 'Short Float',
                'Perf Quarter', 'Sales', 'P/S', 'EPS this Y', 'Inst Trans',
                'Short Ratio', 'Perf Half Y', 'Book/sh', 'P/B', 'EPS next Y', 'ROA',
                'Target Price', 'Perf Year', 'Cash/sh', 'P/C', 'EPS next 5Y', 'ROE',
                '52W Range', 'Perf YTD', 'Dividend', 'P/FCF', 'EPS past 5Y', 'ROI',
                '52W High', 'Beta', 'Dividend %', 'Quick Ratio', 'Sales past 5Y',
                'Gross Margin', '52W Low', 'ATR', 'Employees', 'Current Ratio',
                'Sales Q/Q', 'Oper. Margin', 'RSI (14)', 'Volatility', 'Optionable',
                'Debt/Eq', 'EPS Q/Q', 'Profit Margin', 'Rel Volume', 'Prev Close',
                'Shortable', 'LT Debt/Eq', 'Earnings', 'Payout', 'Avg Volume', 'Price',
                'Recom', 'SMA20', 'SMA50', 'SMA200', 'Volume', 'Change']
        vals = list('-'*72)
        finviz_data = pd.DataFrame([vals],columns=cols,index=[stock_ticker])
        finviz_data['finviz_url'] = finviz_url
        finviz_data['Group'] = ''
        return(finviz_data)
    finviz_data = finviz_data.find_all('td')
    
    cols = [data.text for i,data in enumerate(finviz_data) if i % 2 == 0]
    vals = [data.text for i,data in enumerate(finviz_data) if i % 2 != 0]
    
    finviz_data = pd.DataFrame([vals],columns=cols,index=[stock_ticker])
    finviz_data['finviz_url'] = finviz_url
    finviz_group = stock_result_soup.find("table", class_ = "fullview-title")
    finviz_group = [s.strip() for s in finviz_group.text.split('|')][0].split('\n')[-1] + '-' + [s.strip() for s in finviz_group.text.split('|')][1]
    finviz_data['Group'] = finviz_group
    
    return(finviz_data)

def get_yfinance_data(stock_ticker):
    
    """Returns a df of yahoo finance stock data for a given stock"""
    
    stock = yf.Ticker(stock_ticker)
    
    cols = ['EV/EBITDA','EV/Revenue','ROE']
    try:
        vals = [stock.info['enterpriseToEbitda'],
                stock.info['enterpriseToRevenue'],
                stock.info['netIncomeToCommon'] / (stock.info['sharesOutstanding']*stock.info['bookValue'])]
    except:
        vals = [np.nan,np.nan,np.nan]
    
    yf_data = pd.DataFrame([vals],columns=cols,index=[stock_ticker])
    return(yf_data)

def get_sector_data():
    
    """Returns a data frame of sector information and averages"""
    
    # Get industry mappings
    df_industries = pd.read_excel('http://www.stern.nyu.edu/~adamodar/pc/datasets/indname.xls',
                                  sheet_name='Industry sorted (Global)')
    cols = ['Company Name','Ticker','Country','Industry Group']
    df_industries['Ticker'] = [str(a).split(':')[-1] for a in df_industries['Exchange:Ticker']]
    df_industries = df_industries[cols]
    
    # Get EV/EBITDA averages
    df_evebitda = pd.read_excel('http://www.stern.nyu.edu/~adamodar/pc/datasets/vebitda.xls', header=8)
    cols = ['Industry  Name','Number of firms','EV/EBITDA']
    df_evebitda = df_evebitda[cols]
    
    # Get ROE averages
    df_roe = pd.read_excel('http://www.stern.nyu.edu/~adamodar/pc/datasets/roe.xls', header=7)
    cols = ['Industry  Name','Number of firms','ROE (unadjusted)','ROE (adjusted for R&D)']
    df_roe = df_roe[cols]
    
    # Get PE/PEG average
    df_pe = pd.read_excel('http://www.stern.nyu.edu/~adamodar/pc/datasets/pedata.xls', header=7)
    cols = ['Industry  Name','Number of firms','Current PE','Trailing PE','Forward PE','Expected growth - next 5 years',
            'PEG Ratio']
    df_pe = df_pe[cols]
    
    # Get D/E averages
    df_debt = pd.read_excel('http://people.stern.nyu.edu/adamodar/pc/datasets/dbtfund.xls', header=7,
                            sheet_name='Industry Averages')
    cols = ['Industry  Name','Market D/E (unadjusted)','Market D/E (adjusted for leases)',
            'Institutional Holdings']
    df_debt = df_debt[cols]
    
    
    df_final = df_industries.merge(df_evebitda, left_on='Industry Group', right_on='Industry  Name').merge(df_roe,on='Industry  Name').merge(df_pe,on='Industry  Name').merge(df_debt,on='Industry  Name')
    df_final.index = df_final['Ticker']
    cols = ['Company Name','Industry Group','Number of firms','EV/EBITDA','ROE (unadjusted)','ROE (adjusted for R&D)',
            'Current PE','Trailing PE','Forward PE','Expected growth - next 5 years','PEG Ratio','Market D/E (unadjusted)']
    df_final = df_final[cols]
    df_final.columns = ['Company Name','Industry Group','Number of firms','EV/EBITDA_sec','ROE_sec','ROE_adj_sec',
                        'PE_curr_sec','PE_trail_sec','PE_for_sec','Exp_growth_5yr_sec','PEG_sec','D/E_sec']
    
    return df_final

def save_stock_data(watchlist_clean, full_watchlist, low_priced_stocks, top_comp_stocks):
    
    """Takes all 4 dataframes and saves them to MySQL and Excel"""
    
    writer = pd.ExcelWriter(r'C:\Users\tristan\Documents\Investing\CurrentWatchlistData.xlsx')
    workbook = writer.book

    watchlist_clean.to_excel(excel_writer = writer, header=True, sheet_name='WatchlistDataClean')
    full_watchlist.to_excel(excel_writer = writer, header=True, sheet_name='WatchlistData')
    low_priced_stocks.to_excel(excel_writer = writer, header=True, sheet_name='LowPricedStocks')
    top_comp_stocks.to_excel(excel_writer = writer, header=True, sheet_name='TopCompStocks')

    wdc_sheet = writer.sheets['WatchlistDataClean']
    wd_sheet = writer.sheets['WatchlistData']
    lp_sheet = writer.sheets['LowPricedStocks']
    tc_sheet = writer.sheets['TopCompStocks']
    wdc_sheet.set_column('B:B', 30)
    wd_sheet.set_column('B:B', 30)
    lp_sheet.set_column('B:B', 15)
    tc_sheet.set_column('B:B', 15)

    writer.save()
    
    watchlist_clean.reset_index().to_sql('stocks_full_watchlist_clean',con = engine,if_exists = 'replace')
    full_watchlist.reset_index().to_sql('stocks_full_watchlist',con = engine,if_exists = 'replace')
    low_priced_stocks.reset_index().to_sql('stocks_low_priced',con = engine,if_exists = 'replace')
    top_comp_stocks.reset_index().to_sql('stocks_top_comp',con = engine,if_exists = 'replace')

if __name__ == '__main__':
    
    low_priced_stock_data = get_ibd_data(low_priced_url)
    top_composite_stock_data = get_ibd_data(top_composite_url)
    ibd_data = pd.concat([low_priced_stock_data,top_composite_stock_data])
    ibd_data.drop_duplicates(keep='first',inplace=True)

    # Include stocks from personal watchlist
    full_watchlist = list(set(list(ibd_data.index)+list(stock_list.index)))
    total_time = 0

    # Scrape zacks
    for i,stock in enumerate(full_watchlist):

        start_time = datetime.datetime.now()
        if i == 0:
            zacks_data = get_zacks_data(stock)
        else:
            zacks_data = zacks_data.append(get_zacks_data(stock))
        print(stock + ' - Time Elapsed: ' + str(round((datetime.datetime.now() - start_time).seconds + (datetime.datetime.now() - start_time).microseconds/1000000,2)) + ' seconds')

        total_time += (datetime.datetime.now() - start_time).seconds + (datetime.datetime.now() - start_time).microseconds/1000000

    print('Total zacks time: ' + str(round(total_time/60,2)) + ' minutes\n')

    # Scrape finviz
    total_time = 0

    for i,stock in enumerate(full_watchlist):

        start_time = datetime.datetime.now()
        if i == 0:
            finviz_data = get_finviz_data(stock)
        else:
            finviz_data = finviz_data.append(get_finviz_data(stock))
        print(stock + ' - Time Elapsed: ' + str(round((datetime.datetime.now() - start_time).seconds + (datetime.datetime.now() - start_time).microseconds/1000000,2)) + ' seconds')

        total_time += (datetime.datetime.now() - start_time).seconds + (datetime.datetime.now() - start_time).microseconds/1000000

    print('Total finviz time: ' + str(round(total_time/60,2)) + ' minutes\n')

    # Join dfs
    watchlist_data = pd.concat([zacks_data,finviz_data], axis=1, join='outer')
    watchlist_data.replace('-',0,inplace=True)
    watchlist_data['Volume'] = [str(v).replace(',','') for v in watchlist_data['Volume'].values]
    watchlist_data = watchlist_data.merge(ibd_data.iloc[:,4:8], left_index=True, right_index=True, how='left').fillna('')

    # Clean data
    for col in watchlist_data.columns:

        if col in ['ZacksRank','P/E','EPS (ttm)','Forward P/E','PEG','EPS next Q','P/S','Short Ratio','Book/sh',
                   'P/B','Target Price','Cash/sh','P/C','Dividend','P/FCF','Beta','Quick Ratio','ATR','Employees','Current Ratio',
                   'RSI (14)','Debt/Eq','Rel Volume','Prev Close','LT Debt/Eq','Price','Recom','Volume','Cmp Rtg','Eps Rtg','Rel Str']:
            watchlist_data[col] = pd.to_numeric(watchlist_data[col])
        else:
            continue

    watchlist_cols = ['Group','Price','Volume','Avg Volume','P/E','PEG','Recom','Target Price','ZacksRank','ValueSS','GrowthSS',
                      'MomentumSS','VGMSS','Cmp Rtg','Eps Rtg','Rel Str','Acc Dis','Market Cap','RSI (14)','Insider Own',
                      'Insider Trans','Inst Own','Inst Trans','Current Ratio','Quick Ratio','Beta','Short Ratio','Book/sh',
                      'P/B','Cash/sh','Debt/Eq','Sales Q/Q','EPS Q/Q','Gross Margin','Oper. Margin','Profit Margin','Perf Week',
                      'Perf Year','Earnings']
    watchlist_data = watchlist_data[watchlist_cols]

    # Get yfinance data
    total_time = 0

    for i,stock in enumerate(full_watchlist):

        start_time = datetime.datetime.now()
        if i == 0:
            yfinance_data = get_yfinance_data(stock)
        else:
            yfinance_data = yfinance_data.append(get_yfinance_data(stock))
        print(stock + ' - Time Elapsed: ' + str(round((datetime.datetime.now() - start_time).seconds + (datetime.datetime.now() - start_time).microseconds/1000000,2)) + ' seconds')

        total_time += (datetime.datetime.now() - start_time).seconds + (datetime.datetime.now() - start_time).microseconds/1000000

    print('Total yfinance time: ' + str(round(total_time/60,2)) + ' minutes\n')

    # Get sector data and clean final df
    sector_averages = get_sector_data()

    watchlist_data_clean = watchlist_data[['Group','Price','Avg Volume','P/E', 'PEG','P/B','Debt/Eq']]
    watchlist_data_clean = watchlist_data_clean.merge(yfinance_data,left_index=True, right_index=True)
    watchlist_data_clean = watchlist_data_clean.merge(sector_averages[['Industry Group','EV/EBITDA_sec','ROE_sec',
                                                                       'PE_curr_sec','PEG_sec','D/E_sec']],
                                                      left_index=True,right_index=True)
    watchlist_data_clean.index.rename('Stock', inplace=True)
    watchlist_data_clean = watchlist_data_clean.loc[~watchlist_data_clean.index.duplicated(keep='first')]
    watchlist_data_clean['EV/EBITDA_pctdiff'] = (watchlist_data_clean['EV/EBITDA'] - watchlist_data_clean['EV/EBITDA_sec'])/(watchlist_data_clean['EV/EBITDA_sec'])
    watchlist_data_clean['ROE_pctdiff'] = (watchlist_data_clean['ROE'] - watchlist_data_clean['ROE_sec'])/(watchlist_data_clean['ROE_sec'])
    watchlist_data_clean['PE_pctdiff'] = (watchlist_data_clean['P/E'].replace(0,30) - watchlist_data_clean['PE_curr_sec'])/(watchlist_data_clean['PE_curr_sec'])
    watchlist_data_clean['PEG_pctdiff'] = (watchlist_data_clean['PEG'].replace(0,3) - watchlist_data_clean['PEG_sec'])/(watchlist_data_clean['PEG_sec'])
    watchlist_data_clean['DE_pctdiff'] = (watchlist_data_clean['Debt/Eq'].replace(0,1.5) - watchlist_data_clean['D/E_sec'])/(watchlist_data_clean['D/E_sec'])

    cols = ['Group', 'Price', 'Avg Volume', 'ZacksRank', 'Cmp Rtg', 'Eps Rtg', 'P/E', 'PE_curr_sec', 'PE_pctdiff', 'PEG',
            'PEG_sec', 'PEG_pctdiff', 'Debt/Eq', 'D/E_sec', 'DE_pctdiff', 'EV/EBITDA', 'EV/EBITDA_sec', 'EV/EBITDA_pctdiff',
            'ROE', 'ROE_sec', 'ROE_pctdiff', 'P/B']
    watchlist_data_clean = watchlist_data_clean[cols]

    # Rank df by factors
    asc_label = [1,2,3,4,5]
    desc_label = [5,4,3,2,1]
    watchlist_data_clean['PE_rank'] = pd.qcut(watchlist_data_clean['PE_pctdiff'], q=5, labels=asc_label)
    watchlist_data_clean['PEG_rank'] = pd.qcut(watchlist_data_clean['PEG_pctdiff'].fillna(3), q=5, labels=asc_label)
    watchlist_data_clean['DE_rank'] = pd.qcut(watchlist_data_clean['DE_pctdiff'], q=5, labels=asc_label)
    watchlist_data_clean['EV/EBITDA_rank'] = pd.qcut(watchlist_data_clean['EV/EBITDA_pctdiff'], q=5, labels=asc_label)
    watchlist_data_clean['ROE_rank'] = pd.qcut(watchlist_data_clean['ROE_pctdiff'], q=5, labels=desc_label)
    watchlist_data_clean['PB_rank'] = pd.qcut(watchlist_data_clean['P/B'], q=5, labels=asc_label)

    rank_cols = [col for col in watchlist_data_clean.columns if 'rank' in col]
    [watchlist_data_clean[col].fillna(3, inplace=True) for col in watchlist_data_clean[rank_cols]]
    watchlist_data_clean['tmf_rank'] = watchlist_data_clean[rank_cols].mean(axis=1)
    watchlist_data_clean.sort_values(by='tmf_rank', inplace=True)
    
    # Save data
    save_stock_data(watchlist_data_clean, watchlist_data, low_priced_stock_data, top_composite_stock_data)
