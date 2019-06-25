#!/usr/bin/env python3

import serial
import sqlite3
import subprocess
import time


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


def check_finger(card_code, finger_code):
    con_to_db = sqlite3.connect("Cards.db")
    cursor = con_to_db.cursor()
    query_search = "SELECT user_id FROM fingers WHERE finger_id=?"
    cursor.execute(query_search, (finger_code,))
    user_id = cursor.fetchone()
    query_search = "SELECT id FROM cards WHERE card_code=?, user_id=?"
    cursor.execute(query_search, (card_code,user_id))
    result = cursor.fetchone()
    con_to_db.close()
    if result is None:
        return False
    else:
        return True


cardFounded = True
ser = serial.Serial('/dev/ttyS1', 9600, timeout=30)
print("Connection open on: " + ser.name)
number = "NULL"
bashCommand = "gpio write 1 0"
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
while True:
    out = ser.readline()
    if not out or out == "exit":
        break
    inputStr = str(out)
    if cardFounded:
        getNumber = inputStr.find("Card readed: 32bits")
        if getNumber > 0:
            number = inputStr[getNumber+22:getNumber+30]
            number = number[6] + number[7] + number[4] + number[5] + number[2] + number[3] + number[0] + number[1]
            if check_card(number):
                cardFounded = False
                tryCount = 0
                bashCommand = "gpio write 1 1"
                process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
                output, error = process.communicate()
                print("Found card:" + number)
            else:
                print("Found unknown card:" + number)
    else:
        stopReading = inputStr.find("Timeout reading finger")
        if stopReading > 0:
            cardFounded = True
            bashCommand = "gpio write 1 0"
            process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            print("Timeout reading finger")
        else:
            getFinger = inputStr.find("Found ID #")
            if getFinger > 0:
                image = inputStr[getFinger+10:]
                if check_finger(number, image):
                    cardFounded = True
                    print("Access denied")
                    bashCommand = "gpio write 1 0"
                    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
                    output, error = process.communicate()
                    time.sleep(1)


                else:
                    print("Found unknown finger")
print("Connection close on: " + ser.name)
ser.close()