# from datetime import date, timedelta
import numpy as np
import pandas as pd
import yfinance as yf
import numbers
import mysql.connector #pip install mysql-connector-python
from keras.models import Sequential, Model, model_from_json
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from datetime import timedelta

# These 2 lines are just for me to run the models on my gpu.
physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], enable=True)

# This data queries data from yahoo finance
def getData(startDate, endDate, company):
    object = yf.Ticker(company)
    data = object.history(start=startDate, end=endDate)
    return data

# This function inserts the data into the sql table
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
            print("Record already exists in Table:",table)

# This function transforms the data to be ready for model input
def transform(df, n=40):
    df = pd.DataFrame(df['open'])  # Removing all the other columns as we are only predicting if we should buy based on the opening stock price

    # Normalizing to 0-1 range
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler.fit(df)
    dfScaled = pd.DataFrame(scaler.transform(df), columns=df.columns)
    # dfScaled = pd.DataFrame(df, columns=df.columns)

    # Creating 40 columns that give the past 40 day opening stock price
    for i in range(1, n):
        dfScaled[f'open-{i}'] = dfScaled['open'].shift(i)

    # Subsetting for the neccessary columns.  Chopping off the 1st 40 days as they contain null values (i.e. the data set doesn't contain the past 40 days of opening stock prices for them)
    dfScaled = dfScaled.iloc[39:, 0:]

    # Splitting into appropriate x and y values
    x = dfScaled.to_numpy()

    # Reshaping to get correct form
    x = np.reshape(x, (x.shape[0], x.shape[1], 1))

    return x, scaler

# This function loads a model
def loadModel(name, location=''):
    # CITATION: https://machinelearningmastery.com/save-load-keras-deep-learning-models/

    # load json and create model
    json_file = open(f"{location}{name}.json", 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)

    # load weights into new model
    model.load_weights(f"{location}{name}.h5")
    print("Loaded model from disk")
    return model

def predict(x, scaler, modelName):
    # model = loadModel(modelName, location="C:/Users/Administrator/Documents/GitHub/Stock-Trading-Bot/")
    model = loadModel(modelName, location="")
    preds = model.predict(x)
    preds = scaler.inverse_transform(preds)
    return preds.flatten()
    
def nextTradingDay(today, cursor):
    nextTradingDay  = today+timedelta(days=1)
    if nextTradingDay.isoweekday()==6: # Testing if today is saturday
        nextTradingDay = nextTradingDay + timedelta(days=2)
    elif nextTradingDay.isoweekday()==5:
        nextTradingDay = nextTradingDay + timedelta(days=3) # Testing if today is Friday

    cursor.execute(f"select * from noTradingDays where day>\"{today}\" and day<DATE_ADD(\"{today}\", INTERVAL 4 DAY)")
    holidays = cursor.fetchall()

    increment=True
    while increment:
        increment = False
        for day in holidays:
            if nextTradingDay==day[0]:
                nextTradingDay = nextTradingDay + timedelta(days=1)
                increment = True
            if today.isoweekday()==6: # Testing if today is saturday
                nextTradingDay = today + timedelta(days=2)
                increment = True
            elif today.isoweekday()==5:
                nextTradingDay = today + timedelta(days=3) # Testing if today is Friday
                increment = True
            
    return nextTradingDay

