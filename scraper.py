import urllib.request
import time
from bs4 import BeautifulSoup
import psycopg2

def insert_into_database(name, rating, year, platform):
    try:
        conn = psycopg2.connect(dbname='qelderdelta',
                                user='qelderdelta', password='lolxd322',
                                host='localhost')
        cursor = conn.cursor()
        insert_query = """ INSERT INTO games_list (name, rating, year, platform) VALUES (%s, %s, %s, %s)"""
        to_insert = (name, rating, year, platform)
        cursor.execute(insert_query, to_insert)
        conn.commit()
        cursor.close()
    except (Exception, psycopg2.Error) as error:
        print("Failed to insert data into database", error)
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    URL_PATTERN = "https://www.metacritic.com/browse/games/score/metascore/all/all/filtered?sort=desc&page="
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
    }
    for i in range(30):
        print("Processing page #", i + 1)
        URL = URL_PATTERN + str(i)
        request = urllib.request.Request(URL, headers=headers)
        html = urllib.request.urlopen(request)
        bs_obj = BeautifulSoup(html, features="html.parser")
        game_blocks = bs_obj.findAll("td", {"class" : "clamp-summary-wrap"})
        for game in game_blocks:
            name = game.find("a", {"class" : "title"})
            rating = game.find("div", {"class" : "metascore_w large game positive"})
            info = game.find("div", {"class" : "clamp-details"})
            year = info.find("span", recursive=False)
            platform = info.find("span", {"class" : "data"})
            insert_into_database(name.get_text(), rating.get_text(),
                                 year.get_text().split(',')[1], ''.join(platform.get_text().strip()))
        time.sleep(2)
