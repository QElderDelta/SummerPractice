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
    gameBlocks = bsObj.findAll("td", {"class" : "clamp-summary-wrap"})
    for game in gameBlocks:
        name = game.find("a", {"class" : "title"})
        rating = game.find("div", {"class" : "metascore_w large game positive"})
        platform = game.find("span", {"class" : "data"})
        print(name.get_text() + ' ' + rating.get_text() + ' ' + ''.join(platform.get_text().strip()))      