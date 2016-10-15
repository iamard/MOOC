import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import copy
import QSTK.qstkstudy.EventProfiler as ep

def fetchData(fileName, startDate, endDate):
    timeOfDay   = dt.timedelta(hours = 16)
    timeStamp   = du.getNYSEdays(startDate, endDate, timeOfDay)
    dataAccess  = da.DataAccess('Yahoo')
    symbols = dataAccess.get_symbols_from_list(fileName)
    symbols.append('SPY')
    
    keyValue    = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    dataFrame   = dataAccess.get_data(timeStamp, symbols, keyValue)
    stockInfo   = dict(zip(keyValue, dataFrame))

    for key in keyValue:
        stockInfo[key] = stockInfo[key].fillna(method='ffill')
        stockInfo[key] = stockInfo[key].fillna(method='bfill')
        stockInfo[key] = stockInfo[key].fillna(1.0)

    return symbols, stockInfo

def bollinger(stockInfo, lookback):
    average = pd.rolling_mean(stockInfo['close'], lookback, min_periods = lookback)
    stddev  = pd.rolling_std(stockInfo['close'], lookback, min_periods = lookback)
    output  = (stockInfo['close'] - average) / stddev

    return output

def findEvent(symbols, output):
    # Creating an empty dataframe
    eventData  = copy.deepcopy(output)
    eventData  = eventData * np.NAN

    timeStamp  = output.index
    for symbol in symbols:
        for index in range(1, len(timeStamp)):
            if(output[symbol].ix[timeStamp[index - 0]] <= -2.0 and
               output[symbol].ix[timeStamp[index - 1]] >= -2.0 and
               output['SPY'].ix[timeStamp[index]] >= 1.4):
                eventData[symbol].ix[timeStamp[index]] = 1
            else:
                eventData[symbol].ix[timeStamp[index]] = 0
    return eventData

def genOrder(eventData):
    fileHandle = open("orders.csv", "w" )
    timeStamp  = eventData.index
    for symbol in eventData.columns:
        for index in range(0, len(eventData.index)):
            if eventData[symbol].ix[timeStamp[index]] == 1:
                buyDate = timeStamp[index]
                if (index + 5) >= len(timeStamp):
                    sellDate = timeStamp[-1]
                else:
                    sellDate = timeStamp[index + 5]
                fileHandle.writelines(buyDate.strftime('%Y,%m,%d') + "," + str(symbol) + ",Buy,100\n")
                fileHandle.writelines(sellDate.strftime('%Y,%m,%d') + "," + str(symbol) + ",Sell,100\n")
    fileHandle.close()    

if __name__ == '__main__':
    symbols, stockInfo  = fetchData("sp5002012", dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31))
    outputVal = bollinger(stockInfo, 20)
    eventData = findEvent(symbols, outputVal)
    genOrder(eventData);
    
    ep.eventprofiler(eventData, stockInfo, i_lookback=20, i_lookforward=20,
                     s_filename="eventInfo.pdf", b_market_neutral=True, b_errorbars=True,
                     s_market_sym='SPY')
 