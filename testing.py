from datetime import date
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
from time import sleep
from bet import *
from database import *



# class that scrapes text from an image on instagram from a specific account and sorts text to get the bets
class Scraper:

    def __init__(self,target,date):
        self.target = target
        self.list =[]
        self.login(login_user,login_password)
        self.open_target_profile(self.target)
        print("successfully completed")
        self.driver.close()
        print("sorting through text now...")

        self.sortBet(self.target,date)


    # login to profile 
    def login(self,username,password):
        PATH = r"C:\Users\danie\OneDrive\Desktop\SDN\chromedriver.exe"
        # s = Service(PATH)
        # self.driver = webdriver.Chrome(service = s)
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.get("https://www.instagram.com/")
        sleep(5)
        user_input = self.driver.find_element(By.XPATH,'//*[@id="loginForm"]/div/div[1]/div/label/input')
        user_input.send_keys(username)
        sleep(1)
        password_input = self.driver.find_element(By.XPATH,'//*[@id="loginForm"]/div/div[2]/div/label/input')
        password_input.send_keys(password)
        sleep(1)
        login = self.driver.find_element(By.XPATH,'//*[@id="loginForm"]/div/div[3]').click()
        print("loggining in......")
        sleep(3)
        self.driver.find_element(By.XPATH,"//button[contains(text(), 'Not Now')]").click()
        sleep(3)
        self.driver.find_element(By.XPATH,"//button[contains(text(), 'Not Now')]").click()
        sleep(2)
        print("successfully logged in....")
        
    # open a profile account
    def open_target_profile(self,target):  
        target_profile = target
        main_url = 'https://www.instagram.com/'
        target_profile_url  = main_url + target_profile
        print('Redirecting to {} profile...'.format(target_profile))
        self.driver.get(target_profile_url)
        sleep(5)
        print("successfully redirected....")
        self.img_text()
      

    def img_text(self):
        html = self.driver.page_source
        soup = bs(html, "lxml")
        
        images = soup.find_all('img', alt=True)
        for img in images:
            line = img['alt']
            img_url = img['src']
            postedTime = line[line.find('on') + 3: line.find('.')]
            if "text that says" in line:
                self.list.append((line, img_url, postedTime))

        
    def formatLine(self,line):
        while line.find("(") != -1:
            line = line.replace("(","")
        while line.find(")") != -1:
            line = line.replace(")","")
        while line.find("[") != -1:
            line = line.replace("[","")
        while line.find("]") != -1:
            line = line.replace("]","")
        while line.find("'") != -1:
            line = line.replace("'","")
        if line[line.find("-") - 1] != "":
            line = line.replace("-"," -")
        # while line.find('Picks') != -1:
        #     line = line[line.find('Picks') + 5 :].strip()
        # while line.find("............") != -1:
        #     line = line.replace("............","")
        return line

    

    # function takes in bet object and line of text
    # sorts through known values to get the next possible bet in the line
    def getTemp(self,units,overUnder,odds,spread,line):
        val = ""
        minVal = len(line)

        for i in [units,'ML',overUnder,odds,spread]:
            if line.find(i) < minVal and line.find(i) != 0 and line.find(i) != -1:
                minVal = line.find(i)
                val = i

        temp = ""
        if units == val:
            if units == "1u" and line.find("1น") != -1:
                temp = line[:(line.find("1น") + 2)] 
            else:
                temp = line[:(line.find(units) + len(units) + 1)]
        elif spread == val:
            temp = line[:line.find(spread) + len(spread) + 5]
        elif val:
            temp = line[:(line.find(val) + len(val) + 1)]
        
        print('TEMP: ',temp)
        return temp



    # calls the bet class,
    # sends in the list of text scraped from the posts
    # sorts through the list to determine the bets
    def sortBet(self, target, date):
        betObj = Bet(target)
        try:
            maxId = int(max([x[0] for x in sourceId(target)]))   
        except ValueError:
            maxId = 100
        updatedId = maxId    


        for entry in self.list:
            line = entry[0]
            url = entry[1]
            postedDate = entry[2]
            currentId = int(str(url)[str(url).find('cat') + 4 : str(url).find('cat=') + 7])
            exclusive = ""

            if (date == postedDate) or (date == 'July 1, 2022'):
                if currentId > updatedId:
                    updatedId = currentId     

                line = line[line.find('text that says') + 15:]
                line = self.formatLine(line) 

                print('LINE: ',line)

                
                if target == 'vipcappinduck' and 'Exclusive Parlay' in line:
                    exclusive = line[line.find('Exclusive') + 17 :]
                    line = line[:line.find('Exclusive')]

        
                betObj.getUnits(line)
                betObj.getOdds(line)
                betObj.getOverUnder(line)
                betObj.getNumber(line)

                temp = self.getTemp(betObj.units,betObj.overUnder,betObj.odds,betObj.spreadValue,line)
                print('FIRST TEMP: ', temp)
            
                while temp != "":

                    betObj.getUnits(temp)
                    betObj.getOverUnder(temp)
                    betObj.getOdds(temp)
                    betObj.getNumber(temp)
                    betObj.getPick(temp)
                    betObj.getBetType(temp)
                    betObj.removeEmoji()


                    # use this section to call specific functions for each capper
                    if target == 'bear_betting':
                        betObj.bearbetting()
                    elif target == 'thesystempicks':
                        betObj.systempicks()
                    elif target == 'vipcappinduck':
                        betObj.cappinduck()
                    

                    print("units: ",betObj.units)
                    print("pick: ",betObj.pick)
                    print("over/under: ",betObj.overUnder)
                    print("spread: ", betObj.spreadValue)
                    print("type: ", betObj.betType)
                    print("odds: ",betObj.odds)

                    betObj.updateTable(target,url,postedDate,currentId)


                    # reset the variables
                    
                    betObj.units = ""
                    betObj.pick = ""
                    betObj.overUnder = ""
                    betObj.betType = ""
                    betObj.odds = "" 

                    line = line[line.find(temp) + len(temp) : ]
                    print('CURRENT LINE: ',line)

                    betObj.getUnits(line)
                    betObj.getOdds(line)
                    betObj.getOverUnder(line)
                    betObj.getNumber(line)

                
                    temp = self.getTemp(betObj.units,betObj.overUnder,betObj.odds,betObj.spreadValue,line)

                    if not temp and exclusive:                               
                        betObj.getOdds(exclusive)
                        betObj.getOverUnder(exclusive)
                        betObj.getNumber(exclusive)

                        temp = self.getTemp(betObj,exclusive)
                        betObj.betType = "parlay"

                        exclusive = exclusive.replace(temp,"")

                            

            

        return updatedId


today = date.today().strftime("%B %d, %Y") 
day = 'July 30, 2022' #default all posts that are pulled
# 30

#Scraper('vipcappinduck',day)
#Scraper('fanfanpodcast',day)
#Scraper('bear_betting',day)

Scraper('thesystempicks',day)

