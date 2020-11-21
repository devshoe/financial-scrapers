import requests
from bs4 import BeautifulSoup as bs, NavigableString
from pprint import pprint as p
import re, pandas as pd 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from datetime import datetime as dt
import time
options = Options()
options.headless=True
driver = (webdriver.Chrome("/home/devshoe/chromedriver", chrome_options=options))


driver.get("https://in.investing.com/indices/indices-futures")

headers = {'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'en-GB,en-US;q=0.8,en;q=0.6',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'}
def timeit(func):
    def wrapper(*args, **kwargs):
        start = dt.now()
        ret = func(*args, **kwargs)
        ttaken = (dt.now()-start)
        print(f"Time taken for execution:{ttaken.seconds}s {int(ttaken.microseconds/1000)}ms")
        return ret
    return wrapper

def taiwan(onlyRelevant=True):
    dow = "https://info512ah.taifex.com.tw/EN/FusaQuote_Norl.aspx"
    sesh = requests.Session()
    soup = bs(sesh.get(dow, headers=headers).content, "html.parser")
    head = ([x.text for x in list(soup.find("tr", class_="custDataGridRow").findAll("td"))])
    finalDict = {}
    for i,row in enumerate(soup.findAll("tr", class_="custDataGridRow")):
        if i != 0 :
            content = ([re.sub("\n","",x.text) for x in list(row.findAll("td"))])
            data = (dict(list(zip(head, content))))
            name = data["Contract"]
            del data["Contract"]
            finalDict[name] = data
    if onlyRelevant: return -float(finalDict["TX030"]["Change%"]) if float(finalDict["TX030"]["Change"])<0 else float(finalDict["TX030"]["Change%"])
    return finalDict



    # head = []
    # for tr in soup:
    #     if isinstance(tr, NavigableString):pass
    #     else:
    #         for td in tr.findAll("td"):
    #             print(td.text)
def investing(url): #whatever i can get my hands on, investing.com
    sesh = requests.Session()
    soup = bs(sesh.get(url, headers=headers).content, "html.parser")
    data = {}
    sub = []
    for x in (soup.find("div", class_="last u-down")):
        try:sub.append(x.text)
        except:pass
    sub[0] = float(re.sub(",", "", (sub[0])))
    sub[1] = float(re.sub(",", "", (sub[1])))
    sub[2] = re.sub("(\(|\)|%)", "", sub[2]) #
    return sub[-1]
    print(sub)

def meh(): #very long runtime ~30secs :( no api
    fut = {}
    fut["KOSPI"]  = investing("https://in.investing.com/indices/korea-200-futures")
    fut["DOW"]    = investing("https://in.investing.com/indices/us-30-futures")
    fut["NIKKEI"] = investing("https://in.investing.com/indices/japan-225-futures")
    fut["TAIWAN"] = taiwan()
    fut["EU"]     = investing("https://in.investing.com/indices/eu-stocks-50-futures")
    fut["SGX"]    = investing("https://in.investing.com/indices/india-50-futures")

    return fut

@timeit
def futures(soup=None):
    if not soup:
        className = "common-table-item u-clickable"
        url = "https://in.investing.com/indices/indices-futures"
        sesh = requests.Session()
        soup = bs(sesh.get(url, headers=headers).content, "html.parser")

    data = {}
    cols = []
    for table in soup.findAll("table", class_="common-table medium js-table js-streamable-table"):
        for col in table.findAll("thead"):
            cols.append(col.text)
        cols = re.sub("\n"," ",cols[0]).split(" ")
        cols = [x for x in cols if x != '' and x not in ['Clear', 'Save']]
        cols.append("Status")
        for i,row in enumerate(table.findAll("tr")):
            items = []
            for item in row.findAll("td"):
                itemCpy = item
                item = re.sub("\n", "", item.text)
                if item != " ":
                    items.append(item)
                    attr = itemCpy.attrs.get("class")
                    if "col-time" in attr:
                        status = 1 if "opened" in attr else 0
                        items.append(status)
                    if "col-flag" in attr:
                        print(attr)

            try:
                sub = (dict(list(zip(cols, items))))
                name = sub["Name"]
                del sub["Name"]
                data[name] = sub
            except:pass
    df= (pd.DataFrame.from_dict(data).transpose())
    df["Chg%"] = df["Chg%"].str.rstrip(" %").astype(float)
    return df

def parsedFutures():
    usaBasket = ["Dow 30", "S&P 500", "Nasdaq", "Russel 2000"]
    eurBasket = ["DAX", "FTSE 100"]
    asiaBasket = ["Singapore MSCI", "KOSPI 200", "Hang Seng", "MSCI Taiwan", "Nikkei 225", "Nifty 50"]
    straya = ["S&P/ASX 200"]
    
while(1):
    print(futures(bs(driver.page_source)))
    time.sleep(10)
