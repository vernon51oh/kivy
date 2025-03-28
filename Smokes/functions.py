import pyodbc
from pyodbc import DatabaseError
import configparser
from kivy.logger import Logger
from cryptography.fernet import Fernet
from main import hostOnline, storeOnline


key= 'p3pmgpdNVj413Xlo3YY01XaNlxao2JccH4-gENVxg1c='

config=configparser.ConfigParser()
config.read('smokes.ini')
store=config['store']['storeNumber']

storeDb=config['databases']['storeDb']
storeDbPass = config['databases']['storeDbPass'].encode()
storeDbUser = config['databases']['storeDbUser']

hostDb=config['databases']['hostDb']
hostDbPass = config['databases']['hostDbPass'].encode()
hostDbUser = config['databases']['hostDbUser']

storeDbPassword = Fernet(key).decrypt(storeDbPass).decode()
hostDbPassword = Fernet(key).decrypt(hostDbPass).decode()

Logger.info(f"Connecting to store database {storeDb}")
Logger.info(f"Connecting to host database {hostDb}")
Logger.info(f"Store online: {storeOnline}, Host online: {hostOnline}")
print ('storeOnline',storeOnline)
print ('hostOnline',hostOnline)

try:
    storeDB = pyodbc.connect(f'Driver=ODBC Driver 17 for SQL Server;Server={storeDb};UID={storeDbUser};PWD={storeDbPassword}')
   
    Logger.info("Connected to store databases")
    storeOnline = True
except DatabaseError as e:
    print(f"Database error on store database: {e}")
    Logger.error(f"Database error on store database: {e}")
    storeOnlie = False
    
except pyodbc.Error as e:
    print(f"Pyodbc error on store database: {e}")
    Logger.error(f"Pyodbc erroron store database :{e}")
    storeOnline = False
    

except Exception as e:
    print(f"Error: {e}")
    Logger.error(f"Error: {e}")
    storeOnline = False

try:
    host = pyodbc.connect(f'Driver=ODBC Driver 17 for SQL Server;Server={hostDb};DATABASE=LiveSTORESQL;UID={hostDbUser};PWD={hostDbPassword}')

    Logger.info("Connected to  Host databases")
    hostOnline = True
except DatabaseError as e:
    print(f"Database error: {e}")
    Logger.error(f"Database error on host database: {e}")
    hostOnline = False
    
except pyodbc.Error as e:
    print(f"Pyodbc error: {e}")
    Logger.error(f"Pyodbc error on host database: {e}")
    hostOnline = False

except Exception as e:
    print(f"Error on host database: {e}")
    Logger.error(f"Error on host database: {e}")
    hostOnline = False

def Login(username, password):

    try:
        Logger.info("Checking login credentials")
        Logger.info(f"Store online: {storeOnline}, Host online: {hostOnline}")
        cursor = storeDB.cursor()
        print(username, password)
        print(type(username))
        print(type(password))
        cursor.execute(f"SELECT * FROM CLK_Tab WHERE F1126 = '{username}' AND F1141 = '{password}'")
        Logger.info("Checking login credentials Matched")
        for row in cursor:
            return True
    except DatabaseError as e:
        print(f"Database error: {e}")
        Logger.error(f"Database error: {e}")
        return False


def get_access(username):
    try:
        cursor = storeDB.cursor()
        cursor.execute(f"SELECT  F1142 FROM CLK_Tab WHERE F1126 = '{username}'")
        access=cursor.fetchone()
        Logger.info(f"Access level for {username} is {access[0]}")
        return access[0]
    except DatabaseError as e:
        print(f"Database error: {e}")
        Logger.error(f"Database error: {e}")
        return False
        
def checkStoreDb():
    try:
        store = pyodbc.connect(f'Driver=ODBC Driver 17 for SQL Server;Server={storeDb};UID={storeDbUser};PWD={storeDbPassword}')
    
        Logger.info("Connected to store databases")
        storeOnline = True
        return True
    except DatabaseError as e:
        print(f"Database error on store database: {e}")
        Logger.error(f"Database error on store database: {e}")
        storeOnlie = False
        return False
        
    except pyodbc.Error as e:
        print(f"Pyodbc error on store database: {e}")
        Logger.error(f"Pyodbc erroron store database :{e}")
        storeOnline = False
        return False

    except Exception as e:
        print(f"Error: {e}")
        Logger.error(f"Error: {e}")
        storeOnline = False
        return False

   
class Calculations:
    def __init__(self, store_connection):
        self.store = store_connection

    def get_last_count_date(self):
        cursor = storeDB.cursor()
        cursor.execute("""SELECT TOP (1) BusinessDate FROM [Smokes].[dbo].[DailyCounts]
                order by BusinessDate desc""")
        last_count_date = cursor.fetchone()
        return last_count_date[0]
    
    def get_last_count(self):
        cursor = storeDB.cursor()
        cursor.execute("""EXEC [dbo].[dailycount]""")
        last_count = cursor.fetchall()
        print(last_count)
        Logger.info(f"Last count: {last_count}")
        return last_count

class UpdateSmokes():
    def __init__(self, store_connection):
        self.store = store_connection
    try:
        def InsertCounts(self, count, date,shift, openingBalance,comments,username):
            Logger.info(f"InsertCounts: {count}, {date}, {shift}, {openingBalance}, {comments}, {username}")
            print(count, date,shift, openingBalance,comments,username)
            lastCount = Calculations(storeDB).get_last_count()
            packRemaning = (openingBalance + lastCount[0][3] + lastCount[0][7] + lastCount[0][6] + lastCount[0][8]) - lastCount[0][2] -  lastCount[0][1]
            ovrShort=(int(count)-int(packRemaning))
            sql_query = f"""
                INSERT INTO [SMOKES].[dbo].[DailyCounts]
                ([DayOfMonth], [Store], [Shift], [OpeningBalance], [PacksReceived], [InvoiceNumbers],
                [HHChanges], [DeptSales], [Refunds], [PacksRemaining], [Count], [OverShrt],
                [Comments], [EnteredBY], [BusinessDate], [SyncToHost])
                VALUES ({date.day}, {store}, '{shift}', {openingBalance}, {lastCount[0][3]},
                '{lastCount[0][0]}', {lastCount[0][7]}, {lastCount[0][2]}, {lastCount[0][6]},
                {packRemaning}, {count}, {ovrShort}, '{comments}', '{username}', '{date}', 1)
                """
            Logger.info(f"SQL Query: {sql_query}")
            Logger.info(f"Count: {count}, Store:{store},Date: {date.day}, Shift: {shift}, OpeningBalance: {openingBalance}, Comments: {comments}, EnteredBy: {username}, PackRemaining: {packRemaning}, OvrShort: {ovrShort}, InvoiceNumbers: {lastCount[0][0]}, HHChanges: {lastCount[0][7]}, DeptSales: {lastCount[0][2]}, Refunds: {lastCount[0][6]}")

            cursor = storeDB.cursor()
            cursor.execute(sql_query)
            
            
            storeDB.commit()
            Logger.info("Inserted counts into DailyCounts table")
    except Exception as e:
        Logger.error(f"Error inserting counts into DailyCounts table: {e}")
        print(f"Error: {e}")
        storeDB.rollback()
       