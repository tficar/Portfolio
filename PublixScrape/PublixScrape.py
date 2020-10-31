#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import os
import selenium
from selenium import webdriver
import time
import io
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os.path

url = 'https://www.publix.com/savings/weekly-ad/bogo'

def get_bogo_html():
    
    '''Uses a selenium driver to navigate the publix site, select a store, and returns the html of the bogo page'''
    
    #Install driver
    opts=webdriver.ChromeOptions()
    opts.headless=True
    driver = webdriver.Chrome(ChromeDriverManager().install() ,options=opts)
    
    # Load page
    driver.get(url)
    # Click Find a Store button
    driver.find_element_by_xpath('/html/body/div[1]/div/section/div[3]/div[2]/div/div/button').click()
    # Enter zip
    driver.find_element_by_xpath('//*[@id="input_ZIPorCity,Stateorstorenumber97"]').send_keys('33716')
    # Click search
    driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div/div[2]/div[1]/form/div[1]/button').click()
    time.sleep(3)
    # Click first result, which is the Gateway Crossings location
    driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div/div[2]/div[2]/div/ul/li[1]/div/button').click()
    time.sleep(10)
    # Click the load more button
    driver.find_element_by_xpath('/html/body/div[1]/div/section/div[3]/div[2]/div[2]/div[3]/button').click()
    time.sleep(1)
    # Return html
    bogo_html = driver.page_source
    bogo_html = BeautifulSoup(bogo_html, 'html.parser')
    return bogo_html

def extract_bogo_info(bogos_html):
    
    '''Given the html webpage of bogos, iterates through all of them and extracts basic info to return a df'''
    
    bogos = bogos_html.find('ul', class_ = 'card-list').find_all('li')
    products = []
    savings = []
    valids = []
    for bogo in bogos:
        try:
            products.append(bogo.find('div', class_ = 'text-block-primary card-title clamp-2').text)
        except AttributeError:
            products.append('')
        try:
            savings.append(float(re.findall('\d+\.\d+', bogo.find('div', class_ = 'deal-info').text)[0]))
        except:
            savings.append('')
        try:
            valids.append(bogo.find('div', class_ = 'validity text-block-default').text)
        except:
            valids.append('')
            
    df_bogos = pd.DataFrame([products,savings,valids]).T
    df_bogos.columns = ['Product','Savings','SaleDate']
    df_bogos = df_bogos[df_bogos['Product'] != '']
    return df_bogos

def send_email(email_recipient,
               email_subject,
               email_message,
               attachment_location = ''):

    email_sender = 'youremail@email.com'

    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = email_recipient
    msg['Subject'] = email_subject

    msg.attach(MIMEText(email_message, 'html'))

    if attachment_location != '':
        filename = os.path.basename(attachment_location)
        attachment = open(attachment_location, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        "attachment; filename= %s" % filename)
        msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login('youremail@email.com', 'your_password')
    text = msg.as_string()
    server.sendmail(email_sender, email_recipient, text)
    print('email sent')
    server.quit()
    return

if __name__ == '__main__':
    
    bogo_html = get_bogo_html()
    bogo_df = extract_bogo_info(bogo_html)
    wine_df = bogo_df[bogo_df['Product'].str.contains('Wine')]
    ice_cream_df = bogo_df[bogo_df['Product'].str.contains('Ice Cream')]
    newman_sale = len(bogo_df[bogo_df['Product'].str.contains('Newmans Own Pizza')].index) > 0
    cous_sale = len(bogo_df[bogo_df['Product'].str.contains('Near East Couscous')].index) > 0
    email_df = pd.concat([wine_df,ice_cream_df])
    email_body = """    <html>
      <head></head>
      <body>
        {0}
      </body>
    </html>
    """.format(email_df.to_html())
    if newman_sale:
        email_body = email_body + '\n\n***NEWMAN IS ON SALE***'
    if cous_sale:
        email_body = email_body + '\n\n***COUSCOUS IS ON SALE***'
    send_email('tficar@yahoo.com','BOGO Wines & Newman',email_body)

