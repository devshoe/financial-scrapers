import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint as p
import re, pandas as pd 
from datetime import datetime as dt
from io import StringIO
import json
headers = {'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'en-GB,en-US;q=0.8,en;q=0.6',
        'Connection': 'keep-alive',
        'Host': 'www1.nseindia.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'}

def option_chain(symbol, expiry="28MAY2020"):
    base_url = "https://www.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?"
    indices = ["BANKNIFTY", "NIFTY", "NIFTYIT"]
    query_parameters = {
        "segmentLink": "17",
        "instrument": "OPTIDX" if symbol in indices else "OPTSTK",
        "symbol" : symbol,
        "date": expiry
    }
    html = requests.get(base_url, query_parameters, headers=headers).content
    option_table = bs(html, "html.parser").find("table", id="octable")
    columns = [column_name.text for column_name in option_table.find("thead").find_all("th")][4:-1]
    for i in range(10):
        columns[i] += "_CE"
        columns[11+i] += "_PE"
    rows = []
    for row in option_table.find_all("tr")[2:-1]:
        text = re.sub("(\t|\r)", '', row.text).split('\n')
        while '' in text: text.remove('')
        cleaned_text = [space_separated_text.replace(' ','').replace(',', '') for space_separated_text in text]
        dict_ = dict(zip(columns, cleaned_text))
        for k,v in dict_.items():dict_[k] = float(v) if v!="-" else 0
        rows.append(dict_)
    df = pd.DataFrame(rows).set_index("Strike Price")
    return df

def fo_list():
    url = "https://www1.nseindia.com/products/content/derivatives/equities/fo_underlyinglist.htm"
    sesh = requests.Session()
    resp = sesh.get(url, headers=headers)
    soup = bs(resp.content,"html.parser")
    names = []
    for row in soup.findAll("tr"):
        try:
            elem =  (row.findAll("td")[-1]).text
            names.append(elem.rstrip("\n"))
        except:pass
    names.pop()
    names.remove("Derivatives on Individual Securities")
    names.remove("NIFTYIT")
    return names

def indices():
    data = json.loads(requests.get("https://www1.nseindia.com/homepage/Indices1.json", headers=headers).content)["data"]
    for d in data: del d["imgFileName"]
    return pd.DataFrame(data)

def historical_futures(symbol, expiry=None, dateRange="24month", fromDate=None, toDate=None):
    base_url = "https://www1.nseindia.com/products/dynaContent/common/productsSymbolMapping.jsp?"
    keys ={'instrumentType': "FUTIDX" if "NIFTY" in symbol else "FUTSTK",
				'symbol': symbol,
				'expiryDate': dt.strftime(expiry, "%d-%m-%Y") ,
				'optionType': 'select',
				'strikePrice': '',
				'dateRange': dateRange if not (fromDate and toDate) else '',
				'fromDate': '' if not fromDate else dt.strftime(fromDate, "%d-%m-%Y"),
				'toDate': '' if not fromDate else dt.strftime(fromDate, "%d-%m-%Y"),
				'segmentLink': 9,
                'symbolCount': ''}
    response = bs(requests.get(base_url, headers=headers, params=keys).content, 'html.parser')
    print(response)

def historical_options(symbol, expiry=None, optionType="CE", strikePrice="", dateRange="24month", fromDate=None, toDate=None):
    base_url = "https://www1.nseindia.com/products/dynaContent/common/productsSymbolMapping.jsp?"
    keys ={'instrumentType': "OPTIDX" if "NIFTY" in symbol else "OPTSTK",
				'symbol': symbol,
				'expiryDate': dt.strftime(expiry, "%d-%m-%Y") if expiry else 'select' ,
				'optionType': optionType,
				'strikePrice': strikePrice,
				'dateRange': dateRange if not (fromDate and toDate) else '',
				'fromDate': '' if not fromDate else dt.strftime(fromDate, "%d-%m-%Y"),
				'toDate': '' if not fromDate else dt.strftime(fromDate, "%d-%m-%Y"),
				'segmentLink': 9,
                'symbolCount': ''}
    for k,v in keys.items(): base_url+= k+"="+str(v)+"&"
    response = requests.get(base_url[:-1], headers=headers).text
    print(response)
    return response
(historical_options("NIFTY", strikePrice="9000", dateRange="week"))