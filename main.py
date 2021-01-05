import mysql.connector  # pip install mysql-connector-python
from datetime import date
import sql as sql
import functions as fct
import pandas as pd
from datetime import timedelta
from trading import makeOrder


def main():
    today = date.today()

    # Testing if the markets are open (i.e. is it a weekday)
    if today.isoweekday() in range(1,6):
        # Opening connect to db
        cnx = mysql.connector.connect(**sql.config)
        cursor = cnx.cursor()

        # Getting list of companies
        cursor.execute('select * from companies')
        companies = cursor.fetchall()

        # Iterating through companies to get new data, and make new predictions
        for company in companies:
            data = fct.getData(startDate=today, endDate=today + timedelta(days=1), company=company[1])
            data['Date'] = data.index

            # Inserting the new opening price.  This then causes the trigger "updateResidualTrigger" to fire that updates the residual for the current trading day
            fct.insertData(data=data[['Date', 'Open']], cursor=cursor, table='openingPrices', company=company[1])
            cnx.commit()

            # Getting past 40 days of opening stock price
            cursor.execute(
                f"select * from (select * from openPricesView where company = '{company[1]}' order by rowNum desc limit 40) as openPrice order by date;")
            openingPricesRaw = cursor.fetchall()
            openingPricesDF = pd.DataFrame(openingPricesRaw, columns=['rowNum', 'date', 'open', 'company'])
            scaledX, scaler = fct.transform(openingPricesDF)

            # Making the predictions
            preds = fct.predict(x=scaledX, scaler=scaler, modelName="FORD")

            # Getting the date that we are making predictions for
            tradingDay = fct.nextTradingDay(today, cursor)

            # Inserting prediction.  This causes the trigger "createAction" to fire that will create the boosted prediction and decide on the what action to take.
            fct.insertData(data=pd.DataFrame(data={'date': [tradingDay], 'modelPredicted': preds}),
                           cursor=cursor,
                           table='predictions',
                           company=company[1])
            cnx.commit()

        '''Making Trades'''

        # Getting actions
        cursor.execute('select * from actions where date=(select MAX(date) from actions)')
        actions = cursor.fetchall()
        for dt, company, prediction, action in actions:
            if action == 'buy':
                makeOrder(company, 100, 'buy')
                cursor.execute(f"insert into buyTrades (date,company,numShares) values ('{today}','{company}',100)")
                cnx.commit()

            else:
                cursor.execute(f"select numShares from currentShares where company=\'{company}\'")
                numShares = cursor.fetchone()[0]
                if numShares > 0:
                    makeOrder(company, numShares, 'sell')
                    cursor.execute(f"insert into sellTrades (date,company,numShares) values ('{today}','{company}',{numShares})")
                    cnx.commit()
                else:
                    continue

        cnx.close()


if __name__ == '__main__':
    main()
