import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import copy
import QSTK.qstkstudy.EventProfiler as ep

def fetchData(symbols, startdate, enddate):
    timeOfDay   = dt.timedelta(hours = 16)
    timeStamp   = du.getNYSEdays(startdate, enddate, timeOfDay)
    dataAccess  = da.DataAccess('Yahoo')

    keyValue    = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    dataFrame   = dataAccess.get_data(timeStamp, symbols, keyValue)
    stockInfo   = dict(zip(keyValue, dataFrame))

    for key in keyValue:
        stockInfo[key] = stockInfo[key].fillna(method='ffill')
        stockInfo[key] = stockInfo[key].fillna(method='bfill')
        stockInfo[key] = stockInfo[key].fillna(1.0)

    return stockInfo

def bollinger(stockInfo, lookback):
    average = pd.rolling_mean(stockInfo['close'], lookback, min_periods = lookback)
    stddev  = pd.rolling_std(stockInfo['close'], lookback, min_periods = lookback)
    output  = (stockInfo['close'] - average) / stddev

    return output

if __name__ == '__main__':
    stockInfo  = fetchData(["AAPL", "GOOG", "IBM", "MSFT"], dt.datetime(2010, 1, 1), dt.datetime(2010, 12, 31))
    outputData = bollinger(stockInfo, 20)

    print outputData.ix["2010-5-12"]