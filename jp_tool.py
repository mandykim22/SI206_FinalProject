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

def main():
    con = sqlite3.connect("questions.db")
    cur = con.cursor()

    # section 1 begin
    last_category = 0
    with open("./last_category.txt") as fr:
        last_category = int(fr.readline())

    get_questions_from_category(con, cur, last_category)

    with open("./last_category.txt", "w") as fw:
        fw.write(str(last_category+25))
    # section 1 end

    # section 4 begin
    top_categories = cur.execute("SELECT c.category, c.question_count, AVG(q.value) FROM questions q INNER JOIN categories c ON q.category_id=c.id GROUP BY q.category_id ORDER BY c.question_count DESC").fetchall()[0:10]
    # section 4 end

    # section 2 begin
    with open('calculations.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',')
        spamwriter.writerow(["Category", "Question Count", "Average Value"])
        for top_category in top_categories:
            spamwriter.writerow([top_category[0], top_category[1], top_category[2]])
    # section 2 end

    # section 3 begin
    categories = [tup[0] for tup in top_categories]
    question_counts = [tup[1] for tup in top_categories]
    avg_points = [tup[2] for tup in top_categories]
    colors = ["red", "orange", "yellow", "lime", "green", "lightskyblue", "blue", "purple", "grey", "black"]

    plt.barh(categories, question_counts, color=colors)
    plt.ylabel("Categories")
    plt.xlabel("# of Questions")
    plt.title("# of Questions in each Jeaproady Category")
    plt.show()

    plt.scatter(categories, avg_points, c=colors)
    plt.ylabel("Categories")
    plt.xlabel("Average Value of Questions")
    plt.title("Average Value of Questions in each Jeaproady Category")
    plt.show()
    # section 3 end

if __name__ == "__main__":
    main()