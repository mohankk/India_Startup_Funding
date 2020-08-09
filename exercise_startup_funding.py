import pandas as pd
import numpy as np
import os
from bs4 import BeautifulSoup
from bs4.element import  Tag
import requests
import re
import pandas as pd
from datetime import datetime
from pandas import Series,DataFrame
from matplotlib import pyplot as plt

''' == pattern for searching == 
https://trak.in/india-startup-funding-investment-2015/january-2017/ '''
'''Since september-2015 is not meeting search criteria
<h3><a href="https://trak.in/india-startup-funding-investment-2015/september-2015/" data-wpel-link="internal">
Funding Data for September 2015</a> (88 Deals)</h3>'''

''' 
1.Some data manually added when beautifulsoup cannot read it right 
July 2015 36-45rows  were missing
2. cleaned up some rows from csv which had html tag. 
3. manual cleanup of some extra rows which had only data for few columns 1 or 2
4. Bengaluru vs bangalore,  gurugram vs gurgoan, new delhi - delhi
5. Date format conversions could be painful ex some has 03/02/2012(dd/mm/yyyy) and some you see 1/12/2013 or 21/4/2016
'''


col_nm = ['Sr. No.', 'Date', 'Startup Name', 'Industry / Vertical', 'Sub-Vertical', 'City / Location', 'Investors’ Name', 'Investment Type', 'Amount (In USD)']
data = []
col_set = [[] for i in range(9)]

# Reading html data from below url using request and beautiful soup
url = 'https://trak.in/india-startup-funding-investment-2015/'
result = requests.get(url)
c = result.content
soup = BeautifulSoup(c, 'html.parser')
# html table class = tablepress and there are 47 tables all together in  the above link
summary = soup.find_all('table', {'class': 'tablepress', 'id': ["tablepress-".__add__(str(x)) for x in range(48)]})
rows = soup.find_all('tr')

for tr in rows:
    cols = tr.find_all('td')
    for index, td in enumerate(cols):
        # For some tables(not all) we have 'remarks' column, which i am ignoring.
        if index > 8:
            break
        # Some tables are inconsistent with html table structure so had to use td.next_element to get text of td
        text = td.find(text=True) or td.next_element
        col_set[index].append(text)
        data.append(text)

# Method written to read data from embedded links in main page. half of 2018 and all of 2017,2016,2015 data are in seperate links
def data_from_emb_links(tbl_url):
    results = requests.get(tbl_url)
    content = results.content
    sup = BeautifulSoup(content, 'html.parser')
    tble = sup.find_all('table')
    rws = sup.find_all('tr')
    col_names_frm_links = get_table_col_size(tble[0])
    for trw in rws:
        col = trw.findAll('td')
        for idx, tdt in enumerate(col):
            if idx > 8:
                break
            texts = tdt.find(text=True)
            #Some tables does not have values for certain columns and some tables has less no of coloums
            # This code make sures that data is populated with default data
            if col_names_frm_links == col_nm:
                if len(col) < 9 and idx is len(col)-1:
                    if col[idx-1].find(text=True) is not None and len(col) is 7:
                        col_set[idx].append(texts)
                        col_set[idx+1].append('N/A')
                        col_set[idx+2].append('N/A')
                    else:
                        col_set[idx].append(texts)
                        col_set[idx + 1].append('')
                else:
                    col_set[idx].append(texts)
            # some tables does not have sub-vertical column, populating value with vertical name
            elif set(col_nm) - set(col_names_frm_links) == set(['Sub-Vertical']):
                if idx == 4:
                    col_set[idx].append(col[idx-1].find(text=True))
                    col_set[idx+1].append(texts)
                elif 4 < idx < 8:
                    col_set[idx+1].append(texts)
                elif idx >= 8:
                    break
                else:
                    col_set[idx].append(texts)
            #Some tables does not have three columns so have populated them with same value as column name
            elif set(col_nm) - set(col_names_frm_links) == set(['Sub-Vertical', 'Industry / Vertical', 'City / Location']):
                if idx in [3, 4, 5]:
                    col_set[idx].append(col_nm[idx])
                    col_set[idx+3].append(texts)
                elif idx >= 6:
                    continue
                else:
                    col_set[idx].append(texts)

