#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# import seaborn as sns
# import re
from pytrends.request import TrendReq
from pytrends.exceptions import ResponseError
# get_ipython().run_line_magic('matplotlib', 'inline')

# For plotly charts
import chart_studio.plotly as py
from chart_studio.plotly import iplot
import plotly.graph_objs as go

# For dash dashboard
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

# Initialize instance of pytrends
pytrend = TrendReq()

def get_trends_over_time(kw_list, timeframe = 'today 5-y', geo = 'World'):

    """
    Returns a plotly line chart for a given keyword list, timeframe, and scope of geography

    Params:
        kw_list (string): a keyword list of interest (eg 'keto')
        timeframe (string): a timeframe to view the trend
            - defaults to 'today 5-y'
            - can only be values of 'today 5-y','today 12-m','today 3-m','today 1-m','now 7-d','now 1-d'
        geo (string): a scope for the location
            - defaults to 'World'
            - can be any two-letter country abbreviation or the default value

    Returns:
        plotly lineplot showing trend over given timeframe
    """

    valid_timeframes = ['today 5-y','today 12-m','today 3-m','today 1-m','now 7-d','now 1-d']

    if timeframe not in valid_timeframes:
        raise Exception('Invalid timeframe. See docstring for valid timeframes.')

    group_key_words = list(zip(*[iter(kw_list)]*1))
    group_key_words = [list(x) for x in group_key_words]
    dicti = {}
    i = 1

    try:
        if geo == 'World':
            for word in group_key_words:
                pytrend.build_payload(word, timeframe = timeframe)
                dicti[i] = pytrend.interest_over_time()
                i+=1
        else:
            for word in group_key_words:
                pytrend.build_payload(word, timeframe = timeframe, geo = geo)
                dicti[i] = pytrend.interest_over_time()
                i+=1
    except ResponseError:
        raise Exception('Google response failed. Make sure the country code is valid.')

    df_trend = pd.concat(dicti, axis=1)
    df_trend.columns = df_trend.columns.droplevel(0)
    df_trend = df_trend.drop('isPartial', axis = 1)
    # df_trend.reset_index(level=0, inplace=True)
    df_final = pd.melt(df_trend.reset_index(), id_vars='date', value_vars=kw_list, var_name = 'keyword')

    return df_final

# plot_trends_over_time(['keto','probiotics','collagen','vitamin c','fat loss'], timeframe = 'today 3-m')

def get_regional_trends(kw_list, timeframe = 'today 5-y', geo = 'World', resolution = 'COUNTRY'):

    """
    Returns a df for a given keyword list, timeframe, and scope of geography. Meant for use with the related plot function

    Params:
        kw_list (string): a keyword list of interest (eg 'keto')
        timeframe (string): a timeframe to view the trend
            - defaults to 'today 5-y'
            - can only be values of 'today 5-y','today 12-m','today 3-m','today 1-m','now 7-d','now 1-d'
        geo (string): a scope for the location
            - defaults to 'World'
            - can be any two-letter country abbreviation or the default value
        resolution (string): how granular to drill down to
            - defaults to 'COUNTRY'
            - only other option is 'DMA', which is metro level data

    Returns:
        df with each keyword in its own column
    """

    valid_timeframes = ['today 5-y','today 12-m','today 3-m','today 1-m','now 7-d','now 1-d']

    if timeframe not in valid_timeframes:
        raise Exception('Invalid timeframe. See docstring for valid timeframes.')

    group_key_words = list(zip(*[iter(kw_list)]*1))
    group_key_words = [list(x) for x in group_key_words]
    dicti = {}
    i = 1

    try:
        if geo == 'World':
            for word in group_key_words:
                pytrend.build_payload(word, timeframe = timeframe)
                dicti[i] = pytrend.interest_by_region(resolution=resolution)
                i+=1
        else:
            for word in group_key_words:
                pytrend.build_payload(word, timeframe = timeframe, geo = geo)
                dicti[i] = pytrend.interest_by_region(resolution=resolution)
                i+=1
    except ResponseError:
        raise Exception('Google response failed. Make sure the country code is valid.')
    except:
        raise Exception('Make sure the resolution is valid. See docstring for valid resolutions.')

    df = pd.concat(dicti, axis=1)
    df.columns = df.columns.droplevel(0)
    return(df)

