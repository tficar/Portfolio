#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import datetime
import yfinance as yf
pd.options.mode.chained_assignment = None

def get_spy_returns(date_start='2020-01-01', date_end='2020-09-19'):
    
    spy = yf.Ticker('SPY')
    spy_returns = spy.history(period='1d', start=date_start, end=date_end)
    spy_returns_prch = spy_returns.diff().cumsum()
    spy_returns_pctch = spy_returns_prch / spy_returns.iloc[0]
    
    return spy_returns_pctch

def get_hsa_return(balance_df,deposits_df):
    '''
    Returns a factor that is the time-weighted rate of return (TWRR) 
    
    Params:
        balance_df (dataframe): the df that contains balance info
        deposits_df (dataframe): the df that contains any deposits/withdrawals made
    Returns:
        the TWRR for the given period
    '''
    
    balances = []
    cash_flows = []

    balances.append(balance_df.iloc[0,0])
    cash_flows.append(0)

    for i,row in balance_df.iterrows():

        if i in deposits_df.index:

            balances.append(balance_df.loc[i,'Account value'])
            cash_flows.append(deposits_df.loc[i,'AMOUNT'])

    hsa_returns = []

    for i in range(0,len(balances)-1):

        if i == 0:
            hsa_returns.append(1 + (balances[i+1]-balances[i])/balances[i])
        else:
            hsa_returns.append(1 + (balances[i+1]-balances[i]-cash_flows[i])/(balances[i]-cash_flows[i]))
        
    return np.prod(hsa_returns)

# get_hsa_return(balance_hsa,deposits_hsa)

def get_selfdir_return(balance_df,deposits_df):
    '''
    Returns a factor that is the time-weighted rate of return (TWRR) 
    
    Params:
        balance_df (dataframe): the df that contains balance info
        deposits_df (dataframe): the df that contains any deposits/withdrawals made
    Returns:
        the TWRR for the given period
    '''
    
    balances = []
    cash_flows = []

    balances.append(balance_df.iloc[0,0])

    for i,row in balance_df.iterrows():

        if i in deposits_df.index:

            balances.append(balance_df.loc[i,'Account value'])
            cash_flows.append(deposits_df.loc[i,'AMOUNT'])

    selfdir_returns = []

    for i in range(0,len(balances)-1):

        if i == 0:
            selfdir_returns.append(1 + (balances[i+1]-balances[i])/balances[i])
        else:
            if balances[i]-cash_flows[i] == 0:
                    selfdir_returns.append(1.0)
            else:
                selfdir_returns.append(1 + (balances[i+1]-balances[i]-cash_flows[i])/(balances[i]-cash_flows[i]))

    return np.prod(selfdir_returns)

# get_selfdir_return(balance_selfdir,deposits_selfdir)

def get_hsa_daily_return(balance_hsa,deposit_hsa):
    '''
    Returns a df of the daily returns
    
    Params:
        balance_hsa (dataframe): the df that contains balance info
        deposits_hsa (dataframe): the df that contains any deposits/withdrawals made
    Returns:
        df of daily returns that can be plotted
    '''
        
    hsa_returns_daily = balance_hsa

    for date in deposits_hsa.index:

        deposit = deposits_hsa.loc[deposits_hsa.index == date,'AMOUNT']

        for i, row in hsa_returns_daily.iterrows():

            balance = hsa_returns_daily.loc[i,'Account value']

            if i >= date:

                hsa_returns_daily.at[i,'Account value'] = (hsa_returns_daily.at[i,'Account value'] - deposit)

    balance_hsa_prch = hsa_returns_daily.diff().cumsum()
    balance_hsa_pctch = balance_hsa_prch / hsa_returns_daily.iloc[0]
    
    return balance_hsa_pctch

