import sqlite3
import time


def check_finger(user_id):
    con_to_db = sqlite3.connect("Cards.db")
    cursor = con_to_db.cursor()
    query_search = "SELECT finger_num FROM cards WHERE card_num=?"
    while True:
        # поиск образов в контроллере
        print("Please input user finger id")
        finger_id = input()
        cursor.execute(query_search, finger_id)