# get_regional_trends(['keto','fat loss','pokemon','guns'], 'today 3-m', geo = 'US', resolution='DMA')

# def filter_regional_trends(df, state):

    """Filters the regional trend df for a specific state"""

    # r = re.compile(f'.*{state}')
    # return(df[df.index.isin(list(filter(r.match,df.index)))])

# dff = get_regional_trends(['keto','fat loss','pokemon','guns'], 'today 3-m', geo = 'US', resolution='DMA')
# filter_regional_trends(dff,'FL')

def plot_regional_trends(df, kw, show = 'top', amount = 20):

    """
    Returns a plotly bar chart for the given keyword. Meant for use after calling the get_regional_trends function

    Params:
        df (dataframe): a dataframe in the format that is returned by the get_regional_trends function
        kw (str): a single keyword of interest
        show (string): decides which part of the passed dataframe is plotted
            - can be 'top', 'bottom', or 'all'
        amount (int): indicates how many observations to show on the bar chart
    Returns:
        sorted plotly bar chart of the top 20 locations, if applicable
    """

    if kw not in df.columns:
        raise Exception('Keyword is not listed in the dataframe columns.')

    if show == 'all':
        sorted_df = df.sort_values(by = kw, ascending=False)
    elif show == 'bottom':
        sorted_df = df.sort_values(by = kw, ascending=True).head(amount)
    else:
        sorted_df = df.sort_values(by = kw, ascending=False).head(amount)

    mylayout = go.Layout(title="Google Search Trends by Region - {}".format(kw.title()), yaxis_title='Index Ranking')
    fig = go.Figure(layout=mylayout)
    fig.add_bar(x=sorted_df.index, y=sorted_df[kw])
    return(fig)

# plot_regional_trends(get_regional_trends(['keto','fat loss','pokemon','guns'],
#                                          'today 3-m', geo = 'US', resolution='DMA'),'keto','top',5)

def get_related_keywords(kw, timeframe = 'today 5-y', geo = 'World', metric = 'top'):

    """
    Returns a df of related keywords for a given keyword

    Params:
        kw (str): the keyword to compare
        timeframe (string): a timeframe to view the trend
            - defaults to 'today 5-y'
            - can only be values of 'today 5-y','today 12-m','today 3-m','today 1-m','now 7-d','now 1-d'
        geo (string): a scope for the location
            - defaults to 'World'
            - can be any two-letter country abbreviation or the default value
        metric (str): indicates which metric to return in the df
            - options are 'top' or 'rising'

    Returns:
        df with related keywords
    """

    valid_timeframes = ['today 5-y','today 12-m','today 3-m','today 1-m','now 7-d','now 1-d']
    valid_metrics = ['top', 'rising']

    if timeframe not in valid_timeframes:
        raise Exception('Invalid timeframe. See docstring for valid timeframes.')

    if metric not in valid_metrics:
        raise Exception('Invalid metric. See docstring for valid metrics.')

    if geo == 'World':
        pytrend.build_payload([kw], timeframe=timeframe)
    else:
        pytrend.build_payload([kw], timeframe=timeframe, geo = geo)

    return(pytrend.related_queries()[kw][metric])

# get_related_keywords('elderberry', timeframe='today 12-m', geo = 'US', metric='rising')

# Function 4
# pytrend.top_charts(2019, geo = 'US')
# pytrend.today_searches()
# pytrend.trending_searches(pn='mexico')

def get_keyword_correlations(kw_list, timeframe = 'today 5-y', geo = 'World'):

    """
    Returns a correlation matrix for a given keyword list

    Params:
        kw_list (string): a keyword list of interest (eg 'keto')
        timeframe (string): a timeframe to view the trend
            - defaults to 'today 5-y'
            - can only be values of 'today 5-y','today 12-m','today 3-m','today 1-m','now 7-d','now 1-d'
        geo (string): a scope for the location
            - defaults to 'World'
            - can be any two-letter country abbreviation or the default value

    Returns:
        matrix of keywords
    """

    valid_timeframes = ['today 5-y','today 12-m','today 3-m','today 1-m','now 7-d','now 1-d']

    if timeframe not in valid_timeframes:
        raise Exception('Invalid timeframe. See docstring for valid timeframes.')

    group_key_words = list(zip(*[iter(kw_list)]*1))
    group_key_words = [list(x) for x in group_key_words]
    dicti = {}
    i = 1

    try:
        if geo == 'World':
            for word in group_key_words:
                pytrend.build_payload(word, timeframe = timeframe)
                dicti[i] = pytrend.interest_over_time()
                i+=1
        else:
            for word in group_key_words:
                pytrend.build_payload(word, timeframe = timeframe, geo = geo)
                dicti[i] = pytrend.interest_over_time()
                i+=1
    except ResponseError:
        raise Exception('Google response failed. Make sure the country code is valid.')

    df = pd.concat(dicti, axis=1)
    df.columns = df.columns.droplevel(0)
    df = df.drop('isPartial', axis = 1)
    df.reset_index(level=0, inplace=True)

    return df.corr()

