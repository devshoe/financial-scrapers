import requests, re
from bs4 import BeautifulSoup as bs
from pprint import pprint as p
from support.io import indexDb

homepage = "http://www.moneycontrol.com"
stockNews = "https://www.moneycontrol.com/news/business/stocks/"
rssFeeds ="http://www.moneycontrol.com/india/newsarticle/rssfeeds/rssfeeds.php"
globalIndicesUrl = "https://www.moneycontrol.com/markets/global-indices/"
optionsUrl= "https://www.moneycontrol.com/markets/fno-market-snapshot"
# landingHtml = requests.get(homepage).content
# landingSoup = bs(landingHtml, "html.parser")

# rssFeedSoup = bs(requests.get(rssFeeds).content, "html.parser")
# print(requests.get(rssFeeds).text)

def returnSoup(url):return bs(requests.get(url).content, "html.parser")
def convToFloat(string):
    string = string.rstrip("%")
    string  = string.split(",")
    return float("".join(string))

def grabTables(soup=None, tag="ul", className="nav-tabs mctab"): #the tage and className should be of title you want to grab
    multiCarded = soup.findAll(tag, class_=className)
    tableDict = {}
    for title in multiCarded: #so so if its in this class, its one of those multi option infos
        titles,columns,prevElem = (title.text.split("\n")),[],title
        titles.pop(0)
        titles.pop()
        for i in range(len(titles)):
            prevElem = prevElem.findNext("table")
            headers = []
            for table in prevElem:
                localList= []
                try:
                    for header in table.findAll("th"):
                        h = re.sub("\n", " ",string=header.text)
                        headers.append(h)
                    
                    for row in table.findAll("tr"):
                        data={}
                        for index,elem in enumerate(row.findAll("td")):
                            data[headers[index]] = elem.text
                        localList.append(data)
                    tableDict[titles[i]] = (localList)
                    
                except:pass
    return(tableDict)

def grabAllTables(soup):
    tableDict={}
    for table in soup.findAll("table"):
        headers = []
        title = table.previous_sibling(tag)
        for header in table.findNext("th"):
            headers.append(header.text)
        for row in table.findAll("tr"):
            data = {}
            for index, elem in enumerate(row.findAll("td")):
                data[headers[index]] = elem.text
            

def grabNextTable(soup=None):
    tables, localList = soup.findNext("table"), []
    table = tables#find first complete table
    while len(tables.findAll("th"))<1:
        tables = tables.findNext("table")
        table = tables
    columns = [x.text for x in table.findAll("th")]
    for row in table.findAll("tr"):
        data={}
        for index,elem in enumerate(row.findAll("td")):
            try:data[columns[index]] = elem.text
            except:pass
        if len(data):localList.append(data)
    return localList
#def grabTables(soup=None, tag="ul", className="nav-tabs mctab"):
def fii():return {"FII":grabNextTable(returnSoup(globalIndicesUrl).find("a", {"href":"#ProvisionNSE"}))}

def dii():return {"DII":grabNextTable(returnSoup(globalIndicesUrl).find("div", {"id":"ProvisionNSE"}))}
    
def globalIndices():
    indiceSoup = returnSoup(globalIndicesUrl)
    returnDict = {}
    indices = indiceSoup.findAll(class_="robo_medium")
    for indice in indices:
        indiceInfo = {}
        name = indice.text.strip("\n")
        name = name.strip(" ")
        name = name.split(" ")
        name.pop()
        name.pop()
        for x in range(len(name)): 
            if name[x] == " ": name.pop(x)
        name = " ".join(name)
        presentPrice = (indice.findNext('td').text).split(",")
        presentPrice = float("".join(presentPrice))
        indiceInfo["price"] = presentPrice
        changeAndPct = indice.findNext('td').findNext('td').text.strip(" ").split()
        oandpc= (indice.findNext('td').findNext('td').findNext("td").findNext("td").text.split(" "))
        indiceInfo["open"] = float(oandpc[0].rstrip("\n"))
        indiceInfo["prevClose"] = float(oandpc[-1])
        indiceInfo["change"], indiceInfo["pChange"] = float(changeAndPct[0]), float(changeAndPct[1])
        handl = (indice.findNext('td').findNext('td').findNext("td").findNext("td").findNext("td").text.split(" "))
        indiceInfo["high"] = float(handl[0].rstrip("\n"))
        indiceInfo["low"] = float(handl[-1])
        returnDict[name] = indiceInfo
    return returnDict

def asianIndices(exclJapan = True):
    indices = ['SGX Nifty', 'Nikkei 225', 'Straits Times','Hang Seng', 'SET Composite', 'Jakarta Composite', 'Shanghai Composite', 'KOSPI', 'Taiwan Weighted']
    if exclJapan: indices.remove("Nikkei 225")
    returnDict = {}
    for indice, data in globalIndices().items():
        if indice in indices: returnDict[indice] = data
    return returnDict

