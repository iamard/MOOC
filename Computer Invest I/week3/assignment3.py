import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import copy
import QSTK.qstkstudy.EventProfiler as ep

def fetchData(fileName, startdate, enddate):
    timeOfDay   = dt.timedelta(hours = 16)
    timeStamp   = du.getNYSEdays(startdate, enddate, timeOfDay)
    dataAccess  = da.DataAccess('Yahoo')
    symbols = dataAccess.get_symbols_from_list(fileName)
    symbols.append('SPY')
    
    keyValue    = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    dataFrame   = dataAccess.get_data(timeStamp, symbols, keyValue)
    dictionary  = dict(zip(keyValue, dataFrame))

    for key in keyValue:
        dictionary[key] = dictionary[key].fillna(method='ffill')
        dictionary[key] = dictionary[key].fillna(method='bfill')
        dictionary[key] = dictionary[key].fillna(1.0)

    return dictionary, symbols
 
def findEvent(fileName, startDate, endDate, limit, output):
    dictionary, symbols = fetchData(fileName, startDate, endDate)
    closePrice = dictionary['actual_close']

    # Creating an empty dataframe
    eventData  = copy.deepcopy(closePrice)
    eventData  = eventData * np.NAN

    timeStamp  = closePrice.index
    for symbol in symbols:
        for timeID in range(1, len(timeStamp)):
            # Calculating the returns for this timestamp
            priceToday = closePrice[symbol].ix[timeStamp[timeID - 0]]
            priceYest  = closePrice[symbol].ix[timeStamp[timeID - 1]]
            if (priceYest >= limit) and (priceToday < limit):
                eventData[symbol].ix[timeStamp[timeID]] = 1

    ep.eventprofiler(eventData, dictionary, i_lookback=20, i_lookforward=20,
                     s_filename=output, b_market_neutral=True, b_errorbars=True,
                     s_market_sym='SPY')
                
    return eventData;

if __name__ == '__main__':
    findEvent("sp5002008", dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), 5.0, "study0.pdf")
    findEvent("sp5002008", dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), 6.0, "question2.pdf")
    findEvent("sp5002008", dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), 7.0, "question3.pdf")
    findEvent("sp5002008", dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), 8.0, "question4.pdf")
    findEvent("sp5002008", dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), 9.0, "question5.pdf")
    findEvent("sp5002008", dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), 10.0, "question6.pdf")
    findEvent("sp5002012", dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), 5.0, "study1.pdf")
    findEvent("sp5002012", dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), 6.0, "question7.pdf")
    findEvent("sp5002012", dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), 7.0, "question8.pdf")
    findEvent("sp5002012", dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), 8.0, "question9.pdf")
    findEvent("sp5002012", dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), 9.0, "question10.pdf")
    findEvent("sp5002012", dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), 10.0, "question11pdf")
    