# def plot_keyword_correlations(kw_list, timeframe = 'today 5-y', geo = 'World'):

    # """
    # Returns a heatmap of correlations between a given keyword list

    # Params:
        # kw_list (string): a keyword list of interest (eg 'keto')
        # timeframe (string): a timeframe to view the trend
            # - defaults to 'today 5-y'
            # - can only be values of 'today 5-y','today 12-m','today 3-m','today 1-m','now 7-d','now 1-d'
        # geo (string): a scope for the location
            # - defaults to 'World'
            # - can be any two-letter country abbreviation or the default value

    # Returns:
        # heatmap of keywords
    # """

    # valid_timeframes = ['today 5-y','today 12-m','today 3-m','today 1-m','now 7-d','now 1-d']

    # if timeframe not in valid_timeframes:
        # raise Exception('Invalid timeframe. See docstring for valid timeframes.')

    # group_key_words = list(zip(*[iter(kw_list)]*1))
    # group_key_words = [list(x) for x in group_key_words]
    # dicti = {}
    # i = 1

    # try:
        # if geo == 'World':
            # for word in group_key_words:
                # pytrend.build_payload(word, timeframe = timeframe)
                # dicti[i] = pytrend.interest_over_time()
                # i+=1
        # else:
            # for word in group_key_words:
                # pytrend.build_payload(word, timeframe = timeframe, geo = geo)
                # dicti[i] = pytrend.interest_over_time()
                # i+=1
    # except ResponseError:
        # raise Exception('Google response failed. Make sure the country code is valid.')

    # df = pd.concat(dicti, axis=1)
    # df.columns = df.columns.droplevel(0)
    # df = df.drop('isPartial', axis = 1)
    # df.reset_index(level=0, inplace=True)
    # return(sns.heatmap(df.corr(), cmap='coolwarm', center=0, vmin=0, vmax=1, annot=True))

# plot_keyword_correlations(['fat loss','probiotics','keto','protein'],'today 12-m')

df_today_searches = pd.DataFrame(pytrend.today_searches()).rename(columns={'query':'Global Searches Today'})

