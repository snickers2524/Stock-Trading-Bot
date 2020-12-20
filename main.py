import yfinance as yf
import datetime
import pandas as pd
import mysql.connector #pip install mysql-connector-python
from datetime import date
import numbers
# import functions as fct

def getData(startDate, endDate, company):
    object = yf.Ticker(company)
    data = object.history(start=startDate, end=endDate)
    data.to_csv('test.csv')
    return data

config = {
    'user':'admin',
    'password':'Watermelon4054',
    'host':'stock-trader-db.cmppj2geoch9.us-east-1.rds.amazonaws.com',
    'port':3306,
    'database':'trades'
}

def insertData(data, cursor, table, company):
    # creating column list for insertion
    cols = "`,`".join([str(i) for i in data.columns.tolist()]) + "`,`company"
    
    # Insert DataFrame recrds one by one.
    for i,row in data.iterrows():
        vals = ",".join([str(i) if isinstance(i, numbers.Number) else f"\"{str(i)}\""  for i in row.to_list()]) + f",\"{company}\""
        sql = f"INSERT INTO {table} (`{cols}`) VALUES ({vals})"
        print(sql)
        try:
            cursor.execute(sql)
        except mysql.connector.errors.IntegrityError:
            print("Duplicate entry, must be a holiday")
        

def main():
    today = date.today()

    # Testing if the markets are open (i.e. is it a weekday)
    # if today.isoweekday()  in range(1,6):
    if True:
        # Opening connect to db
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        # Getting list of companies
        cursor.execute('select * from companies')
        rows = cursor.fetchall()

        # Iterating through companies to get new data
        for row in rows:
            data = getData(startDate='2000-01-01', endDate=today,company=row[1])
            data['Date'] = data.index

            # Inserting the new data
            insertData(data=data[['Date','Open']],cursor=cursor,table='openingPrices',company=row[1])
            cnx.commit()
            # insertData(data=data[['High','Low','Close','Volume','Dividends','Stock Splits','Date']],cursor=cursor,table='additionalPrices',company=row[1])
            # cnx.commit()

        cnx.close()

if __name__ == '__main__':
    main()