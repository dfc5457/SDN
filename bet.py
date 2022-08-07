from distutils.errors import LinkError
from multiprocessing import connection
import csv
from typing import Type
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

from variables import *
from datetime import date
from game import *
from database import *

# class objects has all of the methods to take in a line of text and sort out specifc parts of a bet 
# objects all have the methods to update a database and csv files with the found values
class Bet:
    # constant values for an entire post
    date = date.today().strftime("%Y-%m-%d") 
    pick_list = []
    pick = ""
    odds = ""
    betType = ""
    link = ""
    source = ""    

    # create the values that change for each line of the text
    def __init__(self,target):
        self.final = []
        self.target = target
        self.spreadValue = ""
        self.overUnder = ""
        self.units = "" 
        self.gameID = 0
    
    # takes in one line of the text and searches for units
    def getUnits(self,line):
        split_words = line.split()
        for word in split_words:
            word = word.lower().strip(",")
            try:
                if word.endswith('u') and (float(word[:len(word) - 1])) or word.endswith('น'):
                    if word.endswith('น'):
                        word = word.replace('น','u')
                    self.units = word
                    return

                if word.endswith('u') and ("-" in word or "+" in word) and (float(word[1:len(word) - 1])):
                    self.units = word
                    return

                if word == 'units' or word[:5] == 'units':
                    self.units = previous_word + " " + word
                    return

            except ValueError:
                pass

            previous_word = word




    # takes in a line of text and checks each word for over/under values    
    # sets the pick and type values
    def getOverUnder(self,line):
        previous = ""
        split_words = line.split()

        for word in split_words:
        
            if word == 'Under' or word == 'Over' or word == 'under' or word == 'over':
                previous = word
            
            word = word.lower().strip(",").strip()
            try:
                if previous != "" and float(word):
                    self.pick = line
                    self.betType = "total"
                    self.overUnder = previous + " " + word
         
                    return

                elif (word.startswith('o') or word.startswith('0')) and (float(word[1:]))  or word.startswith('u') and \
                        (float(word[1:])):
                    self.pick = line
                    self.betType = "total"
                    self.overUnder = word
                    return

            except ValueError:
                pass

        



    # checks the current pick and matches it to a game id from the endpoint
    def getGameID(self):
        data = get_response_json(url)
        today = date.today().strftime("%d %b %Y")
        # game id
        for entry in data['data']:
            if (entry['date'][5:16] == today):
                team_split = entry['a_team'].replace(',','').lower().split() + entry['h_team'].replace(',','').lower().split()
                for i in team_split:
                     if i in self.pick.lower():
                        self.gameID = entry['gid']

    
    # sort the current pick and replace any emojis or non-letters with a space
    def removeEmoji(self):
        # get rid of emojis/ extra words
        for word in self.pick:
            for letter in word:
               if (ord(letter) > 128 and ord(letter) != 3609) or letter == '@':
                self.pick = self.pick.replace(letter, "").strip() 
            if '#' in word:
                self.pick.replace(word,"")
 

    # takes in a line from the text and sorts for any missed picks
    def getPick(self,line):
        if ('vs') in line or ('vs.'):
            self.pick == line
        if self.pick == "" and self.units in line:
            self.pick == line
        for word in line.split():
            if (self.units in line) and (word in player_keywords): # checks if the line with the units is a pick
                self. pick = line


        
        # check for keywords/ sports betting platforms for promo tweets
        for i in platforms:
            if i in line:
                self.pick = ""

        try:
            if float(self.pick):
                self.pick = ""
        except ValueError:
            pass

    # takes in a line of the text and filters the numbers to get the odds
    def getOdds(self,line):
        temp_line = line.split()
        for word in temp_line:
            word = word.strip().lower()
            try:
                # odds
                if len(word) == 5 and float(word[1:4]) and  "." not in word and (not word.startswith("0")) and (not word.startswith("u") and (not word.startswith("o"))):  # end of line
                    self.odds = word[:4]
                    self.pick = line
                    return
                if len(word[1:]) >= 3 and float(word[1:]) and "." not in word and (not word.startswith("0")) and (not word.startswith("u")) and (not word.startswith("o")):
                    self.odds = word
                    self.pick = line
                    return
                if len(word) == 3 and float(word):
                    self.odds = word
                    self.pick = line
                    return
            except ValueError:
                pass
    
        
    # takes in a line and sorts through all the numbers
    # checks for spread values using +/- , and sets the pick and value if found
    def getNumber(self,line):
        # filter the numbers
        temp_line = line.split()
        for word in temp_line:
            word = word.strip()
            if word.endswith("."):
                word = word[:-1]

            # spread value for player props
            if word.endswith("+"):
                self.spreadValue = word
                self.pick = line[:line.find(word) + len(word) + 5]
                return
                
            try:
                if float(word[word.find("-"):]) :
                    word = word[word.find("-"):]
                elif float(word[word.find("+"):]) :
                    word = word[word.find("+"):]
            except ValueError:
                pass

            word = word.strip().lower()

            if word.startswith("+") or word.startswith("-"):
                # spread bet
                try:
                    if len(word[1:]) < 3 and float(word[1:]):
                        self.spreadValue = word
                        self.betType = "spread"
                        self.pick = line
                        return

                    elif len(word[1:]) <= 3 and "." in word:
                        self.spreadValue = word
                        self.betType = "spread"
                        self.pick = line
                        return
                    
                except ValueError:
                    pass



            # spread values without a + or -
            try:
                if "." in word and float(word):
                    self.spreadValue = word
                    self.betType = "spread"
                    self.pick = line
                    return
                    
            except ValueError:
                pass

          


    # takes in a line of a text and determines the bet type either from keywords in the line or from known class variables    
    # checks for moneyline, parlay and sets pick and type if found   
    # checks for game prop, player prop using keywords from the variables file
    # checks for total using known class variables
    def getBetType(self,line):
        # bet types
        temp_line = line.lower()
        if "money line" in temp_line or "moneyline" in temp_line or "ml" in temp_line:
            self.betType = "money line"
            if len(line.strip()) != 2:
                self.pick = line
        if "game prop" in temp_line or "gameprop" in temp_line:
            self.betType = "game prop"
        if "player prop" in temp_line or "playerprop" in temp_line:
            self.betType = "player prop"
        if "straight bet" in temp_line:
            self.betType == "straight"
        if "parlay" in temp_line:
            self.betType = "parlay"

        # total
        if self.odds != "" and self.spreadValue == "" and self.betType == "":
            self.betType = "total"
        
        # player props
        for word in line.split():
            word = word.lower()
            if word in player_keywords:
                self.betType = "player prop"
            if word in game_keywords:
                self.pick = line
                self.betType = "game prop"
        
        if self.betType == "total" and any(x.isdigit() for x in self.pick) == False and "https" not in self.pick:
            self.pick += self.link
            self.betType = "player/game prop"

                
            
    # update a sample table for easy readability
    def updateTable(self,target,url,postedDate,sourceId):

        """ **** insert here ***** """
    

        entries = readDB(target) # reads pick,odds,units from database

        # formats the pick to remove the known values
        self.pick = self.pick.replace(self.odds, "").replace("1น","").replace(self.units, "").strip()
        self.pick = self.pick.replace(postedDate[postedDate.find(",")-1:], "").strip()

        if self.pick.find(postedDate[:postedDate.find(",")]) != -1:
            self.pick = self.pick.replace(postedDate[:postedDate.find(",")], "").strip()
        

        # reads the database, to the database
        if (self.pick,self.odds,self.units) in entries:
            return
        
        # if the varaibales are satified, a new bet entry is created and appended to the final list 
        elif self.betType != "" and self.pick != "" and (self.units != "" or self.odds != "" or self.spreadValue != "") or (self.odds == "" and target == 'fanfanpodcast') or (self.betType == "money line" and target == "vipcappinduck") or (self.overUnder != "" and target == "vipcappinduck"):        
            writeDB(target,url,'instagram',postedDate, self.gameID,self.betType,self.odds,self.pick,self.units,self.date,self.date,sourceId)
            

    # capper functions to fix any constant formatting problems
    def cappinduck(self):
        self.pick = self.pick[36:]
    
    def bearbetting(self):
        self.pick = self.pick.replace("Picks ","").strip()

    
    def fanpodcast(self):
        self.pick = self.pick[84:self.pick.find('#')]
    
    def systempicks(self):
        self.pick = self.pick.replace('DAILY CARD',"").strip()
        if ":" in self.pick:
            self.pick = self.pick[self.pick.find(":") + 2: ]
        if "," in self.pick:
            self.pick = self.pick[self.pick.find(",") + 1 :]
        self.pick = self.pick.replace("The System Picks.","")

    def cappinduck(self):
        if self.pick.find('Exclusive Picks') != -1:
            self.pick = self.pick[self.pick.find('Exclusive Picks') + 15 :].strip()
    
