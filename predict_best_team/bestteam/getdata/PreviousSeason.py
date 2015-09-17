from bs4 import BeautifulSoup
import urllib2
import numpy as np
import sys
import psycopg2
from psycopg2.extensions import AsIs


def write_to_db(data):
    try:
        conn = psycopg2.connect("dbname='fantasyfootball' user='tylerfolkman'")
        print("Connected to fantasy football database!")
    except:
        print "I am unable to connect to the database."
    cur = conn.cursor()
    for player in data:
        columns = player.keys()
        values = [player[column] for column in columns]
        insert_statement = 'insert into scoring_leaders (%s) values %s'

        cur.execute(insert_statement, (AsIs(','.join(columns)), tuple(values)))

    cur.execute("""DELETE FROM scoring_leaders a
                    WHERE a.ctid <> (SELECT min(b.ctid)
                        FROM scoring_leaders b
                        WHERE (a.name = b.name and a.team = b.team
                        and a.position = b.position and a.season = b.season
                        and a.week = b.week));""")
    conn.commit()


def get_source(url):
    data = urllib2.urlopen(url).read()
    return BeautifulSoup(data)


def generate_all_urls(season, n_pages, page_size=50):
    start_values = np.arange(0, page_size * n_pages, page_size)
    all_urls = []
    for i in start_values:
        all_urls.append("http://games.espn.go.com/ffl/leaders?seasonTotals=true&seasonId={0}&startIndex={1}"
                        .format(season, i))
    return all_urls


def get_data_from_source(source, season):
    table = []
    for tr in source.find_all('tr')[3:]:
        tds = tr.find_all('td')

        player_dict = {}
        try:
            player_info = tds[0].text.split(",")
            player_dict['name'] = player_info[0]
            player_dict['team'] = player_info[1].split(u'\xa0')[0].strip()
            player_dict['position'] = player_info[1].split(u'\xa0')[1].strip()
        except:
            player_info = tds[0].text.split(" ")
            player_dict['name'] = player_info[0]
            player_dict['team'] = player_info[0]
            player_dict['position'] = "D"

        player_dict['season'] = season
        player_dict['week'] = 'all'

        # passing
        cmp_atmp = tds[2].text.split("/")
        player_dict['passing_completed'] = int(cmp_atmp[0])
        player_dict['passing_attempted'] = int(cmp_atmp[1])
        player_dict['passing_yds'] = int(tds[3].text)
        player_dict['passing_td'] = int(tds[4].text)
        player_dict['passing_int'] = int(tds[5].text)

        # rushing)
        player_dict['rushing_attempts'] = int(tds[7].text)
        player_dict['rushing_yds'] = int(tds[8].text)
        player_dict['rushing_td'] = int(tds[9].text)

        # receiving)
        player_dict['receiving_receptions'] = int(tds[11].text)
        player_dict['receiving_yds'] = int(tds[12].text)
        player_dict['receiving_td'] = int(tds[13].text)
        player_dict['receiving_targets'] = int(tds[14].text)

        # misc)
        player_dict['two_point_conv'] = int(tds[16].text)
        player_dict['fumbles'] = int(tds[17].text)
        player_dict['total_returned_tds'] = int(tds[18].text)

        player_dict['total_points'] = int(tds[20].text)

        table.append(player_dict)
    return table


def main():
    season = int(sys.argv[1])
    n_pages = int(sys.argv[2])
    all_urls = generate_all_urls(season, n_pages)
    all_tables = []
    for url in all_urls:
        soup = get_source(url)
        table = get_data_from_source(soup, season)
        all_tables = all_tables + table
    write_to_db(tuple(all_tables))
    print("Finished!")

if __name__ == '__main__':
    main()