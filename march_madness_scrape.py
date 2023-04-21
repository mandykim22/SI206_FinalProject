#Name: Luciana Solorzano
#id: 82482379
#email: lusolorz@umich.edu
#due date: 04/21/23

"""
Uses beautiful to webscrape Wikipedia page and obtain list of 64 teams playing in March Madness 2023 tournament
https://en.wikipedia.org/wiki/2023_NCAA_Division_I_men%27s_basketball_tournament


Table structures:

Possible Calculations:

Limit 1,000 calls per day

Coach ranking vs average ranking of all players? --> team_chance
    add these two values --> values w/ the higher value win the game -> 961 calls

A taller average team wins more games and then compare that to what actually happens -> 65 calls *

A certain region of the US is better at playing basektball -> 1 call but no bracket  

Table Players:
id, first_last, height, team_id

Table teams:
id, name, team_chance(avg height), region, link

Table regions:
id, name


"""

from bs4 import BeautifulSoup
import requests
import sqlite3
import re
import os


def get_teams_playing(url, conn, cur):
    response = requests.get(url).text
    soup = BeautifulSoup(response, "html.parser")
    titles = soup.find_all('table')
    South_reg = titles[12].find_all('a')
    East_reg = titles[18].find_all('a')
    Midwest_reg = titles[24].find_all('a')
    West_reg = titles[30].find_all('a')
    teams = []
    team_id = 1
    for link in South_reg:
        if "2022" in link.get('title'):
            tup = (link.get('title'), team_id, "West Region", link.get('href'))
            teams.append(tup)
            team_id +=1 
    for link in East_reg:
        if "2022" in link.get('title'):
            tup = (link.get('title'), team_id, "East Region",link.get('href'))
            teams.append(tup)
            team_id +=1 
    for link in Midwest_reg:
        if "2022" in link.get('title'):
            #temp = (link.get('title')).replace("2022", "")
            #temp2 = re.sub('\-', '', temp)
            tup = (link.get('title'), team_id, "South Region", link.get('href'))
            teams.append(tup)
            team_id +=1 
    for link in West_reg:
        if "2022" in link.get('title'):
            tup = (link.get('title'), team_id, "Midwest Region", link.get('href'))
            teams.append(tup)
            team_id +=1 
    return teams

def open_db(db):
    path = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.dirname(__file__) #<-- directory name
    full_path = os.path.join(source_dir, db)
    conn = sqlite3.connect(full_path)
    cur = conn.cursor()
    return conn, cur

def creat_table_regions(conn, cur):
    val1 = cur.execute("DROP TABLE IF EXISTS Regions")
    val = cur.execute(
        "CREATE TABLE IF NOT EXISTS Regions (id INTEGER PRIMARY KEY, region TEXT)"
    )
    conn.commit()
    
    regions = ["South Region", "East Region", "Midwest Region", "West Region"]
    count  = 1
    for i in regions:
        val2 = cur.execute(
            "INSERT OR IGNORE INTO Regions (id, region) VALUES (?,?)",(count, i)
        )
        count += 1 
    conn.commit()

def create_teams_table(conn, cur):
    val = cur.execute(
        "CREATE TABLE IF NOT EXISTS Teams_scrape (id INTEGER PRIMARY KEY, name TEXT UNIQUE, team_chance INTEGER, region INTEGER, link TEXT)"
    )
    conn.commit()

def add_to_teams_table(teams, conn, cur):
    cur.execute(
        "SELECT COUNT(*) FROM Teams_scrape"
    )
    index_start = cur.fetchall()[0][0]
    if index_start == None:
        index_start = 0
    elif index_start == 64:
        return
    count = 0
    for i in teams[index_start:]:
        if count == 25:
            break
        cur.execute(
            "SELECT id FROM Regions WHERE region = ?", (i[2], )
        )
        region = cur.fetchall()[0][0]
        cur.execute("INSERT OR IGNORE INTO Teams_scrape (id, name, team_chance, region, link) VALUES (?, ?, ?, ?, ?)",(i[1], i[0], 0, region, i[3]))
        count += 1
    conn.commit()

def create_table_players(conn, cur):
    val = cur.execute(
        "CREATE TABLE IF NOT EXISTS Players (id INTEGER, last_first_name TEXT PRIMARY KEY, height INTEGER, team_id INTEGER, indecks INTEGER)"
    )
    conn.commit()

def insert_into_players(conn, cur):
    cur.execute(
        "SELECT link, id FROM Teams_scrape"
    )
    links = cur.fetchall()
    cur.execute(
        "SELECT MAX(id) FROM Players"
    )
    max_id = cur.fetchall()[0][0]
    indecks = []
    if max_id != None:
        cur.execute(
            "SELECT indecks, team_id FROM Players WHERE id = ?", (max_id, )
        )
        indecks = cur.fetchall()
        start_from  = indecks[0][1] - 1
    else:
        start_from = 0
    cur.execute(
        "SELECT COUNT(*) From Players"
    )
    temp = cur.fetchall()
    if temp:
        player_id = temp[0][0] + 1
    else:
        player_id = 1
    count = 1

    for item in links[start_from:]:
        response = requests.get('https://en.wikipedia.org' + item[0]).text
        soup = BeautifulSoup(response, "html.parser")
        player_table = soup.find_all('table', {'class': 'sortable', 'style': 'background:transparent; margin:0px; width:100%;'})[0].find_all('tr')
        index_for_player = 1

        if not indecks:
            index = 1
        elif indecks[0][0] == 0:
            index = 1
        else:
            index = indecks[0][0]+1
        if index >= len(player_table):
            index = 1
        for item2 in player_table[1:]:
            if count > 25:
                break
            new_player = item2.contents[5].find('span').get("data-sort-value")
            new_player_height = item2.contents[7].find('span').text
            temp = re.findall('[0-9]', new_player_height)
            feet = int(temp[0])
            inches = int(temp[1])
            height = inches + (feet * 12)
            name  = new_player.split(",")
            cur.execute(
                "INSERT OR IGNORE INTO Players (id, last_first_name, height, team_id, indecks) VALUES (?, ?, ?, ?, ?)", (player_id, new_player, height, item[1], index_for_player)
            )
            conn.commit()
            count += 1
            index_for_player += 1
            start_from+=1
            player_id += 1
        if count > 25:
                break
    return 1




if __name__ == '__main__':
    print('running :) ...')
    conn, cur = open_db('March_Madness.db')
    creat_table_regions(conn, cur)
    create_teams_table(conn, cur)
    create_table_players(conn, cur)
    teams = get_teams_playing('https://en.wikipedia.org/wiki/2023_NCAA_Division_I_men%27s_basketball_tournament', conn, cur)
    add_to_teams_table(teams, conn, cur)
    insert_into_players(conn, cur)
