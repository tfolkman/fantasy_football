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
        insert_statement = 'insert into next_week_projections (%s) values %s'

        cur.execute(insert_statement, (AsIs(','.join(columns)), tuple(values)))

    cur.execute("""DELETE FROM next_week_projections a
                    WHERE a.ctid <> (SELECT min(b.ctid)
                        FROM next_week_projections b
                        WHERE (a.name = b.name and a.team = b.team
                        and a.position = b.position and a.season = b.season
                        and a.week = b.week));""")
    conn.commit()


def get_source(url):
    data = urllib2.urlopen(url).read()
    return BeautifulSoup(data)


def generate_all_urls(season, week, n_pages, page_size=40):
    start_values = np.arange(0, page_size * n_pages, page_size)
    all_urls = []
    for i in start_values:
        all_urls\
            .append("http://games.espn.go.com/ffl/tools/projections?&scoringPeriodId={2}&seasonId={0}&startIndex={1}"
                    .format(season, i, week))
    return all_urls


def get_data_from_source(source, season, week):
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
        player_dict['week'] = week

        opponent_text = tds[1].text
        if "@" in opponent_text:
            player_dict['opponent'] = opponent_text[1:]
            player_dict['at_home'] = 0
        else:
            player_dict['opponent'] = opponent_text
            player_dict['at_home'] = 1

        # passing
        cmp_atmp = tds[3].text.split("/")
        player_dict['passing_completed'] = float(cmp_atmp[0])
        player_dict['passing_attempted'] = float(cmp_atmp[1])
        player_dict['passing_yds'] = float(tds[4].text)
        player_dict['passing_td'] = float(tds[5].text)
        player_dict['passing_int'] = float(tds[6].text)

        # rushing)
        player_dict['rushing_attempts'] = float(tds[7].text)
        player_dict['rushing_yds'] = float(tds[8].text)
        player_dict['rushing_td'] = float(tds[9].text)

        # receiving)
        player_dict['receiving_receptions'] = float(tds[10].text)
        player_dict['receiving_yds'] = float(tds[11].text)
        player_dict['receiving_td'] = float(tds[12].text)

        player_dict['total_points'] = int(tds[13].text)

        table.append(player_dict)
    return table


def main():
    season = int(sys.argv[1])
    week = sys.argv[2]
    n_pages = int(sys.argv[3])
    all_urls = generate_all_urls(season, week, n_pages)
    all_tables = []
    for url in all_urls:
        soup = get_source(url)
        table = get_data_from_source(soup, season, week)
        all_tables = all_tables + table
    write_to_db(tuple(all_tables))
    print("Finished!")

if __name__ == '__main__':
    main()