def get_selfdir_daily_returns(balance_selfdir,deposits_selfdir):
    '''
    Returns a df of the daily returns
    
    Params:
        balance_selfdir (dataframe): the df that contains balance info
        deposits_selfdir (dataframe): the df that contains any deposits/withdrawals made
    Returns:
        df of daily returns that can be plotted
    '''
    
    selfdir_returns_daily = balance_selfdir

    for date in deposits_selfdir.index:

        # Ignore first instance of balance and deposit since we need a starting point
        if date == deposits_selfdir.index[0]:
            continue

        deposit = deposits_selfdir.loc[deposits_selfdir.index == date,'AMOUNT']

        for i, row in selfdir_returns_daily.iterrows():

            balance = selfdir_returns_daily.loc[i,'Account value']

            if i >= date:

                selfdir_returns_daily.at[i,'Account value'] = (selfdir_returns_daily.at[i,'Account value'] - deposit)

    balance_selfdir_prch = selfdir_returns_daily.diff().cumsum()
    # If using original deposit of 2000 as a starting point, returns are inflated
    # Instead, I am using the average balance of 6000
    balance_selfdir_pctch = balance_selfdir_prch / (selfdir_returns_daily.iloc[0] + 4000)
    
    return balance_selfdir_pctch

def plot_daily_returns(spy,hsa,selfdir):
    
    '''Plots the daily returns of accounts compared to SPY as a benchmark'''
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=spy.index, y=spy['Close'],mode='lines',name='SPY'))
    fig.add_trace(go.Scatter(x=hsa.index, y=hsa['Account value'],mode='lines',name='HSA'))
    fig.add_trace(go.Scatter(x=selfdir.index, y=selfdir['Account value'],mode='lines', name='SELFDIR'))
    return fig

