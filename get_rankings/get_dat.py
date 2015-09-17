from bs4 import BeautifulSoup
import urllib2
import numpy as np
import json


def get_source(url):
    data = urllib2.urlopen(url).read()
    return BeautifulSoup(data)


def generate_all_urls():
    start_values = np.arange(0, 320, 40)
    all_urls = []
    for i in start_values:
        all_urls.append("http://games.espn.go.com/ffl/tools/projections?&startIndex={0}".format(i))
    return all_urls


def get_data_from_source(source):
    table = []
    for tr in source.find_all('tr')[3:]:
        tds = tr.find_all('td')

        player_dict = {}
        try:
            player_info = tds[1].text.split(",")
            player_dict['name'] = player_info[0]
            player_dict['team'] = player_info[1].split(u'\xa0')[0].strip()
            player_dict['position'] = player_info[1].split(u'\xa0')[1].strip()
        except:
            player_info = tds[1].text.split(" ")
            player_dict['name'] = player_info[0]
            player_dict['team'] = player_info[0]
            player_dict['position'] = "D"
        player_dict['points'] = tds[12].text

        table.append(player_dict)
    return table


def write_to_csv(data_list, filename):
    with open(filename, 'w') as outfile:
        json.dump(data_list, outfile)


def main():
    urls = generate_all_urls()
    all_tables = []
    for url in urls:
        soup = get_source(url)
        table = get_data_from_source(soup)
        all_tables = all_tables + table
    write_to_csv(all_tables, "data/rankings_list.json")

if __name__ == "__main__":
    main()