# Create dash framework
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
        [
            # Row 1
            html.Div(
                [
                    html.H1(
                        html.B('Google Trends Analysis'),
                    ),
                    html.H6(
                        html.B('Summary'),
                    ),
                    html.P(
                        children='''This page uses the pytrends library to get Google Trends data. Select values from the dropdowns,
                                    enter in custom keywords, and then click the submit button to see the trends.
                                    ''',
                    ),
                    html.H6(
                        html.B('Index Ranking Interpretation'),
                    ),
                    html.P(
                        children='''The 'Index Ranking' that is returned is essentially the frequency score in which the term is searched. For example,
                                    using 'keto' below we see that it peaked on 1/6/2019. On 7/1/2018 it had an index ranking of 50. We
                                    can interpret this by simply saying that it was searched half as much on 7/1/2018 as it was on 1/6/2019.
                                    Also, note that each term is independent of one another. The fact that keto and elderberry both have peaks
                                    at 100 does not mean that the frequency was the same between them. The score of 100 simply indicates the
                                    point in time at which the term was searched the most. For terms that are not searched often (try 'kurbo'),
                                    we can see that the index hovers near 0 and then spikes to 100 on the day with the most search volume. So, no matter
                                    what the search volume is, every keyword should have 1 day with an index rank of 100.
                                    ''',
                    )
                ],
                className="row",
                style={'backgroundColor':'#EBF5FB'},
            ),
            # Row blank
            html.Div(
                [
                    html.H3(
                        children=''
                    )
                ],
                className="row",
            ),
            # Row 2
            html.Div(
                [
                    html.H3(
                        children='World & Regional Trends',
                        style={'textAlign': 'center','backgroundColor':'#EBF5FB','font-weight': 'bold'}
                    )
                ],
                className="row",
            ),
            # Row 3
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H6('')
                                ],
                                className="five columns",
                            ),
                            html.Div(
                                [
                                    html.Label('Country'),
                                    dcc.Dropdown(
                                        id='trending_searches_country',
                                        options=[
                                            {'label': 'United States', 'value': 'united_states'},
                                            {'label': 'England', 'value': 'united_kingdom'},
                                            {'label': 'Canada', 'value': 'canada'},
                                            {'label': 'Australia', 'value': 'australia'},
                                            {'label': 'Italy', 'value': 'italy'},
                                            {'label': 'Ireland', 'value': 'ireland'},
                                            {'label': 'Sweden', 'value': 'sweden'},
                                            {'label': 'Germany', 'value': 'germany'},
                                            {'label': 'India', 'value': 'india'},
                                            {'label': 'Indonesia', 'value': 'indonesia'},
                                            {'label': 'Brazil', 'value': 'brazil'},
                                            {'label': 'Japan', 'value': 'japan'}
                                        ],
                                        value='united_states'
                                    ),
                                ],
                                className="two columns",
                            ),
                            html.Div(
                                [
                                    html.H6('')
                                ],
                                className="one columns",
                            ),
                            html.Div(
                                [
                                    html.Label('Year'),
                                    dcc.Dropdown(
                                        id='top_charts_year',
                                        options=[
                                            {'label': '2019', 'value': '2019'},
                                            {'label': '2018', 'value': '2018'},
                                            {'label': '2017', 'value': '2017'},
                                            {'label': '2016', 'value': '2016'},
                                            {'label': '2015', 'value': '2015'},
                                            {'label': '2014', 'value': '2014'},
                                            {'label': '2014', 'value': '2013'},
                                            {'label': '2012', 'value': '2012'},
                                            {'label': '2011', 'value': '2011'}
                                        ],
                                        value='2019'
                                    ),
                                ],
                                className="one columns",
                            ),
                            html.Div(
                                [
                                    html.Label('Country'),
                                    dcc.Dropdown(
                                        id='top_charts_country',
                                        options=[
                                            {'label': 'United States', 'value': 'US'},
                                            {'label': 'England', 'value': 'GB'},
                                            {'label': 'Canada', 'value': 'CA'},
                                            {'label': 'Australia', 'value': 'AU'},
                                            {'label': 'Italy', 'value': 'IT'},
                                            {'label': 'Ireland', 'value': 'IE'},
                                            {'label': 'Sweden', 'value': 'SE'},
                                            {'label': 'Germany', 'value': 'DE'},
                                            {'label': 'India', 'value': 'IN'},
                                            {'label': 'Indonesia', 'value': 'ID'},
                                            {'label': 'Brazil', 'value': 'BR'},
                                            {'label': 'Japan', 'value': 'JP'}
                                        ],
                                        value='US'
                                    ),
                                ],
                                className="two columns",
                            ),

                        ],
                        className="twelve columns",
                    ),
                ],
                # style = dict(justifyContent="center"),
                className="row",
            ),
            # Row 4
            html.Div(
                [
                    html.Div(
                        [
                            dash_table.DataTable(
                                id='today_searches',
                                columns=[{"name": str(i), "id": str(i)} for i in df_today_searches.columns],
                                data=df_today_searches.to_dict("rows"),
                                style_cell={
                                    'width': '300px',
                                    'height': '60px',
                                    'textAlign': 'center'
                                },
                                style_data_conditional=[{
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': 'rgb(248, 248, 248)'
                                }],
                                style_as_list_view=True,
                                style_header={
                                    'backgroundColor': 'rgb(230, 230, 230)',
                                    'fontWeight': 'bold',
                                    'fontSize':16
                                },
                                style_table={
                                    'maxHeight': '55ex',
                                    'overflowY': 'scroll',
                                    'width': '100%'
                            },)
                        ],
                        className="four columns",
                    ),
                    html.Div(
                        id='trending_searches',
                        className='four columns',
                    ),
                    html.Div(
                        id='top_charts',
                        className='four columns',
                    ),
                ],
                className="twelve columns",
                style={"padding-left": "0"},
            ),
            # Row blank
            html.Div(
                [
                    html.H3(
                        children=''
                    )
                ],
                className="row",
            ),
            # Row 5
            html.Div(
                [
                    html.H3(
                        children='Trends Over Time',
                        style={'textAlign': 'center','backgroundColor':'#EBF5FB','font-weight': 'bold'}
                    )
                ],
                className="row",
            ),
            # Row 6
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H6('')
                                ],
                                className="one columns",
                            ),
                            html.Div(
                                [
                                    html.Button('Submit',id='submit_trends',n_clicks=0,style={'background-color':'gray','font-size':'14px','color':'#111'}),
                                ],
                                className="one columns",
                            ),
                            html.Div(
                                [
                                    html.H6('')
                                ],
                                className="one columns",
                            ),
                            html.Div(
                                [
                                    html.Label('Keyword List (comma-separated)'),
                                    dcc.Input(
                                        id='keyword_list',
                                        value='keto, elderberry',
                                        type='text'
                                    ),
                                ],
                                className="two columns",
                            ),
                            html.Div(
                                [
                                    html.H6('')
                                ],
                                className="one columns",
                            ),
                            html.Div(
                                [
                                    html.Label('Timeframe'),
                                    dcc.Dropdown(
                                        id='timeframe',
                                        options=[
                                            {'label': '5-year', 'value': 'today 5-y'},
                                            {'label': '1-year', 'value': 'today 12-m'},
                                            {'label': '3-month', 'value': 'today 3-m'},
                                            {'label': '1-month', 'value': 'today 1-m'},
                                            {'label': '7-day', 'value': 'now 7-d'},
                                            {'label': '1-day', 'value': 'now 1-d'}
                                        ],
                                        value='today 5-y'
                                    ),
                                ],
                                className="two columns",
                            ),
                            html.Div(
                                [
                                    html.H6('')
                                ],
                                className="one columns",
                            ),
                            html.Div(
                                [
                                    html.Label('Geography'),
                                    dcc.Dropdown(
                                        id='geo',
                                        options=[
                                            {'label': 'Global', 'value': 'World'},
                                            {'label': 'United States', 'value': 'US'},
                                            {'label': 'England', 'value': 'GB'},
                                            {'label': 'Canada', 'value': 'CA'},
                                            {'label': 'Australia', 'value': 'AU'},
                                            {'label': 'Italy', 'value': 'IT'},
                                            {'label': 'Ireland', 'value': 'IE'},
                                            {'label': 'Sweden', 'value': 'SE'},
                                            {'label': 'Germany', 'value': 'DE'},
                                            {'label': 'India', 'value': 'IN'},
                                            {'label': 'Indonesia', 'value': 'ID'},
                                            {'label': 'Brazil', 'value': 'BR'},
                                            {'label': 'Japan', 'value': 'JP'}
                                        ],
                                        value='World'
                                    ),
                                ],
                                className="two columns",
                            ),
                            html.Div(
                                [
                                    html.H6('')
                                ],
                                className="one columns",
                            ),
                        ],
                        className="twelve columns",
                    ),
                ],
                # style = dict(justifyContent="center"),
                className="row",
            ),
            # Row 7
            html.Div(
                [
                    html.Div(
                        [
                            dcc.Graph(id='trends_over_time')
                        ],
                        className="eight columns",
                    ),
                    html.Div(
                        [
                            dcc.Graph(id='keyword_correlations')
                        ],
                        className="four columns",
                    ),
                ],
                className="twelve columns",
                style={"padding-left": "0"},
            ),
            # Row 8
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H6('')
                                ],
                                className="one columns",
                            ),
                            html.Div(
                                [
                                    html.Button('Submit',id='submit_regional_trends',n_clicks=0,style={'background-color':'gray','font-size':'14px','color':'#111'}),
                                ],
                                className="one columns",
                            ),
                            html.Div(
                                [
                                    html.Label('Keyword (enter single word)'),
                                    dcc.Input(
                                        id='keyword',
                                        value='keto',
                                        type='text'
                                    ),
                                ],
                                className="two columns",
                            ),
                            html.Div(
                                [
                                    html.Label('Scope'),
                                    dcc.Dropdown(
                                        id='regional_scope',
                                        options=[
                                            {'label': 'Country', 'value': 'COUNTRY'},
                                            {'label': 'City', 'value': 'DMA'}
                                        ],
                                        value='COUNTRY'
                                    ),
                                ],
                                className="two columns",
                            ),
                            html.Div(
                                [
                                    html.H6('')
                                ],
                                className="one columns",
                            ),
                            html.Div(
                                [
                                    html.Label('Show'),
                                    dcc.Dropdown(
                                        id='show_style',
                                        options=[
                                            {'label': 'Top', 'value': 'top'},
                                            {'label': 'Bottom', 'value': 'bottom'},
                                            {'label': 'All', 'value': 'all'}
                                        ],
                                        value='top'
                                    ),
                                ],
                                className="two columns",
                            ),
                            html.Div(
                                [
                                    html.Label('Amount'),
                                    dcc.Slider(
                                        id='show_amount',
                                        min=1,
                                        max=50,
                                        step=None,
                                        marks={
                                            1: '1',
                                            5: '5',
                                            10: '10',
                                            25: '25',
                                            50: '50'
                                        },
                                        value=5
                                    ),
                                ],
                                className="two columns",
                            ),
                        ],
                        className="twelve columns",
                    ),
                ],
                # style = dict(justifyContent="center"),
                className="row",
            ),
            # Row 9
            html.Div(
                [
                    html.Div(
                        [
                            dcc.Graph(id='regional_trends')
                        ],
                        className="twelve columns",
                    ),
                ],
                className="twelve columns",
                style={"padding-left": "0"},
            ),
            # Row 10
            html.Div(
                [
                    html.H3(
                        children='Related Keywords',
                        style={'textAlign': 'center','backgroundColor':'#EBF5FB','font-weight': 'bold'}
                    )
                ],
                className="row",
            ),
            # Row 11
            html.Div(
                [
                    html.Div(
                        id='related_top',
                        className="five columns",
                    ),
                    html.Div(
                        id='related_rising',
                        className="five columns",
                    ),
                ],
                className='ten columns offset-by-two',
            ),
        ],
        className="row",
        # style={'backgroundColor':'#F4F6F6'},
    )