def get_return_metrics(real_gains_hsa,real_gains_selfdir):
    '''
    Returns a df of return metrics for various trading strategies
    
    Params:
        real_gains_hsa (dataframe): the df that contains gains/losses for the hsa account
        real_gains_selfdir (dataframe): the df that contains gains/losses for the self directed account
    Returns:
        df of summary stats for each account returns
    '''
    
    # Day trade info for HSA
    day_trade_hsa = real_gains_hsa.loc[real_gains_hsa['Open date'] == real_gains_hsa['Close date'],:]
    dt_numtrades_hsa = len(day_trade_hsa['Qty'])
    dt_winpct_hsa = len(day_trade_hsa.loc[day_trade_hsa['Adj gain($)'] > 0,'Qty'])/len(day_trade_hsa['Qty'])
    dt_avgwin_hsa = day_trade_hsa.loc[day_trade_hsa['Adj gain($)'] >= 0,'Adj gain($)'].sum()/len(day_trade_hsa.loc[day_trade_hsa['Adj gain($)'] >= 0,'Adj gain($)'])
    dt_avgloss_hsa = day_trade_hsa.loc[day_trade_hsa['Adj gain($)'] < 0,'Adj gain($)'].sum()/len(day_trade_hsa.loc[day_trade_hsa['Adj gain($)'] < 0,'Adj gain($)'])
    dt_net_hsa = day_trade_hsa['Adj gain($)'].sum()
    dt_netavg_hsa = day_trade_hsa['Adj gain($)'].sum()/len(day_trade_hsa['Adj gain($)'])
    
    day_trade_hsa_metrics = pd.DataFrame([[dt_numtrades_hsa,dt_winpct_hsa,dt_avgwin_hsa,dt_avgloss_hsa,dt_net_hsa,dt_netavg_hsa]],
                                     columns=['NumTrades','WinPct','AvgWin','AvgLoss','Net','NetAvg'], index=['DT_HSA'])
    
    # Day trade info for selfdir
    day_trade_selfdir = real_gains_selfdir.loc[real_gains_selfdir['Open date'] == real_gains_selfdir['Close date'],:]
    dt_numtrades_selfdir = len(day_trade_selfdir['Qty'])
    dt_winpct_selfdir = len(day_trade_selfdir.loc[day_trade_selfdir['Adj gain($)'] > 0,'Qty'])/len(day_trade_selfdir['Qty'])
    dt_avgwin_selfdir = day_trade_selfdir.loc[day_trade_selfdir['Adj gain($)'] >= 0,'Adj gain($)'].sum()/len(day_trade_selfdir.loc[day_trade_selfdir['Adj gain($)'] >= 0,'Adj gain($)'])
    dt_avgloss_selfdir = day_trade_selfdir.loc[day_trade_selfdir['Adj gain($)'] < 0,'Adj gain($)'].sum()/len(day_trade_selfdir.loc[day_trade_selfdir['Adj gain($)'] < 0,'Adj gain($)'])
    dt_net_selfdir = day_trade_selfdir['Adj gain($)'].sum()
    dt_netavg_selfdir = day_trade_selfdir['Adj gain($)'].sum()/len(day_trade_selfdir['Adj gain($)'])

    day_trade_selfdir_metrics = pd.DataFrame([[dt_numtrades_selfdir,dt_winpct_selfdir,dt_avgwin_selfdir,dt_avgloss_selfdir,
                                               dt_net_selfdir,dt_netavg_selfdir]],columns=['NumTrades','WinPct','AvgWin',
                                                                                           'AvgLoss','Net','NetAvg'],
                                             index=['DT_SELFDIR'])
    
    # Combine day trade dfs
    day_trade_metrics = pd.concat([day_trade_hsa_metrics,day_trade_selfdir_metrics])
    
    # Gets option indicator
    real_gains_hsa_excl_dt = real_gains_hsa.loc[real_gains_hsa['Open date'] != real_gains_hsa['Close date'],:]
    real_gains_hsa_excl_dt['Option'] = [int(a.split()[-1] in ['Put','Call']) for a in real_gains_hsa_excl_dt['Security']]
    real_gains_selfdir_excl_dt = real_gains_selfdir.loc[real_gains_selfdir['Open date'] != real_gains_selfdir['Close date'],:]
    real_gains_selfdir_excl_dt['Option'] = [int(a.split()[-1] in ['Put','Call']) for a in real_gains_selfdir_excl_dt['Security']]

    # Stock return info for HSA
    stock_hsa = real_gains_hsa_excl_dt.loc[real_gains_hsa_excl_dt['Option'] == 0,:]
    stock_numtrades_hsa = len(stock_hsa.index)
    stock_winpct_hsa = len(stock_hsa.loc[stock_hsa['Adj gain($)'] > 0,'Qty'])/len(stock_hsa.index)
    stock_avgwin_hsa = stock_hsa.loc[stock_hsa['Adj gain($)'] >= 0,'Adj gain($)'].sum()/len(stock_hsa.loc[stock_hsa['Adj gain($)'] >= 0,'Adj gain($)'])
    stock_avgloss_hsa = stock_hsa.loc[stock_hsa['Adj gain($)'] < 0,'Adj gain($)'].sum()/len(stock_hsa.loc[stock_hsa['Adj gain($)'] < 0,'Adj gain($)'])
    stock_net_hsa = stock_hsa['Adj gain($)'].sum()
    stock_netavg_hsa = stock_hsa['Adj gain($)'].sum()/len(stock_hsa['Adj gain($)'])
    
    stock_hsa_metrics = pd.DataFrame([[stock_numtrades_hsa,stock_winpct_hsa,stock_avgwin_hsa,stock_avgloss_hsa,stock_net_hsa,
                                       stock_netavg_hsa]],columns=['NumTrades','WinPct','AvgWin','AvgLoss','Net','NetAvg'],
                                     index=['STOCK_HSA'])
    
    # Option return info for HSA
    option_hsa = real_gains_hsa_excl_dt.loc[real_gains_hsa_excl_dt['Option'] == 1,:]
    option_numtrades_hsa = len(option_hsa.index)
    option_winpct_hsa = len(option_hsa.loc[option_hsa['Adj gain($)'] > 0,'Qty'])/len(option_hsa.index)
    option_avgwin_hsa = option_hsa.loc[option_hsa['Adj gain($)'] >= 0,'Adj gain($)'].sum()/len(option_hsa.loc[option_hsa['Adj gain($)'] >= 0,'Adj gain($)'])
    option_avgloss_hsa = option_hsa.loc[option_hsa['Adj gain($)'] < 0,'Adj gain($)'].sum()/len(option_hsa.loc[option_hsa['Adj gain($)'] < 0,'Adj gain($)'])
    option_net_hsa = option_hsa['Adj gain($)'].sum()
    option_netavg_hsa = option_hsa['Adj gain($)'].sum()/len(option_hsa['Adj gain($)'])
    
    option_hsa_metrics = pd.DataFrame([[option_numtrades_hsa,option_winpct_hsa,option_avgwin_hsa,option_avgloss_hsa,
                                        option_net_hsa,option_netavg_hsa]],columns=['NumTrades','WinPct','AvgWin','AvgLoss',
                                                                                    'Net','NetAvg'],index=['OPTION_HSA'])
    
    # Stock return info for selfdir
    stock_selfdir = real_gains_selfdir_excl_dt.loc[real_gains_selfdir_excl_dt['Option'] == 0,:]
    stock_numtrades_selfdir = len(stock_selfdir.index)
    stock_winpct_selfdir = len(stock_selfdir.loc[stock_selfdir['Adj gain($)'] > 0,'Qty'])/len(stock_selfdir.index)
    stock_avgwin_selfdir = stock_selfdir.loc[stock_selfdir['Adj gain($)'] >= 0,'Adj gain($)'].sum()/len(stock_selfdir.loc[stock_selfdir['Adj gain($)'] >= 0,'Adj gain($)'])
    stock_avgloss_selfdir = stock_selfdir.loc[stock_selfdir['Adj gain($)'] < 0,'Adj gain($)'].sum()/len(stock_selfdir.loc[stock_selfdir['Adj gain($)'] < 0,'Adj gain($)'])
    stock_net_selfdir = stock_selfdir['Adj gain($)'].sum()
    stock_netavg_selfdir = stock_selfdir['Adj gain($)'].sum()/len(stock_selfdir['Adj gain($)'])
    
    stock_selfdir_metrics = pd.DataFrame([[stock_numtrades_selfdir,stock_winpct_selfdir,stock_avgwin_selfdir,
                                           stock_avgloss_selfdir,stock_net_selfdir,stock_netavg_selfdir]],
                                         columns=['NumTrades','WinPct','AvgWin','AvgLoss','Net','NetAvg'],
                                         index=['STOCK_SELFDIR'])
    
    # Option return info for selfdir
    option_selfdir = real_gains_selfdir_excl_dt.loc[real_gains_selfdir_excl_dt['Option'] == 1,:]
    option_numtrades_selfdir = len(option_selfdir.index)
    option_winpct_selfdir = len(option_selfdir.loc[option_selfdir['Adj gain($)'] > 0,'Qty'])/len(option_selfdir.index)
    option_avgwin_selfdir = option_selfdir.loc[option_selfdir['Adj gain($)'] >= 0,'Adj gain($)'].sum()/len(option_selfdir.loc[option_selfdir['Adj gain($)'] >= 0,'Adj gain($)'])
    option_avgloss_selfdir = option_selfdir.loc[option_selfdir['Adj gain($)'] < 0,'Adj gain($)'].sum()/len(option_selfdir.loc[option_selfdir['Adj gain($)'] < 0,'Adj gain($)'])
    option_net_selfdir = option_selfdir['Adj gain($)'].sum()
    option_netavg_selfdir = option_selfdir['Adj gain($)'].sum()/len(option_selfdir['Adj gain($)'])
    
    option_selfdir_metrics = pd.DataFrame([[option_numtrades_selfdir,option_winpct_selfdir,option_avgwin_selfdir,
                                            option_avgloss_selfdir,option_net_selfdir,option_netavg_selfdir]],
                                          columns=['NumTrades','WinPct','AvgWin','AvgLoss','Net','NetAvg'],
                                          index=['OPTION_SELFDIR'])
    
    # Combine all results from above
    stock_metrics = pd.concat([stock_hsa_metrics,stock_selfdir_metrics])
    option_metrics = pd.concat([option_hsa_metrics,option_selfdir_metrics])
    perf_metrics = pd.concat([day_trade_metrics,stock_metrics,option_metrics])
    
    # Add row for overall totals/averages
    num_trades_total = sum(perf_metrics['NumTrades'])
    weights = [a/num_trades_total for a in perf_metrics['NumTrades']]
    winpct_avg = sum(weights*perf_metrics['WinPct'])
    win_avg = sum(weights*perf_metrics['AvgWin'])
    loss_avg = sum(weights*perf_metrics['AvgLoss'])
    net_total = sum(perf_metrics['Net'])
    netavg_avg = sum(weights*perf_metrics['NetAvg'])
    totals_df = pd.DataFrame(index=['TOTAL'],data=[[num_trades_total,winpct_avg,win_avg,loss_avg,net_total,netavg_avg]],
                             columns=perf_metrics.columns)
    perf_metrics = pd.concat([perf_metrics,totals_df])
    
    return perf_metrics

