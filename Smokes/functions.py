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
    
    def get_todays_audit_count(self,store, date):
        day = date.day
        Logger.info(f"Getting todays audit count for store {store} and date {date} and day {day}")
        day = date.day
        cursor = storeDB.cursor()
        cursor.execute(f"""SELECT TOP (1) ISNULL(audit ,0) FROM [Smokes].[dbo].[DailyCounts] where Store = {store} and DayOfMonth = {day} and businessdate = '{date}'
                order by BusinessDate desc""")
        last_audit_count = cursor.fetchone()
        Logger.info(f"Last audit count: {last_audit_count}")
        if last_audit_count == None:
            return 0
        else:
            Logger.info(f"Last audit count: {last_audit_count[0]}")
            print(f"Last audit count: {last_audit_count[0]}")
        return last_audit_count[0]
class UpdateSmokes():
    def __init__(self, store_connection):
        self.store = store_connection
   
    def InsertCounts(self, count, date,shift, openingBalance,comments,username):
        try:
            calculations = Calculations(store)
            audit = calculations.get_todays_audit_count(store, date)
            Logger.debug(F"callling get_todays_audit_count {audit}")
            if audit == None:
                audit = 0
            print(f"Audit: {audit}")
            Logger.info(f"InsertCounts: {count}, {date}, {shift}, {openingBalance}, {comments}, {username}")
            print(count, date,shift, openingBalance,comments,username)
            lastCount = Calculations(storeDB).get_last_count()
            packRemaning = (openingBalance + lastCount[0][3] + lastCount[0][7] + lastCount[0][6] + lastCount[0][8]) - lastCount[0][2] -  lastCount[0][1]
            ovrShort=(int(count))-int(packRemaning)
            if audit > 0 or audit < 0:
                ovrShort = 0

            sql_query = f"""
                INSERT INTO [SMOKES].[dbo].[DailyCounts]
                ([DayOfMonth], [Store], [Shift], [OpeningBalance], [PacksReceived], [InvoiceNumbers],
                [HHChanges], [DeptSales], [Refunds], [PacksRemaining], [Count], [OverShrt],
                [Comments], [EnteredBY], [BusinessDate], [SyncToHost],[Audit])
                VALUES ({date.day}, {store}, '{shift}', {openingBalance}, {lastCount[0][3]},
                '{lastCount[0][0]}', {lastCount[0][7]}, {lastCount[0][2]}, {lastCount[0][6]},
                {packRemaning}, {count}, {ovrShort}, '{comments}', '{username}', '{date}', 0, {audit})
                """
            Logger.info(f"SQL Query: {sql_query}")
            Logger.info(f"Count: {count}, Store:{store},Date: {date.day}, Shift: {shift}, OpeningBalance: {openingBalance}, Comments: {comments}, EnteredBy: {username}, PackRemaining: {packRemaning}, OvrShort: {ovrShort}, InvoiceNumbers: {lastCount[0][0]}, HHChanges: {lastCount[0][7]}, DeptSales: {lastCount[0][2]}, Refunds: {lastCount[0][6]}")

            cursor = storeDB.cursor()
            cursor.execute(sql_query)
            
            
            storeDB.commit()

            Logger.info("Inserted counts into DailyCounts table")
            Logger.debug("calling SyncToHost") 
            self.SyncToHost()

        except Exception as e:
            Logger.error(f"Error inserting counts into DailyCounts table: {e}")
            print(f"Error: {e}")
            storeDB.rollback()


    def setAuditCounts(self, count, date, openingBalance,comments,username):

        
        lastCount = Calculations(storeDB).get_last_count()
        packRemaning = (openingBalance + lastCount[0][3] + lastCount[0][7] + lastCount[0][6] + lastCount[0][8]) - lastCount[0][2] -  lastCount[0][1]        
        calcAudit = int(count)-int(packRemaning)
        ovrShort=(int(count))-int(packRemaning)
        try:
            sql_query = f"""
            INSERT INTO [SMOKES].[dbo].[DailyCounts]
            ([DayOfMonth], [Store], [Shift], [OpeningBalance], [PacksReceived], [InvoiceNumbers],
            [HHChanges], [DeptSales], [Refunds], [PacksRemaining], [Count], [OverShrt],
            [Comments], [EnteredBY], [BusinessDate], [SyncToHost],[Audit])
            VALUES ({date.day}, {store}, '9', {openingBalance}, {lastCount[0][3]},
            '{lastCount[0][0]}', {lastCount[0][7]}, {lastCount[0][2]}, {lastCount[0][6]},
            {packRemaning}, {count}, {ovrShort}, '{comments}', '{username}', '{date}', 0, {calcAudit})
            """
            cursor = storeDB.cursor()
            Logger.info(f"SQL Query: {sql_query}")
            Logger.debug(f"AuditCount: {count}, Store:{store},Date: {date.day}, Comments: {comments}, EnteredBy: {username} calcAudit: {calcAudit}")

            cursor.execute(sql_query)
            storeDB.commit()
            Logger.info("Inserted counts into AuditCounts table")
            self.SyncToHost()
        except Exception as e:
            Logger.error(f"Error inserting counts into AuditCounts table: {e}")
            print(f"Error: {e}")
            storeDB.rollback()

    def SyncToHost(self):
        # check to see if recoreds need to be synced to host
        cursor = storeDB.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM [SMOKES].[dbo].[DailyCounts] WHERE SyncToHost = 0 ")
        count = cursor.fetchone()[0]    
        if count == 0:
            Logger.info("No records to sync to host")
            return
        else:
            Logger.info(f"Records to sync to host: {count}")
            cursor.execute(f"SELECT * FROM [SMOKES].[dbo].[DailyCounts] WHERE SyncToHost = 0 ")
            records = cursor.fetchall() 
            Logger.debug(f"Records to sync to host: {records}")
            if hostOnline == False:
                Logger.error("Host database is not online")
                return
            else:
                for record in records:
                    try:
                        record = [
                            value if value is not None else '' if isinstance(value, str) else 0
                            for value in record
                        ]

                        cursor = host.cursor()
                        sql_query = f"""
                        Merge INTO [SMOKES].[dbo].[DailyCounts] AS target
                        USING (SELECT {record[0]} AS DayOfMonth, {record[1]} AS Store, '{record[2]}' AS Shift, {record[3]} AS OpeningBalance, {record[4]} AS PacksReceived,
                        '{record[5]}' AS InvoiceNumbers, {record[6]} AS HHChanges, {record[8]} AS DeptSales, {record[9]} AS Refunds,
                        {record[10]} AS PacksRemaining, {record[11]} AS Count, {record[13]} AS OverShrt,
                        '{record[14]}' AS Comments, '{record[15]}' AS EnteredBY, '{record[17]}' AS BusinessDate, 1 AS SyncToHost, {record[12]} AS Audit) AS source
                        ON target.DayOfMonth = source.DayOfMonth AND target.Store = source.Store AND target.BusinessDate = source.BusinessDate
                        WHEN MATCHED THEN
                        UPDATE SET target.Shift = source.Shift, target.OpeningBalance = source.OpeningBalance, target.PacksReceived = source.PacksReceived,
                        target.InvoiceNumbers = source.InvoiceNumbers, target.HHChanges = source.HHChanges, target.DeptSales = source.DeptSales,
                        target.Refunds = source.Refunds, target.PacksRemaining = source.PacksRemaining, target.Count = source.Count,
                        target.OverShrt = source.OverShrt, target.Comments = source.Comments, target.EnteredBY = source.EnteredBY,
                        target.SyncToHost = source.SyncToHost, target.Audit = source.Audit
                        WHEN NOT MATCHED THEN
                        INSERT (DayOfMonth, Store, Shift, OpeningBalance, PacksReceived, InvoiceNumbers, HHChanges, DeptSales, Refunds,
                        PacksRemaining, Count, OverShrt, Comments, EnteredBY, BusinessDate, SyncToHost, Audit)  
                        VALUES (source.DayOfMonth, source.Store, source.Shift, source.OpeningBalance, source.PacksReceived, source.InvoiceNumbers,
                        source.HHChanges, source.DeptSales, source.Refunds, source.PacksRemaining, source.Count, source.OverShrt,
                        source.Comments, source.EnteredBY, source.BusinessDate, source.SyncToHost, source.Audit);
                        """
                        # print the sql query for debugging

                        Logger.info(f"SQL Query: {sql_query}")
                        cursor.execute(sql_query)
                        host.commit()
                        Logger.info("Inserted counts into DailyCounts table on host")
                        # update the sync to host flag in the store database
                        cursor = storeDB.cursor()
                        cursor.execute(f"UPDATE [SMOKES].[dbo].[DailyCounts] SET SyncToHost = 1 WHERE TransactionNumber = {record[19]}")
                        storeDB.commit()
                    except Exception as e:
                        Logger.error(f"Error syncing counts to host: {e}")
                        print(f"Error: {e}")
                        storeDB.rollback()
                        host.rollback()
        Logger.info("Sync to host complete")
        return True
        # check if host is online
       

        