@app.callback(
    Output('trending_searches','children'),
    [Input('trending_searches_country','value')])
def get_trending_searches(country):
    df_trending_searches = pytrend.trending_searches(pn=country)
    df_trending_searches.rename(columns={0:'Trending Terms Today'}, inplace=True)
    return html.Div([
			dash_table.DataTable(
				id='table',
				columns=[{"name": str(i), "id": str(i)} for i in df_trending_searches.columns],
				data=df_trending_searches.to_dict("rows"),
				style_cell={
                    'width': '300px',
                    'height': '60px',
                    'textAlign': 'center'
                },
                style_data_conditional=[{
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                }],
                style_as_list_view=True,
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold',
                    'fontSize':16
                },
                style_table={
                    'maxHeight': '55ex',
                    'overflowY': 'scroll',
                    'width': '100%'
                },)
			])

@app.callback(
    Output('top_charts','children'),
    [Input('top_charts_year','value'),
     Input('top_charts_country','value')])
def get_top_charts(year,country):
    df_top_charts = pytrend.top_charts(year,geo=country)
    df_top_charts.rename(columns={'title':'Trending Terms Yearly'}, inplace=True)
    df_top_charts.drop('exploreQuery', axis=1, inplace=True)
    return html.Div([
			dash_table.DataTable(
				id='table',
				columns=[{"name": str(i), "id": str(i)} for i in df_top_charts.columns],
				data=df_top_charts.to_dict("rows"),
				style_cell={
                    'width': '300px',
                    'height': '60px',
                    'textAlign': 'center'
                },
                style_data_conditional=[{
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                }],
                style_as_list_view=True,
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold',
                    'fontSize':16
                },
                style_table={
                    'maxHeight': '55ex',
                    'overflowY': 'scroll',
                    'width': '100%'
                },)
			])

