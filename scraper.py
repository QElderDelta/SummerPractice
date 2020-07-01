import urllib.request
from bs4 import BeautifulSoup
import time

if __name__ == "__main__":
    urlPattern = "https://www.metacritic.com/browse/games/score/metascore/all/all/filtered?sort=desc&page=0"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'    
    }
    for i in range(2):
        url = urlPattern + str(i)
        request = urllib.request.Request(url, headers = headers)
        html = urllib.request.urlopen(request)
        bsObj = BeautifulSoup(html, features="html.parser")
        gameBlocks = bsObj.findAll("td", {"class" : "clamp-summary-wrap"})
        for game in gameBlocks:
            name = game.find("a", {"class" : "title"})
            rating = game.find("div", {"class" : "metascore_w large game positive"})
            info = game.find("div", {"class" : "clamp-details"})
            year = info.find("span", recursive = False)
            platform = info.find("span", {"class" : "data"})
            print(name.get_text() + ' ' + rating.get_text() + ' ' + ''.join(platform.get_text().strip()) 
                + ' ' + year.get_text().split(',')[1])
        time.sleep(2)          