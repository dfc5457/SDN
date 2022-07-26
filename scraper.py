from datetime import date
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.common.exceptions
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
        s = Service(PATH)
        self.driver = webdriver.Chrome(service = s)
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
        return line



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

            if (date == postedDate) or (date == 'July 1, 2022'):
                if currentId > updatedId:
                    updatedId = currentId     

                
                line = line[line.find('text that says') + 15:]
                line = self.formatLine(line) 
                print('LINE: ',line)

                if target in multiple_bets:
                                    
                    betObj.getUnits(line)
                    print('inital units:' ,betObj.units)
                    betObj.getOdds(line)
                    print('inital odds:' ,betObj.odds)
                    
                    if betObj.units != "":
                        if betObj.units == "1u" and line.find("1น") != -1:
                            temp = line[:(line.find("1น") + 2)] 
                        else:
                            temp = line[:(line.find(betObj.units) + len(betObj.units) + 1)]
                    elif betObj.odds != "":
                        temp = line[:(line.find(betObj.odds) + len(betObj.odds) + 1)]
                    elif 'parlay' in line.lower():
                        temp = line
                    elif 'ML' in line:
                        temp = line[:(line.find('ML')) + 2]
                       
                    print('first line: ',temp)
                        
                    
                    
                    while temp != "":

                        #betObj.readFile(target,url,postedDate,temp)
                        betObj.getUnits(temp)
                        betObj.getOverUnder(temp)
                        betObj.getOdds(temp)
                        betObj.getNumber(temp)
                        betObj.getBetType(temp)
                        betObj.getPick(temp)
                        betObj.removeEmoji()
                        betObj.getGameID()

                        #betObj.readFile(target,url,postedDate,temp)
                       
                        

                        # use this section to call specific functions for each capper
                        if target == 'bear_betting':
                            betObj.bearbetting()
                        if target == 'thesystempicks':
                            betObj.systempicks()
                        
                        betObj.updateTable(target,url,postedDate,currentId)
                        

                        print('pick: ', betObj.pick)
                        # print('type: ', betObj.betType)
                        # print('odds: ', betObj.odds)
                        print('units: ',betObj.units)
                        # print('over/under: ', betObj.overUnder)
                        
                       
                        betObj.betType = ""
                        betObj.odds = ""
                        betObj.units = ""
                        betObj.pick = ""
                        betObj.overUnder = ""

                        line = line[line.find(temp) + len(temp) : ]
                    
                        betObj.getUnits(line)
                        betObj.getOdds(line)
                        

                        if betObj.units != "":
                            if betObj.units == "1u" and line.find("1น") != -1:
                                temp = line[:(line.find("1น") + 2)]
                            else:
                                temp = line[:(line.find(betObj.units) + len(betObj.units) + 1)]
                        elif betObj.odds != "":
                            temp = line[:(line.find(betObj.odds) + len(betObj.odds) + 1)]
                        elif 'parlay' in line.lower():
                            temp = line
                        elif 'ML' in line:
                            temp = line[:(line.find('ML')) + 2]

                
                        else:
                            break

                        print('next: ',temp)
                        

                    print("------------------------------------------------------------------------------------------------------------------------")

                else:
                    #betObj.readFile(target,url,postedDate,line)
                    betObj.getUnits(line)
                    betObj.getOverUnder(line)
                    betObj.getOdds(line)
                    betObj.getNumber(line)
                    betObj.getPick(line)
                    betObj.getBetType(line)
                    betObj.removeEmoji()
                    betObj.getGameID()


                    # use this section to call specific functions for each capper
                    if target == 'fanfanpodcast':
                        betObj.fanpodcast()
                    elif target == 'cappinduck':
                        betObj.cappinduck()


                    betObj.updateTable(target,url,postedDate,currentId)
                    #betObj.readFile(target,url,postedDate,line)
            #betObj.writeFile()

        return updatedId


today = date.today().strftime("%B %d, %Y")
day = 'July 1, 2022'
Scraper('thesystempicks',day)