@app.callback(
    [Output('trends_over_time','figure'),
     Output('keyword_correlations','figure')],
    [Input('submit_trends','n_clicks')],
    [State('keyword_list','value'),
     State('timeframe','value'),
     State('geo','value')])
def update_trends_and_corrs(n_clicks,kw_list,timeframe,geo):
    if n_clicks is not None:
        keywords = [a.strip() for a in kw_list.split(',')]
        df_trends = get_trends_over_time(keywords,timeframe,geo)
        df_corr = get_keyword_correlations(keywords,timeframe,geo)
        mylayout_trends = go.Layout(title="Google Search Trends - {}".format(geo), yaxis_title='Index Ranking')
        fig_trends = go.Figure(layout=mylayout_trends)
        for keyword in df_trends['keyword'].unique():
            fig_trends.add_scatter(x = df_trends[df_trends['keyword'] == keyword]['date'], y = df_trends[df_trends['keyword'] == keyword]['value'], name = keyword,
                            mode = 'lines')

        x = list(df_corr.columns)
        y = list(df_corr.columns)
        z = [list(df_corr[a].values) for a in df_corr]
        mylayout_corrs = go.Layout(title="Keyword Correlations")
        trace = go.Heatmap(
            x = x,
            y = y,
            z = z,
            type = 'heatmap',
            colorscale = 'Cividis_r',
            zmin = -1,
            zmax = 1
        )
        mydata = [trace]
        fig_corrs = go.Figure(data = mydata, layout = mylayout_corrs)

        return fig_trends, fig_corrs