if __name__ == '__main__':
    
    start_date = input('Enter desired start date (yyyymmdd): ')
    end_date = input('Enter desired end date (yyyymmdd): ')
    start_date_str = start_date[:4] + '-' + start_date[4:6] + '-' + start_date[6:8]
    end_date_str = end_date[:4] + '-' + end_date[4:6] + '-' + end_date[6:8]
    # Load all reports from TDA
    # Make way to automate downloading these files
    balance_hsa = pd.read_csv('C:/Users/Tristan/Documents/Learning/Python/Data/TDA/chart (7).csv', thousands=',')
    balance_selfdir = pd.read_csv('C:/Users/Tristan/Documents/Learning/Python/Data/TDA/chart (8).csv', thousands=',')
    deposits_hsa = pd.read_csv('C:/Users/Tristan/Documents/Learning/Python/Data/TDA/transactions (2).csv', thousands=',')
    deposits_selfdir = pd.read_csv('C:/Users/Tristan/Documents/Learning/Python/Data/TDA/transactions (3).csv', thousands=',')
    real_gains_hsa = pd.read_excel(f'C:/Users/Tristan/Documents/Learning/Python/Data/TDA/RC_124002398_{start_date}_{end_date}.xlsx', headers=True, thousands=',')
    real_gains_selfdir = pd.read_excel(f'C:/Users/Tristan/Documents/Learning/Python/Data/TDA/RC_454325656_{start_date}_{end_date}.xlsx', headers=True, thousands=',')
    # Unrealized gains are on 2 different sheets. Concat to combine them
    unreal_gainslo_hsa = pd.read_excel(f'C:/Users/Tristan/Documents/Learning/Python/Data/TDA/UC_124002398_{end_date}.xlsx', sheet_name='Unrealized Long', headers=True, thousands=',')
    unreal_gainssh_hsa = pd.read_excel(f'C:/Users/Tristan/Documents/Learning/Python/Data/TDA/UC_124002398_{end_date}.xlsx', sheet_name='Unrealized Short', headers=True, thousands=',')
    unreal_gains_hsa = pd.concat([unreal_gainslo_hsa,unreal_gainssh_hsa]).reset_index(drop=True)
    unreal_gainslo_selfdir = pd.read_excel(f'C:/Users/Tristan/Documents/Learning/Python/Data/TDA/UC_454325656_{end_date}.xlsx', sheet_name='Unrealized Long', headers=True, thousands=',')
    unreal_gainssh_selfdir = pd.read_excel(f'C:/Users/Tristan/Documents/Learning/Python/Data/TDA/UC_454325656_{end_date}.xlsx', sheet_name='Unrealized Short', headers=True, thousands=',')
    unreal_gains_selfdir = pd.concat([unreal_gainslo_selfdir,unreal_gainssh_selfdir]).reset_index(drop=True)
    
    # Clean all dfs
    balance_hsa.dropna(inplace=True)
    balance_hsa['Date'] = [datetime.datetime.strptime(a,'%m/%d/%Y') for a in balance_hsa['Date']]
    balance_hsa.set_index('Date', inplace=True)
    balance_selfdir.dropna(inplace=True)
    balance_selfdir['Date'] = [datetime.datetime.strptime(a,'%m/%d/%Y') for a in balance_selfdir['Date']]
    balance_selfdir.set_index('Date', inplace=True)
    balance_selfdir['Account value'].replace(0,2000.00,inplace=True)

    deposits_hsa.dropna(subset=['TRANSACTION ID'], inplace=True)
    deposits_hsa = deposits_hsa[deposits_hsa['DESCRIPTION'].str.contains('TRANSFER.*')].reset_index(drop=True)
    deposits_hsa['DATE'] = [datetime.datetime.strptime(a,'%m/%d/%Y') for a in deposits_hsa['DATE']]
    deposits_hsa.set_index('DATE', inplace=True)
    deposits_selfdir.dropna(subset=['TRANSACTION ID'], inplace=True)
    deposits_selfdir['DATE'] = [datetime.datetime.strptime(a,'%m/%d/%Y') for a in deposits_selfdir['DATE']]
    deposits_selfdir.set_index('DATE', inplace=True)
    deposits_selfdir.sort_index(inplace=True)

    real_gains_hsa.dropna(subset=['Trans type'], inplace=True)
    real_gains_hsa['Ticker'] = [a.split('(')[1][:-1] if a[-1] == ')' else a.split()[0] for a in real_gains_hsa['Security']]
    real_gains_hsa.set_index('Ticker', inplace=True)
    real_gains_selfdir.dropna(subset=['Trans type'], inplace=True)
    real_gains_selfdir['Ticker'] = [a.split('(')[1][:-1] if a[-1] == ')' else a.split()[0] for a in real_gains_selfdir['Security']]
    real_gains_selfdir.set_index('Ticker', inplace=True)

    unreal_gains_hsa.dropna(subset=['Qty'], inplace=True)
    unreal_gains_hsa['Ticker'] = [a.split('(')[1][:-1] if a[-1] == ')' else a.split()[0] for a in unreal_gains_hsa['Security']]
    unreal_gains_hsa.set_index('Ticker', inplace=True)
    unreal_gains_selfdir.dropna(subset=['Qty'], inplace=True)
    unreal_gains_selfdir['Ticker'] = [a.split('(')[1][:-1] if a[-1] == ')' else a.split()[0] for a in unreal_gains_selfdir['Security']]
    unreal_gains_selfdir.set_index('Ticker', inplace=True)
    
    # Get benchmark info
    spy = get_spy_returns(date_start = start_date_str, date_end = end_date_str)
    
    # Get time-weighted return for each account. This is the return metric used to compare investment results
    twrr_hsa = get_hsa_return(balance_hsa,deposits_hsa)
    twrr_selfdir = get_selfdir_return(balance_selfdir,deposits_selfdir)
    
    # Get daily returns for each account. These are not time-weighted, so they may be inflated
    daily_return_hsa = get_hsa_daily_return(balance_hsa,deposits_hsa)
    daily_return_selfdir = get_selfdir_daily_returns(balance_selfdir,deposits_selfdir)
    
    # Plot returns compared to benchmark
    daily_returns_plot = plot_daily_returns(spy,daily_return_hsa,daily_return_selfdir)
    
    # Get return metrics
    perf_metrics = get_return_metrics(real_gains_hsa,real_gains_selfdir)
    
    # Save results
    daily_returns_plot.write_html("C:/Users/Tristan/Documents/Learning/Python/Output/TDA/daily_returns.html")
    perf_metrics.to_csv("C:/Users/Tristan/Documents/Learning/Python/Output/TDA/performance_metrics.csv")

    print('Results saved.')