#Some tables have inconsistent columns names, making consistent across all tables.
def get_table_col_size(table):
    data_array = []
    if len(table.findAll('th')) > 0:
        col = table.findAll('th')
    else:
        rws = table.findAll('tr')
        col = rws[0].findAll('td')
    for idx, tdt in enumerate(col):
        texts = tdt.find(text=True)
        if texts in ['Industry Vertical', 'Industry / Vertical', 'Industry/ Vertical']:
            data_array.append('Industry / Vertical')
        elif texts in ['Date (dd/mm/yyyy)', 'Date\xa0 (dd/mm/yyyy)']:
            data_array.append('Date')
        elif texts in ['Invest-ment', 'Investment']:
            data_array.append('Investment Type')
        elif texts == 'Amount (in USD)':
            data_array.append('Amount (In USD)')
        elif texts == "Investors' Name":
            data_array.append('Investors’ Name')
        else:
            data_array.append(str(texts).strip())
    return data_array


# Reading embedded links in the main page(data for 2015, 2016, 2017 partly 2018).
href_data = soup.find_all('a', {'data-wpel-link':'internal', 'rel':'noopener noreferrer'})
links_data = []
for tag in href_data:
    link = tag.get('href')
    links_data.append(link)

#For easy cross validation of data manually, i wrote below line
set_links = sorted(set(links_data), key=links_data.index)

# Only sep 2015 link has special pattern so appending here.
set_links.insert(len(links_data)-3, 'https://trak.in/india-startup-funding-investment-2015/september-2015/')
for ix, urL in enumerate(set_links):
    data_from_emb_links(urL)

# Preparing Dataframe from series of columns
df = pd.concat([pd.Series(col_data) for col_data in col_set], axis=1)
df.columns = col_nm

# Data cleaning.
df.dropna(how='all', axis=0, inplace=True)
df.drop_duplicates(keep='first', inplace=True)
df.drop(df[df['Sr. No.'] == 'Sr. No.'].index, inplace=True)
df.drop(df[df['Sr. No.'] == 'Sr. No.'].index, inplace=True)
print(df.shape)
df.to_csv('startup_funding.csv')

#df = pd.read_csv('startup_funding_gen.csv')

df['Date'].replace('22/01//2015', '22/01/2015', inplace=True)
df['Date'].replace('13/04.2015', '13/04/2015', inplace=True)
df['Date'].replace('01/07/015', '01/07/2015', inplace=True)
df['Date'].replace('15/01.2015', '15/01/2015', inplace=True)
df['Date'].replace('12/05.2015', '12/05/2015', inplace=True)
df['Date'].replace('05/072018', '05/07/2018', inplace=True)

# Replacing data
df['City / Location'].replace('Bangalore', 'Bengaluru', inplace=True)
df['City / Location'].replace('Gurgaon', 'Gurugram', inplace=True)
df['City / Location'].replace('New Delhi', 'Delhi', inplace=True)
df['Industry / Vertical'].replace(['ecommerce', 'ECommerce', 'E-Commerce', 'E-commerce', 'Ecommerce', 'eCommerce'], 'ECommerce', inplace=True)


#There is still some junk data, it is easy to clean it manually than write code to clean. hint: sort data by any date column
#Some dates are not inline with standard dd/mm/yyyy pattern, below is attempt to fix it.
# df.Date = df.Date[1:].apply(lambda x: datetime.strptime(x, "%d/%m/%Y").strftime("%d/%m/%Y"))
# df.Date = pd.to_datetime(df.Date, infer_datetime_format=True)
#
# #Plotting funding per year
# df.Date.dt.year.value_counts().sort_index().plot(kind='bar')
# plt.xlabel('Year')
# plt.ylabel('Count')
# plt.title('Startups Funded Per Year')
#
# #Plotting funding per month
# ser = df.Date.groupby([df.Date.dt.year, df.Date.dt.month]).count().unstack(level=-1)
# ser.columns = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
# ser.plot(kind='bar', stacked=True, figsize=(15,8), legend='reverse');
#
# # #Removing missing values and plotting rest of  the data
# df['Industry / Vertical'].value_counts()[:3].append(df['Industry / Vertical'].value_counts()[4:10]).plot(kind='pie', figsize=(8,8))
#
# # #Removing missing values and plotting rest of  the data
# City_Count = df['City / Location'].value_counts()
# City_Count[:4].append(City_Count[5:16]).plot(kind='barh', fontsize=12, figsize=(12,8))
#
# plt.show()