def news(categories=[""], exclude=[""]):
    stockNewsSoup = bs(requests.get(stockNews).content)
    # categories,links = [], []
    # catHtml = stockNewsSoup.find("ul", class_="headbotmmenus clearfix nav-tabs")
    # for category in catHtml.findAll("a"):
    #     print(category["title"])
 
    newsList = []
    for news in stockNewsSoup.findAll("li", class_="clearfix"):
        content = news.text.split("IST")
        timestamp = content[0].strip("\n")
        headline = re.sub("\n","",content[1])

        text = news.findNext("p").text
        localDict = {"timestamp":timestamp, "title":headline, "content":text}
        newsList.append(localDict)
    return newsList

def marketStats(): #todo
    statsSoup = returnSoup("https://www.moneycontrol.com/stocks/marketstats/index.php")
    titles = ["Top Losers NSE", "Top Losers BSE", "Top Gainers NSE", "Top Gainers NSE"]
    titles = ["Only Buyers NSE"]
    for title in titles:
        tb = grabNextTable(statsSoup.find("a",{"title":title}))
        print(tb)
        
def contributionToIndex():
    contSoup = returnSoup("https://www.moneycontrol.com/stocks/marketstats/indcontrib.php?optex=NSE&opttopic=indcontrib")
    data = []
    for name in contSoup.findAll("td", class_="PR"):
        info = {}
        stock = (name.text.split(" ")[0])
        news = (name.findNext("li"))
        sector = (news.findNext("td"))
        price = sector.findNext("td")
        change = price.findNext("td")
        changeP = change.findNext("td")
        mktCap = changeP.findNext("td")
        contribution = mktCap.findNext("td")
        volumes  = contribution.findNext("div", class_="title2 MB5 TAC").findNext("table") #last is todays
        deliverables = volumes.findNext("div", class_="title2 MB5 TAC").findNext("table")
        performance = (contribution.findNext("td", class_="performance"))
        sma30 = volumes.findNext("td", class_="30d")
        sma50 = volumes.findNext("td", class_="50d")
        sma150 = volumes.findNext("td", class_="150d")
        sma200 = volumes.findNext("td", class_="200d")
        pe = volumes.findNext("td", class_="pe")
        pb = volumes.findNext("td", class_="pb")
        uc = volumes.findNext("td", class_="uc")
        lc = volumes.findNext("td", class_="lc")
        vwap = volumes.findNext("td", class_="vwap")
        del3 = deliverables.findNext("td", {"align":"right"})
        del5 = del3.findNext("td", {"align":"right"})
        del8 = del5.findNext("td", {"align":"right"})

        
        info["name"]= stock
        info["news"] = news.text
        info["sector"]= sector.text
        info["price"] = convToFloat(price.text)
        info["change"] = convToFloat(changeP.text)
        info["changePoints"] = convToFloat(change.text)
        info["marketcap"] = mktCap.text
        info["contribution"] = convToFloat(contribution.text)
        info["sma30"] = convToFloat(sma30.text)
        info["sma50"] = convToFloat(sma50.text)
        info["sma150"] = convToFloat(sma150.text)
        info["sma200"] = convToFloat(sma200.text)
        info["vwap"] = convToFloat(vwap.text)
        info["uppercircuit"] = convToFloat(uc.text)
        info["lowercircuit"] = convToFloat(lc.text)
        info["pe"] = convToFloat(pe.text)
        info["pb"] = convToFloat(pb.text)
        info["deliverables3"] = convToFloat(del3.text)
        info["deliverables5"] = convToFloat(del5.text)
        info["deliverables8"] = convToFloat(del8.text)
        data.append(info)
    return data

def deliverables(indice = "NIFTY 50"):
    indiceLink = {"NIFTY 50": "cnx-nifty"}
    url = "http://www.moneycontrol.com/india/stockmarket/stock-deliverables/marketstatistics/indices/"+indiceLink[indice]+".html"
    soup = returnSoup(url)
    table = soup.find("table",class_="tbldata14 bdrtpg")
    columns = [x.text for x in table.findAll("th")]
    data = []
    for row in (table.findAll("tr")):
        r = {}
        for i,cell in enumerate(row.findAll("td")):
            txt = re.sub("(\n|,| )","",cell.text)
            try: txt = float(txt)
            except:pass
            if isinstance(txt,str): txt=txt.upper()
            r[columns[i]] = txt
        data.append(r)
    data.pop(0)
    for x,dat in enumerate(indexDb[indice].find({}).sort([("Symbol", 1)])):
        data[x]["symbol"] = dat["Symbol"]
    return data

print(fii())