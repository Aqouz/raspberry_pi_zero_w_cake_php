#!/usr/bin/env python3
from tm1637 import TM1637
import includes_display
# Setup Display
DIO=2
CLK=3
tm = TM1637(CLK, DIO)
tm.brightness(5)


import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

import time

#mysql database
import MySQLdb
try:
    db = MySQLdb.connect(host="localhost", user="phpmyadmin", passwd="pi_root1", db="hackathon_kicker_db")
    cursor = db.cursor()
except:
    print "Cannot connect to database"


#Variable definitions
score_home = 0
score_guest = 0
#lights = 0 -> button; lights = 1 -> light sensor
lights = 1
max_score = 6
score_timeout = 1000
game_ID = 0

#reset button
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#goal counter home
if lights == 0:
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
else:
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#goal counter guest
if lights == 0:
    GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
else:
    GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#clear display and data at start
#add clear data here
includes_display.show_score(tm,0,0)
#at initial start: read max game_ID from database
try:
    #cursor.execute("SELECT MAX(game_id) FROM `games` WHERE 1")
    #max_id = cursor.fetchone()
    #print(max_id[0])
    #game_ID = max_id[0] + 1
    cursor.execute("INSERT INTO `games` (name_home, score_home, score_guest, name_guest) VALUES ('', 0, 0, '')")
    db.commit()
except:
    print "No DB connection or failure - init"

def write_score(score_home,score_guest,db,cursor):
    #write to file
    file_score  = open("gamescore", "w")
    concat_score = str(score_home) + " " + str(score_guest) + " - " + time.strftime("%c")+ "\n"
    file_score.write(concat_score)
    file_score.close()
    #update database value
    try:
        cursor.execute("SELECT MAX(game_id) FROM `games` WHERE 1")
        max_id = cursor.fetchone()
        #print("UPDATE `games` SET score_home = 3, score_guest = 7 WHERE game_id = " + max_id[0])
        #print(max_id[0])
        #print("UPDATE `games` SET score_home = {}, score_guest = {} WHERE game_id = {}".format(score_home,score_guest,max_id[0]))
        cursor.execute("UPDATE `games` SET score_home = {}, score_guest = {} WHERE game_id = {}".format(score_home,score_guest,max_id[0]))
        db.commit()
    except:
        print "No DB connection or failure - score"

def reset_btn_pressed(channel):
    print "Game will be reset to 0:0"
    global score_home
    global score_guest
    global cursor
    global db
    score_home = 0
    score_guest = 0
    includes_display.show_score(tm,score_home,score_guest)
    #create new game
    try:
        cursor.execute("INSERT INTO `games` (name_home, score_home, score_guest, name_guest) VALUES ('', 0, 0, '')")
        db.commit()
    except:
        print "No DB connection or failure - new game"

    write_score(score_home,score_guest,db,cursor)


def home_scores(channel):
    global score_home
    global score_guest
    global cursor
    global db
    if score_home == max_score or score_guest == max_score:
        return()
    print "Goal for home team"
    score_home = score_home + 1
    print(score_home,score_guest)
    includes_display.show_score(tm,score_home,score_guest)
    if score_home == max_score:
        blink_score(tm,score_home,score_guest, "Home")
    write_score(score_home,score_guest,db,cursor)

def guest_scores(channel):
    global score_home
    global score_guest
    global cursor
    global db
    if score_home == max_score or score_guest == max_score:
        return()
    print "Goal for guest team"
    score_guest = score_guest + 1
    print(score_home,score_guest)
    includes_display.show_score(tm,score_home,score_guest)
    if score_guest == max_score:
        blink_score(tm,score_home,score_guest, "Guest")
    write_score(score_home,score_guest,db,cursor)


def blink_score(tm,score_home,score_guest,winning_team):
    print "We have a winner: " + winning_team
    for x in range(3):
        tm.brightness(0)
        time.sleep(1)
        tm.brightness(5)
        time.sleep(1)
        #better blinking


GPIO.add_event_detect(4, GPIO.FALLING, callback=reset_btn_pressed, bouncetime=score_timeout)
if lights == 0:
    GPIO.add_event_detect(17, GPIO.FALLING, callback=home_scores, bouncetime=score_timeout)
else:
    GPIO.add_event_detect(17, GPIO.RISING, callback=home_scores, bouncetime=score_timeout)
if lights == 0:
    GPIO.add_event_detect(27, GPIO.FALLING, callback=guest_scores, bouncetime=score_timeout)
else:
    GPIO.add_event_detect(27, GPIO.RISING, callback=guest_scores, bouncetime=score_timeout)


#error handling and script exit
#try:
#    raw_input("Press Enter to exit\n>")
#
#except KeyboardInterrupt:
#    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
#GPIO.cleanup()           # clean up GPIO on normal exit
while True:
    pass
