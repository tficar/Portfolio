#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from dateutil.parser import parse

headers = {'user-agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "DNT": "1", "Connection": "close", "Upgrade-Insecure-Requests": "1"}
url = 'https://inciweb.nwcg.gov/accessible-view/'

# Used for looping through incident specific urls
root_url = 'https://inciweb.nwcg.gov'

def get_incident_urls(url):
    
    '''Returns a df of all incidents and their urls from inciweb.nwcg.gov'''
    
    result = requests.get(url,headers=headers)
    soup = BeautifulSoup(result.text, 'html.parser')
    
    # Grab incident table view html
    table_html = soup.find('table')
    
    # Get info for all hyperlinks
    hrefs_html = []
    for href_html in table_html.findAll('a', attrs={'href':re.compile("/incident/")}):
        hrefs_html.append(href_html)
        
    # Get type. We will exclude non-fire ones later
    types = [a.text for a in table_html.findAll('td', headers='unit')]
        
    # Parse html for name and url
    hrefs = []
    names = []
    for a in hrefs_html:
        hrefs.append(a['href'])
        names.append(a.text)
        
    incident_urls = [''.join([root_url,href]) for href in hrefs]
    
    # Create final df to return
    df = pd.DataFrame([names,types,hrefs,incident_urls]).transpose()
    df.columns = ['Incident_Name','Type','Incident_URL','Full_URL']
    df = df[df['Type'] == 'Wildfire']
    df.drop('Type', axis=1, inplace=True)
    
    return df

def get_incident_info(url):
    
    '''Returns specific info from inciweb.nwcg.gov for a given url'''
    
    result = requests.get(url,headers=headers)
    soup = BeautifulSoup(result.text, 'html.parser')
    
    # Get html tables needed
    incident_info_tables = []
    for table in soup.findAll('table'):
        incident_info_tables.append(table)

    # Split resulting html into column names and values
    # Only parsing the first 2 tables found
    cols_a = [a.text for i,a in enumerate(incident_info_tables[0].findAll('td')) if i % 2 == 0]
    vals_a = [a.text for i,a in enumerate(incident_info_tables[0].findAll('td')) if i % 2 != 0]
    df_a = pd.DataFrame(data=vals_a).transpose()
    df_a.columns = cols_a
    
    cols_b = []
    try:
        for i,a in enumerate(incident_info_tables[1].findAll('td')):
            if i % 2 == 0:
                cols_b.append(a.text)
    except:
        print('Missing table 2.')
    
    vals_b = []
    try:
        for i,a in enumerate(incident_info_tables[1].findAll('td')):
            if i % 2 != 0:
                vals_b.append(a.text)
    except:
        print('Missing table 2.')
        
    df_b = pd.DataFrame(data=vals_b).transpose()
    df_b.columns = cols_b
    
    df = pd.concat([df_a,df_b], axis=1)
    
    return df

def clean_df(df):
    
    '''Returns a cleaned version of the df created by the get_incident_info function'''
    
    df['Current as of'] = [parse(a.split('"')[1]).date() for a in df['Current as of']]
    df['Date of Origin'] = [parse(' '.join(a.split()[1:4] + a[3].split()[5:7])) if isinstance(a, str) else a for a in df['Date of Origin']]
    df['Estimated Containment Date'] = [parse(' '.join(a.split()[1:4] + a[3].split()[5:7])) if isinstance(a, str) else a for a in df['Estimated Containment Date']]
    df['Coordinates'] = [a.split()[0] + ', ' + a.split()[2] for a in df['Coordinates']]
    df['Total Personnel'] = [re.sub("[^0-9]", "", a) if isinstance(a, str) else a for a in df['Total Personnel']]
    df['Size'] = [re.sub("[^0-9]", "", a) if isinstance(a, str) else a for a in df['Size']]
    df.rename(columns={'Size':'Size (Acres)'}, inplace=True)
    df['Percent of Perimeter Contained'] = [int(re.sub("%", "", a))/100 if isinstance(a, str) else a for a in df['Percent of Perimeter Contained']]
    
    return df

if __name__ == '__main__':
    
    df_url = get_incident_urls(url)
    
    df_list = []
    
    for u in df_url['Full_URL']:
        df_list.append(get_incident_info(u))
        
    df = pd.concat(df_list)
    df = clean_df(df)
    df_final = pd.concat([df_url.reset_index(drop=True),df.reset_index(drop=True)], axis=1)
    cols_final = ['Incident_Name','Incident Type','Cause', 'Location','Coordinates', 'Incident Commander', 'Total Personnel',
                  'Size (Acres)','Percent of Perimeter Contained','Fuels Involved', 'Significant Events','Date of Origin',
                  'Estimated Containment Date', 'Current as of','Incident Description', 'Planned Actions', 'Remarks',
                  'Incident_URL', 'Full_URL']
    df_final = df_final[cols_final]
    
    # Make smaller summary table
    cols_summary = ['Incident_Name', 'Size (Acres)', 'Percent of Perimeter Contained', 'Coordinates', 'Full_URL', 'Current as of']
    df_summary = df_final[cols_summary]
    
    # Save results
    writer = pd.ExcelWriter(r'C:\Users\tristan\Documents\Learning\Python\Output\InciwebResults.xlsx')
    workbook = writer.book
    df_summary.to_excel(excel_writer = writer, header=True, sheet_name='Summary', index=False)
    df_final.to_excel(excel_writer = writer, header=True, sheet_name='All_Cols', index=False)
    writer.save()
    writer.close()

