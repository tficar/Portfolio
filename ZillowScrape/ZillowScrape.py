#!/usr/bin/env python
# coding: utf-8

# In[87]:


import requests
import math
import re
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import datetime
import json
import datetime as dt
import geopy.distance
import pymysql
from sqlalchemy import create_engine


# In[88]:


# create sqlalchemy engine
user = 'tficar'
pw = 'T2tdog1313!'
db = 'test_db'

engine = create_engine(f"mysql+pymysql://{user}:{pw}@localhost/{db}")


# In[101]:


headers = {'user-agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "DNT": "1", "Connection": "close", "Upgrade-Insecure-Requests": "1"}
# headers = {'user-agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "DNT": "1", "Connection": "close", "Upgrade-Insecure-Requests": "1"}
# headers = {
#     'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
#     'referrer': 'https://google.com',
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
#     'Accept-Encoding': 'gzip, deflate, br',
#     'Accept-Language': 'en-US,en;q=0.9',
#     'Pragma': 'no-cache',
# }
current_time = dt.datetime.now().strftime('%Y%m%d')
downtown_stpete_coord = (27.773849, -82.634747)

# Below url is for a specifically drawn range in St Pete
# Each url is for a different page of results. Only grabbing first 10 pages
zillow_url_stpete_pg1 = 'https://www.zillow.com/homes/for_sale/house_type/2-_beds/2.0-_baths/2_p/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3A%2233704%22%2C%22mapBounds%22%3A%7B%22west%22%3A-82.83671780670538%2C%22east%22%3A-82.56686612213507%2C%22south%22%3A27.703815042550914%2C%22north%22%3A27.90333710146889%7D%2C%22mapZoom%22%3A12%2C%22isMapVisible%22%3Atrue%2C%22customRegionId%22%3A%22cb7fc5ee82X1-CR1wn9oxtm7nsse_xmttn%22%2C%22filterState%22%3A%7B%22price%22%3A%7B%22max%22%3A425000%2C%22min%22%3A120000%7D%2C%22beds%22%3A%7B%22min%22%3A2%7D%2C%22baths%22%3A%7B%22min%22%3A2%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A1537%2C%22min%22%3A434%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%7D'
zillow_url_stpete_pg2 = 'https://www.zillow.com/homes/for_sale/house_type/2-_beds/2.0-_baths/2_p/?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage%22%3A2%7D%2C%22usersSearchTerm%22%3A%2233704%22%2C%22mapBounds%22%3A%7B%22west%22%3A-82.83671780670538%2C%22east%22%3A-82.56686612213507%2C%22south%22%3A27.703815042550914%2C%22north%22%3A27.90333710146889%7D%2C%22mapZoom%22%3A12%2C%22isMapVisible%22%3Atrue%2C%22customRegionId%22%3A%22cb7fc5ee82X1-CR1wn9oxtm7nsse_xmttn%22%2C%22filterState%22%3A%7B%22price%22%3A%7B%22max%22%3A425000%2C%22min%22%3A120000%7D%2C%22beds%22%3A%7B%22min%22%3A2%7D%2C%22baths%22%3A%7B%22min%22%3A2%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A1537%2C%22min%22%3A434%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%7D'
zillow_url_stpete_pg3 = 'https://www.zillow.com/homes/for_sale/house_type/2-_beds/2.0-_baths/2_p/?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage%22%3A3%7D%2C%22usersSearchTerm%22%3A%2233704%22%2C%22mapBounds%22%3A%7B%22west%22%3A-82.83671780670538%2C%22east%22%3A-82.56686612213507%2C%22south%22%3A27.703815042550914%2C%22north%22%3A27.90333710146889%7D%2C%22mapZoom%22%3A12%2C%22isMapVisible%22%3Atrue%2C%22customRegionId%22%3A%22cb7fc5ee82X1-CR1wn9oxtm7nsse_xmttn%22%2C%22filterState%22%3A%7B%22price%22%3A%7B%22max%22%3A425000%2C%22min%22%3A120000%7D%2C%22beds%22%3A%7B%22min%22%3A2%7D%2C%22baths%22%3A%7B%22min%22%3A2%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A1537%2C%22min%22%3A434%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%7D'
zillow_url_stpete_pg4 = 'https://www.zillow.com/homes/for_sale/house_type/2-_beds/2.0-_baths/2_p/?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage%22%3A4%7D%2C%22usersSearchTerm%22%3A%2233704%22%2C%22mapBounds%22%3A%7B%22west%22%3A-82.83671780670538%2C%22east%22%3A-82.56686612213507%2C%22south%22%3A27.703815042550914%2C%22north%22%3A27.90333710146889%7D%2C%22mapZoom%22%3A12%2C%22isMapVisible%22%3Atrue%2C%22customRegionId%22%3A%22cb7fc5ee82X1-CR1wn9oxtm7nsse_xmttn%22%2C%22filterState%22%3A%7B%22price%22%3A%7B%22max%22%3A425000%2C%22min%22%3A120000%7D%2C%22beds%22%3A%7B%22min%22%3A2%7D%2C%22baths%22%3A%7B%22min%22%3A2%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A1537%2C%22min%22%3A434%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%7D'
zillow_url_stpete_pg5 = 'https://www.zillow.com/homes/for_sale/house_type/2-_beds/2.0-_baths/2_p/?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage%22%3A5%7D%2C%22usersSearchTerm%22%3A%2233704%22%2C%22mapBounds%22%3A%7B%22west%22%3A-82.83671780670538%2C%22east%22%3A-82.56686612213507%2C%22south%22%3A27.703815042550914%2C%22north%22%3A27.90333710146889%7D%2C%22mapZoom%22%3A12%2C%22isMapVisible%22%3Atrue%2C%22customRegionId%22%3A%22cb7fc5ee82X1-CR1wn9oxtm7nsse_xmttn%22%2C%22filterState%22%3A%7B%22price%22%3A%7B%22max%22%3A425000%2C%22min%22%3A120000%7D%2C%22beds%22%3A%7B%22min%22%3A2%7D%2C%22baths%22%3A%7B%22min%22%3A2%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A1537%2C%22min%22%3A434%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%7D'
zillow_url_stpete_pg6 = 'https://www.zillow.com/homes/for_sale/house_type/2-_beds/2.0-_baths/2_p/?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage%22%3A6%7D%2C%22usersSearchTerm%22%3A%2233704%22%2C%22mapBounds%22%3A%7B%22west%22%3A-82.83671780670538%2C%22east%22%3A-82.56686612213507%2C%22south%22%3A27.703815042550914%2C%22north%22%3A27.90333710146889%7D%2C%22mapZoom%22%3A12%2C%22isMapVisible%22%3Atrue%2C%22customRegionId%22%3A%22cb7fc5ee82X1-CR1wn9oxtm7nsse_xmttn%22%2C%22filterState%22%3A%7B%22price%22%3A%7B%22max%22%3A425000%2C%22min%22%3A120000%7D%2C%22beds%22%3A%7B%22min%22%3A2%7D%2C%22baths%22%3A%7B%22min%22%3A2%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A1537%2C%22min%22%3A434%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%7D'
zillow_url_stpete_pg7 = 'https://www.zillow.com/homes/for_sale/house_type/2-_beds/2.0-_baths/2_p/?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage%22%3A7%7D%2C%22usersSearchTerm%22%3A%2233704%22%2C%22mapBounds%22%3A%7B%22west%22%3A-82.83671780670538%2C%22east%22%3A-82.56686612213507%2C%22south%22%3A27.703815042550914%2C%22north%22%3A27.90333710146889%7D%2C%22mapZoom%22%3A12%2C%22isMapVisible%22%3Atrue%2C%22customRegionId%22%3A%22cb7fc5ee82X1-CR1wn9oxtm7nsse_xmttn%22%2C%22filterState%22%3A%7B%22price%22%3A%7B%22max%22%3A425000%2C%22min%22%3A120000%7D%2C%22beds%22%3A%7B%22min%22%3A2%7D%2C%22baths%22%3A%7B%22min%22%3A2%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A1537%2C%22min%22%3A434%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%7D'
zillow_url_stpete_pg8 = 'https://www.zillow.com/homes/for_sale/house_type/2-_beds/2.0-_baths/2_p/?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage%22%3A8%7D%2C%22usersSearchTerm%22%3A%2233704%22%2C%22mapBounds%22%3A%7B%22west%22%3A-82.83671780670538%2C%22east%22%3A-82.56686612213507%2C%22south%22%3A27.703815042550914%2C%22north%22%3A27.90333710146889%7D%2C%22mapZoom%22%3A12%2C%22isMapVisible%22%3Atrue%2C%22customRegionId%22%3A%22cb7fc5ee82X1-CR1wn9oxtm7nsse_xmttn%22%2C%22filterState%22%3A%7B%22price%22%3A%7B%22max%22%3A425000%2C%22min%22%3A120000%7D%2C%22beds%22%3A%7B%22min%22%3A2%7D%2C%22baths%22%3A%7B%22min%22%3A2%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A1537%2C%22min%22%3A434%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%7D'
zillow_url_stpete_pg9 = 'https://www.zillow.com/homes/for_sale/house_type/2-_beds/2.0-_baths/2_p/?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage%22%3A9%7D%2C%22usersSearchTerm%22%3A%2233704%22%2C%22mapBounds%22%3A%7B%22west%22%3A-82.83671780670538%2C%22east%22%3A-82.56686612213507%2C%22south%22%3A27.703815042550914%2C%22north%22%3A27.90333710146889%7D%2C%22mapZoom%22%3A12%2C%22isMapVisible%22%3Atrue%2C%22customRegionId%22%3A%22cb7fc5ee82X1-CR1wn9oxtm7nsse_xmttn%22%2C%22filterState%22%3A%7B%22price%22%3A%7B%22max%22%3A425000%2C%22min%22%3A120000%7D%2C%22beds%22%3A%7B%22min%22%3A2%7D%2C%22baths%22%3A%7B%22min%22%3A2%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A1537%2C%22min%22%3A434%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%7D'
zillow_url_stpete_pg10 = 'https://www.zillow.com/homes/for_sale/house_type/2-_beds/2.0-_baths/2_p/?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage%22%3A10%7D%2C%22usersSearchTerm%22%3A%2233704%22%2C%22mapBounds%22%3A%7B%22west%22%3A-82.83671780670538%2C%22east%22%3A-82.56686612213507%2C%22south%22%3A27.703815042550914%2C%22north%22%3A27.90333710146889%7D%2C%22mapZoom%22%3A12%2C%22isMapVisible%22%3Atrue%2C%22customRegionId%22%3A%22cb7fc5ee82X1-CR1wn9oxtm7nsse_xmttn%22%2C%22filterState%22%3A%7B%22price%22%3A%7B%22max%22%3A425000%2C%22min%22%3A120000%7D%2C%22beds%22%3A%7B%22min%22%3A2%7D%2C%22baths%22%3A%7B%22min%22%3A2%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A1537%2C%22min%22%3A434%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%7D'

zillow_url_stpete_allpages = [zillow_url_stpete_pg1,zillow_url_stpete_pg2,zillow_url_stpete_pg3,zillow_url_stpete_pg4,
                              zillow_url_stpete_pg5,zillow_url_stpete_pg6,zillow_url_stpete_pg7,zillow_url_stpete_pg8,
                              zillow_url_stpete_pg9,zillow_url_stpete_pg10]


# In[ ]:


def get_page_list(page1_url):
    
    '''Returns a list of the available zillow pages given the first page of the search'''
    
    result = requests.get(page1_url,headers=headers)
    soup = BeautifulSoup(result.text, 'html.parser')
    num_listings = int(re.sub('[^0-9]','',soup.find('span',class_='result-count').text))
    
    num_pages = math.ceil(num_listings/40)
    
    return zillow_url_stpete_allpages[:num_pages]


# In[112]:


def scrape_zillow_main(page_url):
    
    """Returns a data frame of zillow data given a url from the main search page"""
    
    lis = []
    lis2 = {}
    price = []
    sq_ft = []
    addr1 = []
    city = []
    state = []
    zipcode = []
    lat = []
    long = []
    url = []
    
    result = requests.get(page_url,headers=headers)
#     For debugging
#     print(result)
    
    soup = BeautifulSoup(result.text, 'html.parser')
    listings = soup.findAll('article', class_ = 'list-card list-card_not-saved')
    scripts = soup.findAll('script', attrs={'type': 'application/ld+json'})
    description = [a.text for a in soup.findAll('div',class_='list-card-type')]
    
    for listing in listings:

        price.append(re.sub('[^0-9]','',listing.find('div', class_ = 'list-card-price').text))
        
    for listing in listings:
        uls = listing.findAll('ul')

        for ul in uls:
            lis.append(ul.findAll('li'))

    for i,li in enumerate(lis):

        for r in range(0,3):

            try:
                lis2[str(i)+str(r)] = li[r].text
            except:
                lis2[str(i)+str(r)] = 'NA'

    lis2 = pd.DataFrame.from_dict(lis2, orient = 'index')
    lis2.rename(columns = {0:'stat'}, inplace = True)
    lis2.reset_index(inplace = True)
    lis2['index'] = [int(a[:-1]) for a in lis2['index']]
    
    
    beds = pd.DataFrame(range(0,len(listings)),columns = ['index']).merge(lis2[lis2['stat'].str.contains('bd.*')],
                                                                          on='index',how='left')
    beds['stat'] = [a if pd.isnull(a) else re.sub('[^0-9]','',a) for a in beds['stat']]
    beds.rename(columns = {'stat':'num_beds'}, inplace = True)
    baths = pd.DataFrame(range(0,len(listings)),columns = ['index']).merge(lis2[lis2['stat'].str.contains('ba.*')],
                                                                           on='index',how='left')
    baths['stat'] = [a if pd.isnull(a) else re.sub('[^0-9]','',a) for a in baths['stat']]
    baths.rename(columns = {'stat':'num_baths'}, inplace = True)

    for i in range(0,len(scripts)):

        # sq_ft
        try:
            sq_ft.append(int(re.sub('[^0-9]','',json.loads(scripts[i].string)['floorSize']['value'])))
        except:
            sq_ft.append('NA')

        # address info
        try:
            addr1.append(json.loads(scripts[i].string)['address']['streetAddress'].strip())
        except:
            addr1.append('NA')
        try:
            city.append(json.loads(scripts[i].string)['address']['addressLocality'].strip())
        except:
            city.append('NA')
        try:
            state.append(json.loads(scripts[i].string)['address']['addressRegion'].strip())
        except:
            state.append('NA')
        try:
            zipcode.append(json.loads(scripts[i].string)['address']['postalCode'].strip())
        except:
            zipcode.append('NA')

        # lat/long
        try:
            lat.append(json.loads(scripts[i].string)['geo']['latitude'])
        except:
            lat.append('NA')
        try:
            long.append(json.loads(scripts[i].string)['geo']['longitude'])
        except:
            long.append('NA')

        # url
        try:
            url.append(json.loads(scripts[i].string)['url'])
        except:
            url.append('NA')
            
    listings_to_drop = [i for i, j in enumerate(addr1) if j == 'NA']
    sq_ft = [i for j, i in enumerate(sq_ft) if j not in listings_to_drop]
    addr1 = [i for j, i in enumerate(addr1) if j not in listings_to_drop]
    city = [i for j, i in enumerate(city) if j not in listings_to_drop]
    state = [i for j, i in enumerate(state) if j not in listings_to_drop]
    zipcode = [i for j, i in enumerate(zipcode) if j not in listings_to_drop]
    lat = [i for j, i in enumerate(lat) if j not in listings_to_drop]
    long = [i for j, i in enumerate(long) if j not in listings_to_drop]
    url = [i for j, i in enumerate(url) if j not in listings_to_drop]
    
    df_listings = pd.DataFrame({'Description':description,'Street':addr1,'City':city,'State':state,'Zip':zipcode,
                                'Lat':lat,'Long':long,'Beds':beds['num_beds'],'Baths':baths['num_baths'],
                                'SqFt':sq_ft,'Price':price,'URL':url})
    
    return(df_listings)


# In[110]:


def scrape_zillow_details(url):
    
    """Returns a data frame of detailed Zillow data given a url for a specific listing"""
    
    result = requests.get(url,headers=headers)
    soup = BeautifulSoup(result.text, 'html.parser')
    
    cols = []
    vals = []
    
    try:
        cols.append(soup.findAll('div',class_=re.compile('^Text-aiai24-0.*'))[0].text)
    except:
        pass
    try:
        vals.append(soup.findAll('div',class_=re.compile('^Text-aiai24-0.*'))[1].text)
    except:
        pass
    try:
        cols.append(soup.findAll('div',class_=re.compile('^Text-aiai24-0.*'))[2].text)
    except:
        pass
    try:
        vals.append(soup.findAll('div',class_=re.compile('^Text-aiai24-0.*'))[3].text)
    except:
        pass
    try:
        cols.append(soup.findAll('div',class_=re.compile('^Text-aiai24-0.*'))[4].text)
    except:
        pass
    try:
        vals.append(soup.findAll('div',class_=re.compile('^Text-aiai24-0.*'))[5].text)
    except:
        pass
    cols.append('Home Description')
    try:
        vals.append(soup.findAll('div',class_='ds-overview-section')[0].text)
    except:
        vals.append(np.nan)
    # Cannot find payment data in returned html
#     cols.append('Est. Mortgage Payment')
#     try:
#         vals.append(soup.findAll('span',class_=re.compile('^sc-1i7l885-4.*'))[0].text)
#     except:
#         vals.append(np.nan)
    try:
        cols.append(soup.findAll('h4',class_=re.compile('^Text-aiai24-0 StyledHeading.*'))[4].text.split(':')[0].strip())
    except:
        try:
            cols.append(soup.findAll('h4',class_=re.compile('^Text-aiai24-0 StyledHeading.*'))[5].text.split(':')[0].strip())
        except:
            pass
    try:
        vals.append(soup.findAll('h4',class_=re.compile('^Text-aiai24-0 StyledHeading.*'))[4].text.split(':')[1].strip())
    except:
        try:
            vals.append(soup.findAll('h4',class_=re.compile('^Text-aiai24-0 StyledHeading.*'))[5].text.split(':')[1].strip())
        except:
            pass
    cols.append('Price/SqFt')
    try:
        vals.append(int(re.sub('[^0-9]','',soup.findAll('span',class_='ds-body ds-home-fact-value')[6].text)))
    except:
        vals.append(np.nan)
    
    for item in soup.findAll('span',class_=re.compile('Text-aiai24-0 c.*')): 

        cols.append(item.text.split(':')[0])
        try:
            vals.append(item.text.split(':')[1].strip())
        except:
            vals.append(np.nan)

    return(pd.DataFrame(vals,cols).T)


# In[114]:


def get_zillow_main(url_list):
    
    """Executes the scraping of the zillow main page for a given list of urls and returns a single dataframe"""
    
    all_listings = []

    for page_url in url_list:

        temp_df = scrape_zillow_main(page_url)
        all_listings.append(temp_df)

    df_listings_main = pd.concat(all_listings, ignore_index=True)
    
    return(df_listings_main)


# In[94]:


def get_zillow_details(df_listings_main):
    
    """Executes the scraping of the zillow detail page given the main df and returns a single dataframe"""
    
    list_df = []

    for url in df_listings_main['URL']:

        try:
            list_df.append(scrape_zillow_details(url))
        except:
            pass
        
    list_df = [a.loc[:,~a.columns.duplicated()] for a in list_df]
    df_listings_detail = pd.concat(list_df, axis = 0, ignore_index=True)
    
    return(df_listings_detail)


# In[95]:


def create_final_zillow_df(df_listings_detail,df_listings_main):
    
    """Return a single, final df given the detail and main zillow dfs"""
    
    keep_cols = ['Time on Zillow','Views','Saves','Sewer information','MLS ID','Property Type',
                 'Lot Features','Flood Zone Code','Subdivision Name','Bedrooms','Bathrooms','Full bathrooms',
                 '1/2 bathrooms','Basement','Flooring','Heating features','Cooling features','Appliances included',
                 'Parking features','Garage spaces','Levels','Stories','Private pool','Exterior features','Home Description',
                 'Lot size','Home type','Foundation','Roof','New construction','Year built','Major remodel year',
                 'Utilities for property','Sunscore','Region','Tax assessed value',
                 'Annual tax amount','Construction Materials','Pets Allowed','Other Structures']
    
    df_listings_detail = df_listings_detail[keep_cols]
    
    # To save a copy of each individual df, uncomment and execute below code
    # Mostly meant to save time while debugging
    # df_listings_main.to_csv('Output/Zillow/ZillowSummaryDataMom.csv')
    # df_listings_detail.to_csv('Output/Zillow/ZillowDetailDataMom.csv')
    
    # Load copy of saved dfs for debugging
    # df_listings_main = pd.read_csv('Output/Zillow/ZillowSummaryData.csv')
    # df_listings_detail = pd.read_csv('Output/Zillow/ZillowDetailData.csv')
    
    df_final = df_listings_main.merge(df_listings_detail, how='left', left_index=True, right_index=True)
    
    df_final['Distance from DTSP'] = [geopy.distance.distance(downtown_stpete_coord,x).mi for x in list(zip(list(df_final['Lat']),list(df_final['Long'])))]
    # Clean columns
    df_final.drop(df_final[df_final['Price'] == ''].index, inplace = True)
    df_final.drop(df_final[df_final['Price'].isna()].index, inplace = True)
    df_final.drop(df_final[df_final['Description'].isin(['Lot / Land for sale','Auction','Foreclosure','Foreclosed','Pre-foreclosure'])].index, inplace=True)
    try:
        df_final.drop(['Unnamed: 0_x','Unnamed: 0_y'], axis = 1, inplace = True)
    except:
        pass
    df_final['Price'] = df_final['Price'].astype('int')
    df_final['SqFt'].fillna(1200, inplace = True)
    df_final['SqFt'].replace('NA',1200, inplace = True)
    df_final['SqFt'] = df_final['SqFt'].astype('int')
    df_final['PricePerSqFt'] = df_final['Price']/df_final['SqFt']
    df_final['Beds'].fillna(0, inplace = True)
    df_final['Beds'].replace('',0, inplace = True)
    df_final['Beds'] = df_final['Beds'].astype('int')
    df_final['Baths'].fillna(0, inplace = True)
    df_final['Baths'].replace('',0, inplace = True)
    df_final['Baths'] = df_final['Baths'].astype('int')
    df_final['New construction'] = df_final['New construction'].map(dict(Yes=1,No=0))
    df_final['Pets Allowed'] = df_final['Pets Allowed'].map(dict(Yes=1,No=0))
    df_final['Time on Zillow'] = [1 if (len(re.findall('.hour.*',str(a))) > 0 or a == '--' or pd.isna(a) or a == 'nan') else int(re.sub('[^0-9]','',str(a))) for a in df_final['Time on Zillow']]
    df_final['Views'] = [0 if a == '--' or isinstance(a, float) else int(float(re.sub('[^0-9]','',a))) for a in df_final['Views']]
    df_final['Saves'] = [0 if a == '--' or isinstance(a, float) else int(a) for a in df_final['Saves']]
    df_final['Tax assessed value'] = [0 if isinstance(a,float) else int(float(re.sub('[^0-9]','',a))) for a in df_final['Tax assessed value']]
    df_final['Annual tax amount'] = [0 if isinstance(a,float) else int(float(re.sub('[^0-9]','',a))) for a in df_final['Annual tax amount']]
    df_final['Save Rate'] = df_final['Saves']/df_final['Views']
    df_final['ViewsPerDay'] = df_final['Views']/df_final['Time on Zillow']
    
    return(df_final)


# In[96]:


def save_zillow_output(df_final):
    
    """Saves output of final df to both MySQL and a .csv file"""
    
    listings_DTSP = df_final[(df_final['Price'] < 400000) & (df_final['Price'] > 50000) & (df_final['Distance from DTSP'] <= 1) & df_final['Pets Allowed'].isin([1,'NaN'])][['Description','Time on Zillow','Views','Saves','ViewsPerDay','Save Rate','Beds','Baths','SqFt','Price','PricePerSqFt','Annual tax amount','Street','City','State','Zip','Lat','Long','Distance from DTSP','Year built','Major remodel year','URL']]
    listings_pricerange = df_final[(df_final['Price'] < 400000) & (df_final['Price'] > 50000) & df_final['Pets Allowed'].isin([1,'NaN'])][['Description','Time on Zillow','Views','Saves','ViewsPerDay','Save Rate','Beds','Baths','SqFt','Price','PricePerSqFt','Annual tax amount','Street','City','State','Zip','Lat','Long','Distance from DTSP','Year built','Major remodel year','URL']]
    listings_all = df_final[df_final['Pets Allowed'].isin([1,'NaN'])][['Description','Time on Zillow','Views','Saves','ViewsPerDay','Save Rate','Beds','Baths','SqFt','Price','PricePerSqFt','Annual tax amount','Street','City','State','Zip','Lat','Long','Distance from DTSP','Year built','Major remodel year','URL']]
    
    listings_DTSP.to_sql('listings_dtsp',con = engine,if_exists = 'replace')
    listings_pricerange.to_sql('listings_pricerange',con = engine,if_exists = 'replace')
    listings_all.to_sql('listings_all',con = engine,if_exists = 'replace')
    print('Output saved to MySQL.')
    
    if datetime.date.today().weekday() == 6:
        listings_DTSP.to_csv(f'C:/Users/Tristan/Documents/Learning/Python/Output/Zillow/ZillowListingsDTSP_{current_time}.csv', index=False)
        listings_pricerange.to_csv(f'C:/Users/Tristan/Documents/Learning/Python/Output/Zillow/ZillowListingsPriceRange_{current_time}.csv', index=False)
        listings_all.to_csv(f'C:/Users/Tristan/Documents/Learning/Python/Output/Zillow/ZillowListingsAll_{current_time}.csv', index=False)
    else:
        listings_DTSP.to_csv('C:/Users/Tristan/Documents/Learning/Python/Output/Zillow/ZillowListingsDTSP.csv', index=False)
        listings_pricerange.to_csv('C:/Users/Tristan/Documents/Learning/Python/Output/Zillow/ZillowListingsPriceRange.csv', index=False)
        listings_all.to_csv('C:/Users/Tristan/Documents/Learning/Python/Output/Zillow/ZillowListingsAll.csv', index=False)
    print('Output saved to csv file.')


# In[ ]:


if __name__ == '__main__':
    
    page_list = get_page_list(zillow_url_stpete_pg1)
    main_df = get_zillow_main(page_list)
    detail_df = get_zillow_details(main_df)
    final_df = create_final_zillow_df(detail_df, main_df)
    save_zillow_output(final_df)


# In[ ]:




