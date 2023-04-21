import matplotlib.pyplot as plt
import sqlite3
import os
import re


"""
Calculations:

Regions:
Teams in each region 

Team:
Player on each team (roster)

Teams:
Average height for each team 

"""


def open_db(db):
    path = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.dirname(__file__) #<-- directory name
    full_path = os.path.join(source_dir, db)
    conn = sqlite3.connect(full_path)
    cur = conn.cursor()
    return conn, cur

def update_team_chance_col(conn, cur):
    val = cur.execute(
        "SELECT Teams_scrape.id, Players.height FROM Players JOIN Teams_scrape ON Players.team_id = Teams_scrape.id"
    )
    li = cur.fetchall()
    height_dict = {}
    for item in li:
        if item[0] in height_dict:
            temp = height_dict[item[0]]
            height_dict[item[0]]= ((temp + item[1])/2)
        else:
            if item[0] == 1:
                height_dict[item[0]] = item[1]
            else:
                val2 = cur.execute(
                    "UPDATE Teams_scrape SET team_chance = ? WHERE id = ?", (height_dict[item[0] -1], item[0] -1, )
                )
                conn.commit()
                height_dict[item[0]] = item[1]
    get_last_key = list(height_dict.keys())[-1]
    val3 = cur.execute(
        "UPDATE Teams_scrape SET team_chance = ? WHERE id = ?", (height_dict[get_last_key], get_last_key, )
    )
    conn.commit()

def write_regions_to_txt(conn, cur):
    with open('calcs.txt', 'w') as f:
        f.write('Teams in each region:\n')
        val = cur.execute(
            "SELECT Teams_scrape.name, Regions.region FROM Teams_scrape JOIN Regions ON Teams_scrape.region = Regions.id"
        )
        data = cur.fetchall()
        dict = {}
        for item in data:
            if item[1] in dict:
                dict[item[1]].append(item[0])
            else:
                dict[item[1]] = []
                dict[item[1]].append(item[0])
        for item2 in dict:
            f.write('\n\n' + item2 + ':\n--------------------------------------------------------------\n')
            for item3 in dict[item2]:
                f.write(item3 + '\n')
        f.write('\n\n\n\n')

def write_rosters_to_txt(conn, cur):
    with open('calcs.txt', 'a') as f:
        f.write('Rosters:\n')
        val = cur.execute(
            "SELECT Players.last_first_name, Teams_scrape.name, Teams_scrape.team_chance FROM Players JOIN Teams_scrape ON Players.team_id = Teams_scrape.id"
        )
        data = cur.fetchall()
        dict = {}
        for item in data:
            tup = (item[1], item[2])
            if tup in dict:
                dict[tup].append(item[0])
            else:
                dict[tup] = []
                dict[tup].append(item[0])
        for item2 in dict:
            f.write('\n\n' + item2[0] + ':\nAvg Height: ' + str(item2[1])+ ' inches \n--------------------------------------------------------------\n')
            for item3 in dict[item2]:
                f.write(item3 + '\n')

def visualize_write_team_heights_average(conn, cur):
    val = cur.execute(
        "SELECT name, team_chance FROM Teams_scrape ORDER BY team_chance DESC"
    )
    li = cur.fetchall()
    val2 = cur.execute(
        "SELECT Regions.region, Teams_scrape.team_chance FROM Regions JOIN Teams_scrape ON Teams_scrape.region = Regions.id ORDER BY Teams_scrape.team_chance DESC"
    )
    li2 = cur.fetchall()

    taller = li2[:31]
    shorter = li2[32:]

    taller_dict = {}
    shorter_dict = {}
    all_dict = {}

    for piece in li2:
        if piece[0] in all_dict:
            all_dict[piece[0]] += piece[1]
        else:
            all_dict[piece[0]] = piece[1]

    for piece in taller:
        if piece[0] in taller_dict:
            taller_dict[piece[0]] += 1
        else:
            taller_dict[piece[0]] = 1
    
    for piece in shorter:
        if piece[0] in shorter_dict:
            shorter_dict[piece[0]] += 1
        else:
            shorter_dict[piece[0]] = 1

    #pie plot 
    plt.pie([x*100 for x in all_dict.values()],labels=[x for x in all_dict.keys()],autopct='%0.1f',explode=[0,0.1,0,0]) 

    #label the plot 
    plt.title('Percentage Per Region of Overall Height \n Across all March Madness Teams \n (The Tallest Region)') 
    plt.show()
    #pie plot 
    plt.pie([x*100 for x in taller_dict.values()],labels=[x for x in taller_dict.keys()],autopct='%0.1f',explode=[0.1,0.1,0,0.1]) 

    #label the plot 
    plt.title('Region(s) with the Most Teams in Taller Category') 
    plt.show()

    plt.pie([x*100 for x in shorter_dict.values()],labels=[x for x in shorter_dict.keys()],autopct='%0.1f',explode=[0,0.1,0,0]) 

    #label the plot 
    plt.title('Region(s) with the Most Teams in Shorter Category') 
    plt.show()

    x_axis = []
    y_axis = []

    for item in li:
        name = item[0].replace(" men's basketball team", '')
        name2 = re.findall('\D+', name)
        x_axis.append(name2[1])
        y_axis.append(item[1])

    plt.barh(x_axis, y_axis, color = 'green', align = 'edge')
    plt.title('Average Height of March Madness Basketball Teams Per Team')
    plt.ylabel('Schools')
    plt.xlabel('Average Height (inches)')
    plt.show()


if __name__ == '__main__':
    conn, cur = open_db('March_Madness.db')
    update_team_chance_col(conn, cur)
    write_regions_to_txt(conn, cur)
    write_rosters_to_txt(conn, cur)
    visualize_write_team_heights_average(conn, cur)