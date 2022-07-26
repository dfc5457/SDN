import sqlite3
from venv import create
from database import *

# connect to SQL lite
conn = sqlite3.connect('test.db')
c = conn.cursor()
c.execute("DROP TABLE IF EXISTS pending_bet")
conn.commit()

c.execute(create_pending_bets)

# c.execute("INSERT INTO pending_bet (rawContent,contentSource,contentCreatedDate,betGid,betType,betOdds,betPick,betUnit,betDate,capperId,sourceId) VALUES ('aaabb', 'cfwee', 'conten56u56dDate','bghgfid','bejghpe','9990dds','b5433k','rgethit','betrht','thesystempicks',108)")
# c.execute("INSERT INTO pending_bet (rawContent,contentSource,contentCreatedDate,betGid,betType,betOdds,betPick,betUnit,betDate,capperId,sourceId) VALUES ('aaabb', 'cfwee', 'conten56u56dDate','bghgfid','bejghpe','9990dds','b5433k','rgethit','betrht','thesystempicks',106)")
conn.commit()

conn.close()


