import requests
import matplotlib.pyplot as plt
import sqlite3
import csv

def get_questions_from_category(con, cur, category):
    for i in range(category, category + 25):
        print(i)
        x = requests.get("https://jservice.io/api/clues", params={"category": i})
        json_ret = x.json()
        if(len(json_ret) == 0):
            continue
        cur.execute("INSERT INTO categories (id, category, question_count) VALUES (?, ?, ?)", (json_ret[0]["category"]["id"], json_ret[0]["category"]["title"], json_ret[0]["category"]["clues_count"]))
        for question in json_ret:
            cur.execute("INSERT INTO questions (id, value, question, category_id) VALUES (?, ?, ?, ?)", (question["id"], question["value"], question["question"], question["category"]["id"]))
    con.commit()