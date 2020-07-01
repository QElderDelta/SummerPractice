import urllib.request
from bs4 import BeautifulSoup

if __name__ == "__main__":
    url = "https://www.metacritic.com/browse/games/score/metascore/all/all/filtered"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'    
    }
    request = urllib.request.Request(url, headers = headers)
    html = urllib.request.urlopen(request)
    bsObj = BeautifulSoup(html, features="html.parser")
    games = bsObj.findAll("a", {"class" : "title"})
    rates = bsObj.findAll("div", {"class" : "metascore_w large game positive"})
    p = bsObj.findAll("div", {"class" : "platform"})
    for game in games:
        print(game.get_text())
    for rate in rates:
        print(rate.get_text())
    for platform in p:
        plat = platform.find("span", {"class" : "data"})
        if plat is not None:
            print(plat.get_text())        