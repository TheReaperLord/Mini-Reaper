import pyodbc
import time
import os
from dotenv import load_dotenv

load_dotenv()

server = os.getenv('SQL_ADDRESS')
database = os.getenv('SQL_DATABASE')
username = os.getenv('SQL_USERNAME')
password = os.getenv('SQL_PASSWORD')
# driver= '{ODBC Driver 17 for SQL Server}'
driver = '{ODBC Driver 17 for SQL Server}'
cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
#pyodbc.pooling = False

def connect():
    try:
        return cnxn.cursor()
    except:
        cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
        return cnxn.cursor()

def sendData(query, *args):
    cursor = connect()
    cursor.execute(query, args)
    cursor.commit()
    #cnxn.commit()
    cursor.close()

def getData(query, *args):
    cursor = connect()
    results = cursor.execute(query, args).fetchall()
    cursor.close()
    return results


def getDataDic(query, *args):
    cursor = connect()
    cursor.execute(query, args)
    columns = [column[0] for column in cursor.description]
    rows = cursor.fetchall()
    results = []
    cursor.close()
    for row in rows:
        results.append(dict(zip(columns, row)))
    return results

def checkConnection():
    if not cnxn:  # No connection yet? Connect.
        cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
        cursor = connection.cursor()
    try:
        cursor.execute(INSERT_QUERY)
        cursor.commit()
    except pyodbc.Error as pe:
        print("Error:", pe)
        if pe.args[0] == "08S01":  # Communication error.
            # Nuke the connection and retry.
            cnxn.close()
            cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
            cursor = connection.cursor()
        raise  # Re-raise any other exception

if __name__ == "__main__":
    print(getDataDic("SELECT * FROM serverConfig WHERE id = ?", os.getenv('ME')))
    print(getDataDic("SELECT * FROM serverConfig WHERE id = ?", os.getenv('ME')))
    '''connect()
    cursor.execute("SELECT * FROM serverConfig")
    print(cursor)
    print(getDataDic("SELECT * FROM serverConfig"))'''