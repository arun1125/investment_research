import re
from pickle import dump
import requests
from bs4 import BeautifulSoup
import bs4
import pandas as pd

class secscraper:
    def __init__(self):
        self.cik_url = 'http://www.sec.gov/cgi-bin/browse-edgar?CIK={}&Find=Search&owner=exclude&action=getcompany'
        self.CIK_RE = re.compile(r'.*CIK=(\d{10}).*')
        self.nasdaq = pd.read_csv('nasdaq.csv')
        self.sec_url = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&type=&dateb=&owner=exclude&start=0&count=100'

    def get_cik(self, ticker):
        f = requests.get(self.cik_url.format(ticker), stream = True);
        results = self.CIK_RE.findall(f.text)
        return results[0]
    

    def get_excel_url(self, cik, key):
        base_url = ['https://','sec.gov']
        
        response = requests.get(self.sec_url.format(cik))
        soup = BeautifulSoup(response.text, 'html.parser')
        tbls = soup.find_all('table', {'class':'tableFile2'})[0]
        tag = self.search_latest_report(tbls, key)
        interactive_data_url = tag.find_all('a')[1].get('href')
        interactive_data_url = ''.join(base_url + [interactive_data_url])
        interactive_data_page = requests.get(interactive_data_url)

        page_soup = BeautifulSoup(interactive_data_page.text, 'html.parser')
        excel_url = page_soup.find_all('a', {'class':'xbrlviewer'})[1]
        excel_url = excel_url.get('href')
        pandas_excel_url = ''.join(base_url + [excel_url])

        return pandas_excel_url


    def search_latest_report(self, table, key):
        for tr in table:
            search = False
            for td in tr:
                
                if isinstance(td, bs4.element.Tag):
                    
                    if key in td.text and len(td.text) == 4:
                        search=True
                        
                    if search and 'Interactive Data' in td.text:
                        return td

    
    def get_report(self, ticker, key = '10-Q'):
        cik = self.get_cik(ticker)
        url = self.get_excel_url(cik, key=key)
        dfs = pd.read_excel(url, 
                            sheet_name = None,
                           engine='openpyxl')
        return dfs

