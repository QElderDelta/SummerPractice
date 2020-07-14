import urllib.request
from urllib.error import HTTPError
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

def get_name(product_title):
    name = product_title.find("a", {"class" : "hover_none"})
    if name is not None:
        name = name.get_text().strip()
    return name

def get_platform(product_title):
    platform = product_title.find("span", {"class" : "platform"})
    if platform is not None:
        platform = platform.find("a")
    if platform is not None:
        platform = ''.join(platform.get_text().strip())
    return platform

def get_year(game_info):
    year = game_info.find("div", {"class" : "product_data"})
    if year is not None:
        year = year.find("li", {"class" : "summary_detail release_data"})
    if year is not None:
        year = year.find("span", {"class" : "data"})
    if year is not None:
        year = year.get_text()
        if ',' in year:
            year = year.split(',')[1]
    return year

def get_rating(game_info):
    rating = game_info.find("div", {"class" : "score_summary metascore_summary"})
    if rating is not None:
        rating = rating.find("a", {"class" : "metascore_anchor"})
    if rating is not None:
        rating = rating.find("span")
    if rating is not None:
        rating = rating.get_text()
    return rating

if __name__ == "__main__":
    mainsitemap_url = "https://www.metacritic.com/siteindex.xml"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
    }
    request = urllib.request.Request(mainsitemap_url, headers=headers)
    mainsitemap = urllib.request.urlopen(request)
    mainsitemap_bs = BeautifulSoup(mainsitemap, features="lxml")
    sitemaps = []
    gamespages = []
    for sitemap in mainsitemap_bs.findAll("sitemap"):
        if "Game" in sitemap.get_text():
            sitemaps.append(sitemap.get_text())
    counter = 1
    for sitemap in sitemaps:
        print("Processing {} out of {} maps".format(counter, len(sitemaps)))
        counter += 1
        request = urllib.request.Request(sitemap, headers=headers)
        while True:
            try:
                xml = urllib.request.urlopen(request)
                break
            except HTTPError as e:
                print(e)
                time.sleep(0.5)
                continue
        sitemap_bs = BeautifulSoup(xml, features="lxml")
        counter = 0
        for link in sitemap_bs.findAll("loc"):
            if "/details" in link.get_text():
                print("Processing {} page".format(counter))
                counter += 1
                request = urllib.request.Request(link.get_text(), headers=headers)
                while True:
                    try:
                        html = urllib.request.urlopen(request)
                        break
                    except HTTPError as e:
                        print(e)
                        time.sleep(0.5)
                        continue
                game_info = BeautifulSoup(html, features="html.parser").find("div", {"id" : "main"})
                if game_info is None:
                    continue
                rating = game_info.find("div", {"class" : "data metascore score_tbd"})
                if rating is None:
                    product_title = game_info.find("div", {"class" : "product_title"})
                    if product_title is not None:
                        name = get_name(product_title)
                        platform = get_platform(product_title)
                        year = get_year(game_info)
                        rating = get_rating(game_info)
                        if name is None or platform is None or year is None or rating is None:
                            continue
                        print(name, platform, year, rating)
                        insert_into_database(name, rating, year, platform)
                    else:
                        continue
                else:
                    continue
                time.sleep(1)
