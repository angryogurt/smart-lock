import sqlite3


def check_card(card_code):
    con_to_db = sqlite3.connect("Cards.db")
    cursor = con_to_db.cursor()
    query_search = "SELECT user_id FROM cards WHERE card_code=?"
    cursor.execute(query_search, (card_code,))
    user_id = cursor.fetchone()
    con_to_db.close()
    if user_id is None:
        return False
    else:
        return True


def add_card(user_id, card_code):
    con_to_db = sqlite3.connect("Cards.db")
    cursor = con_to_db.cursor()
    query = "INSERT INTO cards(card_code,user_id) VALUES (?,?)"
    cursor.execute(query, [card_code, user_id])
    con_to_db.commit()
    con_to_db.close()


def del_card(card_code):
    con_to_db = sqlite3.connect("Cards.db")
    cursor = con_to_db.cursor()
    query = "DELETE FROM cards WHERE card_code = ?"
    cursor.execute(query, card_code)
    con_to_db.commit()
    con_to_db.close()