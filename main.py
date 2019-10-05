#!/usr/bin/env python3

import serial
import sqlite3
import subprocess


def find_users_by_card(card_code):
    con_to_db = sqlite3.connect("Cards.db")
    cursor = con_to_db.cursor()
    query_search = "SELECT user FROM users_cards WHERE card=?"
    cursor.execute(query_search, card_code)
    user_ids = cursor.fetchall()
    con_to_db.close()
    return user_ids


def find_fingers_by_user(user_ids):
    con_to_db = sqlite3.connect("Cards.db")
    cursor = con_to_db.cursor()
    query_search = "SELECT finger FROM users_fingers WHERE user IN (?)"
    cursor.execute(query_search, user_ids)
    finger_ids = cursor.fetchall()
    con_to_db.close()
    return finger_ids


def parse_card_number(line):
    get_code = line.find("Card readed: 32bits")
    if get_code > 0:
        number = inputStr[get_code + 22:get_code + 30]
        number = number[6] + number[7] + number[4] + number[5] + number[2] + number[3] + number[0] + number[1]
        return number
    return None


def update_reading_mode(flag):
    if flag:
        command = "gpio write 1 0"
        print("Start reading cards")
    else:
        command = "gpio write 1 1"
        print("Start reading fingers")
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()


card_reading_mode = True
up_time = 1800
ser_speed = 9600
ser_port = '/dev/ttyS1'
ser = serial.Serial(ser_port, ser_speed, timeout=up_time)
print("Connection open on: " + ser.name)
update_reading_mode(card_reading_mode)
fingers = []
while True:
    out = ser.readline()
    if not out or out == "exit":
        break
    inputStr = str(out)
    if card_reading_mode:
        mifare = parse_card_number(inputStr)
        if not (mifare is None):
            print("Found card with Mifare code:" + mifare)
            users = find_users_by_card(mifare)
            if not (users is None):
                fingers = find_fingers_by_user(users)
                if not (fingers is None):
                    card_reading_mode = False
                    update_reading_mode(card_reading_mode)
                else:
                    print("Missing fingerprints of cardholders. Access is denied.")
            else:
                print("This card is not affiliated with any one person. Access is denied.")
    else:
        stopReading = inputStr.find("Timeout reading finger")
        if stopReading > 0:
            card_reading_mode = True
            update_reading_mode(card_reading_mode)
            print("Timeout reading finger")
        else:
            getFinger = inputStr.find("Found ID #")
            if getFinger > 0:
                finger = inputStr[getFinger+10:getFinger+13]
                print("Found finger №{}".format(finger))
                if fingers.count(finger) > 0:
                    print("Access denied")
                    card_reading_mode = True
                    update_reading_mode(card_reading_mode)
                else:
                    print("The entered fingerprint doesn't match the cardholder")
print("Connection close on: " + ser.name)
ser.close()
