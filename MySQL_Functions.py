#Functions for SQL DB I/O
import sqlite3
from importlib_metadata import re
con = sqlite3.connect('UserData.db')
cur = con.cursor()
import datetime
import configparser

#Reads INI Settings
config = configparser.ConfigParser()
config.read("Config.ini")
Logs = config.get('Settings','Logging')

def UpdateTime():
    time=datetime.datetime.now().strftime("%m/%d/%Y, %I:%M %p")
    return time
#Updates a given column in a given row. row should be equal to the data present in the ID column
def WriteSQL(Column,Data,Row,Table):
    Row=f'"{str(Row)}"'
    cur.execute(f"UPDATE {Table} SET {Column} = {Data} WHERE ID = {Row};")
    if Logs == 'True':
        time=UpdateTime()
        print(f"{time}: wrote {Data} to row {Row} and column {Column} in table {Table}")
    con.commit()


#Inserts a row into the ID Column of the data table
def InsertSQLrow(Data,table,Column):
    cur.execute(f"INSERT INTO {table} ({Column}) VALUES (?)", [Data])
    if Logs == 'True':
        time=UpdateTime()
        print(f"{time}: Inserted new entry {Data} into table Data")
    con.commit()

#deletes a row from a table
def DeleteSQLrow(Row,Table):
    Row=f'"{str(Row)}"'
    cur.execute(f"DELETE FROM {Table} WHERE ID = {Row};")
    if Logs == 'True':
        time=UpdateTime()
        print(f"{time}: Removed row {Row} from table {Table}")
    con.commit()

#checks if given value is in DB in UserID Column
#Returns 1 if value is found returns 0 otherwise
def CheckSQLUser(Value):
    Value=f'"{str(Value)}"'
    cur.execute(f"SELECT ID FROM data WHERE ID={Value};")
    result=cur.fetchone()
    if result == None:
        result = 0

    if result == 0:
        return result
    else:
        return 1

#Reads the data in a given SQL cell
def ReadSQL(Row,Column,Table):
    Row='"'+Row+'"'
    cur.execute(f"SELECT {Column} FROM {Table} WHERE ID = {Row};")
    Value=cur.fetchone()
    return(Value[0])

#Reads the amount of messages a user has sent
def GetMsgAmt(ID):
    data=ReadSQL((ID),"Messages","data")
    data = re.findall(r'\d+',str(data))
    return(data[0])
