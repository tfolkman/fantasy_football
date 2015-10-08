from bs4 import BeautifulSoup
import urllib2
import numpy as np
import sys
import psycopg2
from psycopg2.extensions import AsIs


def write_to_db(data, season):
    try:
        conn = psycopg2.connect("dbname='fantasyfootball' user='tylerfolkman'")
        print("Connected to fantasy football database!")
    except:
        print "I am unable to connect to the database."
    cur = conn.cursor()
    cur.execute("""DELETE FROM points_against WHERE season = {0}""".format(str(season)))
    for player in data:
        columns = player.keys()
        values = [player[column] for column in columns]
        insert_statement = 'insert into points_against (%s) values %s'

        cur.execute(insert_statement, (AsIs(','.join(columns)), tuple(values)))

    conn.commit()


def get_source(url):
    data = urllib2.urlopen(url).read()
    return BeautifulSoup(data)


def get_all_data(season):
    position_dict = {'1': 'QB', '2': 'RB', '3': 'WR', '4': 'TE', '16': 'D'}
    all_tables = []
    for key, value in position_dict.iteritems():
        url = "http://games.espn.go.com/ffl/pointsagainst?&seasonId={0}&positionId={1}".format(season, key)
        soup = get_source(url)
        table = get_data_from_source(soup, season, value)
        all_tables = all_tables + table
    return all_tables


def get_data_from_source(source, season, position):
    table = []
    for tr in source.find_all('tr')[3:]:
        tds = tr.find_all('td')

        player_dict = {}

        player_info = tds[0].text.split("vs.")
        player_dict['team'] = player_info[0].strip()
        player_dict['position'] = position

        player_dict['season'] = season

        if season == 2015:
	    if tds[2].text == "** BYE **":
                start_index = 4
	    else:
		start_index = 5
        elif season == 2014:
            start_index = 4

        # passing
        cmp_atmp = tds[start_index].text.split("/")
        player_dict['passing_completed'] = int(cmp_atmp[0])
        player_dict['passing_attempted'] = int(cmp_atmp[1])
        player_dict['passing_yds'] = int(tds[start_index+1].text)
        player_dict['passing_td'] = int(tds[start_index+2].text)
        player_dict['passing_int'] = int(tds[start_index+3].text)

        # rushing)
        player_dict['rushing_attempts'] = int(tds[start_index+5].text)
        player_dict['rushing_yds'] = int(tds[start_index+6].text)
        player_dict['rushing_td'] = int(tds[start_index+7].text)

        # receiving)
        player_dict['receiving_receptions'] = int(tds[start_index+9].text)
        player_dict['receiving_yds'] = int(tds[start_index+10].text)
        player_dict['receiving_td'] = int(tds[start_index+11].text)
        player_dict['receiving_targets'] = int(tds[start_index+12].text)

        player_dict['total_points'] = float(tds[start_index+14].text)

        table.append(player_dict)
    return table


def main():
    season = int(sys.argv[1])
    tables = get_all_data(season)
    write_to_db(tuple(tables), season)
    print("Finished!")

if __name__ == '__main__':
    main()
