import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import copy
import QSTK.qstkstudy.EventProfiler as ep
import csv
import sys

def readFund(filename):
    dataFrame   = pd.read_csv(filename, header = None)

    startDate   = dt.datetime(dataFrame.get_value(0, 0), dataFrame.get_value(0, 1), dataFrame.get_value(0, 2), 16)
    lastRow     = len(dataFrame) - 1
    endDate     = dt.datetime(dataFrame.get_value(lastRow, 0), dataFrame.get_value(lastRow, 1), dataFrame.get_value(lastRow, 2), 16)    
    fundData    = dataFrame[3].values.copy()
    normalized  = fundData / fundData[0]
    dailyReturn = normalized.copy()
    dailyReturn = tsu.returnize0(normalized);
    volatility  = np.std(dailyReturn)
    average     = np.mean(dailyReturn)
    sharpeRatio = (average / volatility) * np.sqrt(252)
    totalReturn = fundData[len(fundData) -1] / fundData[0]
    return startDate, endDate, int(fundData[len(fundData) -1]), volatility, average, sharpeRatio, totalReturn

def readSPX(startDate, endDate):
    timeOfDay   = dt.timedelta(hours = 16)
    timeStamp   = du.getNYSEdays(startDate, endDate, timeOfDay)
    dataAccess  = da.DataAccess('Yahoo', cachestalltime = 0)
    keyValue    = ['close', 'actual_close']
    dataFrame   = dataAccess.get_data(timeStamp, ['$SPX'], keyValue)
    dictionary  = dict(zip(keyValue, dataFrame))

    closePrice  = dictionary['close'].values
    normalized  = closePrice / closePrice[0, :]
    dailyReturn = normalized.copy()
    dailyReturn = tsu.returnize0(normalized);
    volatility  = np.std(dailyReturn)
    average     = np.mean(dailyReturn)
    sharpeRatio = (average / volatility) * np.sqrt(252)
    totalReturn = closePrice[len(closePrice) -1, 0] / closePrice[0, 0]
    return volatility, average, sharpeRatio, totalReturn
    
if __name__ == '__main__':
    startDate, endDate, fundFinalValue, fundVolatility, fundAverage, fundSharpeRatio, fundTotalReturn = readFund("output.csv")
    spxVolatility, spxAverage, spxSharpeRatio, spxTotalReturn = readSPX(startDate, endDate);

    print "Details of the Performance of the portfolio :"
    print "The final value of the portfolio using the sample file is -- " + str(endDate) + ", " + str(fundFinalValue)
    print "Data Range : " + str(startDate) + " to " + str(endDate)
    print "Sharpe Ratio of Fund : " + str(fundSharpeRatio)
    print "Sharpe Ratio of $SPX : " + str(spxSharpeRatio)
    print "Total Return of Fund : " + str(fundTotalReturn)
    print "Total Return of $SPX : " + str(spxTotalReturn)
    print "Standard Deviation of Fund : " + str(fundVolatility)
    print "Standard Deviation of $SPX : " + str(spxVolatility)
    print "Average Daily Return of Fund : " + str(fundAverage)
    print "Average Daily Return of $SPX : " + str(spxAverage)

    