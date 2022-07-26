from bet import *
from variables import*
import sqlite3


def writeDB(capperId,rawcontent, contentSource, contentCreatedDate,betGid,betType,betOdds, betPick, betUnit, betDate,reviewedTime,sourceId):
    # connect to SQL lite
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    #c.execute("DROP TABLE IF EXISTS test")
    #conn.commit()
    v = (rawcontent, contentSource, contentCreatedDate,betGid,betType,betOdds, betPick, betUnit, betDate,capperId,reviewedTime,sourceId)
    sql = "INSERT INTO pending_bet (rawContent,contentSource,contentCreatedDate,betGid,betType,betOdds,betPick,betUnit,betDate,capperId,reviewedTime,sourceId) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
    c.execute(sql,v)

    
    conn.commit()
    conn.close()

def readDB(user):
    # connect to SQL lite
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    print("reading database.....")
    #read all the picks from table for a specific user

    c.execute("SELECT betPick, betOdds, betUnit FROM pending_bet WHERE capperId = ? ", (user,))
    conn.commit()
        
    entries = c.fetchall()
    conn.commit()

    conn.close()
    return entries



def updateDB(user,type,units,odds,pick,gid,contentCreatedDate):
    # connect to SQL lite
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    print("updating now...........")
    # update the values if the pick is found in the table
    sql = "UPDATE pending_bet SET (betType,betUnit,betOdds,betGid) = (?,?,?,?) WHERE (capperId,betPick,contentCreatedDate) = (?,?,?)"
    v = (type,units,odds,gid,user,pick,contentCreatedDate)
    c.execute(sql,v)
    
    conn.commit()
    conn.close()

def sourceId(user):
    # connect to SQL lite
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    print("reading ids.....")
    #read all the picks from table for a specific user

    c.execute("SELECT sourceId FROM pending_bet WHERE capperId = ? ", (user,))
    conn.commit()

    entries = c.fetchall()

    conn.commit()

    conn.close()
    return entries

create_pending_bets = """
    CREATE TABLE IF NOT EXISTS `pending_bet` (
    `id` int INTEGER PRIMARY KEY,
    `rawContent` text,
    `contentSource` text,
    `contentCreatedDate` varchar(70) DEFAULT NULL,
    `hitOrMiss` tinyint(1) DEFAULT NULL,
    `betGid` int DEFAULT NULL,
    `betLeague` varchar(50) DEFAULT NULL,
    `betType` varchar(100) DEFAULT NULL,
    `betLine` decimal(10,0) DEFAULT NULL,
    `betOdds` decimal(10,0) DEFAULT NULL,
    `betPick` text,
    `betUnit` decimal(10,0) DEFAULT NULL,
    `betDate` date DEFAULT NULL,
    `capperId` int DEFAULT NULL,
    `isPremium` tinyint(1) DEFAULT NULL,
    `reviewedTime` varchar(70) DEFAULT NULL,
    `sourceId` varchar(200) DEFAULT NULL);
    """