@app.callback(
    Output('regional_trends','figure'),
    [Input('submit_regional_trends','n_clicks')],
    [State('keyword','value'),
     State('timeframe','value'),
     State('geo','value'),
     State('regional_scope','value'),
     State('show_style','value'),
     State('show_amount','value')])
def update_regional_trends(n_clicks, keyword, timeframe, geo, resolution, show, amount):
    if n_clicks is not None:
        df_regional = get_regional_trends([keyword], timeframe, geo, resolution)
        fig_regional = plot_regional_trends(df_regional, keyword, show, amount)

        return fig_regional

@app.callback(
    Output('related_top','children'),
    [Input('submit_regional_trends','n_clicks')],
    [State('keyword','value'),
     State('timeframe','value'),
     State('geo','value')])
def update_related_kw_top(n_clicks, keyword, timeframe, geo, metric = 'top'):
    if n_clicks is not None:
        df_related_kw_top = get_related_keywords(keyword, timeframe, geo)
        df_related_kw_top.rename(columns={'query':'Top Related Keywords','value':'Index Ranking'}, inplace=True)
        return html.Div([
                dash_table.DataTable(
                    id='related_table',
                    columns=[{"name": str(i), "id": str(i)} for i in df_related_kw_top.columns],
                    data=df_related_kw_top.to_dict("rows"),
                    style_cell={
                        'width': '300px',
                        'height': '60px',
                        'textAlign': 'center'
                    },
                    style_data_conditional=[{
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                    }],
                    style_as_list_view=True,
                    style_header={
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'fontWeight': 'bold',
                        'fontSize':16
                    },
                    style_table={
                        'maxHeight': '55ex',
                        'overflowY': 'scroll',
                        'width': '100%'
                    },)
                ])

@app.callback(
    Output('related_rising','children'),
    [Input('submit_regional_trends','n_clicks')],
    [State('keyword','value'),
     State('timeframe','value'),
     State('geo','value')])
def update_related_kw_rising(n_clicks, keyword, timeframe, geo, metric = 'rising'):
    if n_clicks is not None:
        df_related_kw_top = get_related_keywords(keyword, timeframe, geo, metric)
        df_related_kw_top.rename(columns={'query':'Rising Related Keywords','value':'Index Ranking'}, inplace=True)
        return html.Div([
                dash_table.DataTable(
                    id='related_table',
                    columns=[{"name": str(i), "id": str(i)} for i in df_related_kw_top.columns],
                    data=df_related_kw_top.to_dict("rows"),
                    style_cell={
                        'width': '300px',
                        'height': '60px',
                        'textAlign': 'center'
                    },
                    style_data_conditional=[{
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                    }],
                    style_as_list_view=True,
                    style_header={
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'fontWeight': 'bold',
                        'fontSize':16
                    },
                    style_table={
                        'maxHeight': '55ex',
                        'overflowY': 'scroll',
                        'width': '100%'
                    },)
                ])

if __name__ == '__main__':

    app.run_server(debug=True)