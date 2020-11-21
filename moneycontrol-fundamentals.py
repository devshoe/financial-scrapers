import requests
from bs4 import BeautifulSoup as bs
import json
import re
from pprint import pprint as p

def get_fundamentals(stock):
    data = str(bs(requests.get(f"https://stocks.tickertape.in/{stock}").content, "html.parser").find_all("script")[-7])
    cleaned_data = json.loads(re.sub("(;(?=_).*)", '', data)[24:])["props"]["pageProps"]
    news = cleaned_data["news"]
    announcements = cleaned_data["events"]["data"]["announced"]
    peers = [{stock["stock"]["info"]["ticker"]:stock["stock"]["ratios"]} for stock in cleaned_data["peers"]["data"]["stocks"]]
    ratios = cleaned_data["overview"]["data"]["overview"]["stock"]["ratios"]
    return {"ratios":ratios, "news":news, "announcements":announcements, "peers":peers}

# p(get_fundamentals("BHARTIARTL"))
