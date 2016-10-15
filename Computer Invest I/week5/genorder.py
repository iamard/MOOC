import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import copy
import QSTK.qstkstudy.EventProfiler as ep

def fetchData(fileName, timeStamp):
    dataAccess  = da.DataAccess('Yahoo')
    symbols     = dataAccess.get_symbols_from_list(fileName)
    symbols.append('SPY')
    keyValue    = ['close', 'actual_close']
    dataFrame   = dataAccess.get_data(timeStamp, symbols, keyValue)
    dictionary  = dict(zip(keyValue, dataFrame))

    for key in keyValue:
        dictionary[key] = dictionary[key].fillna(method='ffill')
        dictionary[key] = dictionary[key].fillna(method='bfill')
        dictionary[key] = dictionary[key].fillna(1.0)
    return dictionary, symbols
 
def findEvent(dictionary, symbols, limit):
    closePrice = dictionary['actual_close']

    # Creating an empty dataframe
    eventData  = copy.deepcopy(closePrice)
    eventData  = eventData * np.NAN

    timeStamp  = closePrice.index
    for symbol in symbols:
        for index in range(1, len(timeStamp)):
            # Calculating the returns for this timestamp
            priceToday = closePrice[symbol].ix[timeStamp[index - 0]]
            priceYest  = closePrice[symbol].ix[timeStamp[index - 1]]
            if (priceYest >= limit) and (priceToday < limit):
                eventData[symbol].ix[timeStamp[index]] = 1
            else:
                eventData[symbol].ix[timeStamp[index]] = 0
    return eventData;

if __name__ == '__main__':
    startDate  = dt.datetime(2008, 1, 1)
    endDate    = dt.datetime(2009, 12, 31)
    timeOfDay  = dt.timedelta(hours = 16)
    timeStamp  = du.getNYSEdays(startDate, endDate, timeOfDay)
    dictionary, symbols = fetchData("sp5002012", timeStamp)
    eventData  = findEvent(dictionary, symbols, 10.0)

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
