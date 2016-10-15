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

def readOrder(filename):
    file    = open(filename, "rU")
    reader  = csv.reader(file, delimiter=',')
    dates   = set()
    symbols = set()
    for row in reader:
        dates.add(dt.datetime(int(row[0]), int(row[1]), int(row[2])))
        symbols.add(row[3])

    dates   = sorted(list(dates))
    start   = dates[ 0]
    end     = dates[-1] + dt.timedelta(days = 1) 
    dates   = du.getNYSEdays(start, end, dt.timedelta(hours = 16))
    symbols = list(symbols)

    order   = pd.DataFrame(np.zeros((len(dates), len(symbols))), index = dates, columns = symbols)
    file.seek(0)
    for row in reader:
        date   = dt.datetime(int(row[0]), int(row[1]), int(row[2]), 16)
        symbol = row[3]
        trade  = row[4]
        amount = int(row[5])
        if(trade == 'Buy'):
            order[symbol].loc[date] += amount
        else:
            order[symbol].loc[date] += -amount
    print order["AAPL"]
    return symbols, dates, order

def fetchData(symbols, dates):
    timeOfDay   = dt.timedelta(hours = 16)
    startdate   = dates[ 0]
    enddate     = dates[-1] + dt.timedelta(days = 1) 
    timeStamp   = du.getNYSEdays(startdate, enddate, timeOfDay)
    dataAccess  = da.DataAccess('Yahoo')    
    keyValue    = ['close', 'actual_close']
    dataFrame   = dataAccess.get_data(timeStamp, symbols, keyValue)
    price       = dict(zip(keyValue, dataFrame))

    for key in keyValue:
        price[key] = price[key].fillna(method='ffill')
        price[key] = price[key].fillna(method='bfill')
        price[key] = price[key].fillna(1.0)

    return price

def fecthOrder(symbols, dates, order, price, startCash):
    symbols.append("_CASH")
    holding = pd.DataFrame(np.zeros((len(dates), len(symbols))), index = dates, columns = symbols)
    holding["_CASH"][dates[0]] = startCash

    total = dict()
    for symbol in symbols:
        total[symbol] = 0
    
    curCash = startCash
    for date in order.index:
        for symbol in order.columns:
            value  = price['close'][symbol][date]
            amount = order[symbol].loc[date]
            total[symbol] = total[symbol] + amount
            holding[symbol].loc[date] = total[symbol]
            curCash = curCash - value * amount;
            holding["_CASH"][date] = curCash
        print holding.loc[date]
    return holding

def calcValue(symbols, dates, holding):
    value = pd.DataFrame(np.zeros((len(dates), 1)), index=list(dates), columns=list("V"))

    for date in dates:
	    total = 0
	    for symbol in symbols:
		    if symbol == "_CASH":
			    total = total + holding[symbol][date]
		    else:
			    total = total + holding[symbol][date] * price['close'][symbol][date]
	    value["V"][date] = total
    print value
    return value

if __name__ == '__main__':
    filename  = sys.argv[1]
    startCash = int(sys.argv[2])
    symbols, dates, order = readOrder(filename)
    price     = fetchData(symbols, dates)
    holding   = fecthOrder(symbols, dates, order, price, startCash)
    value     = calcValue(symbols, dates, holding)
    
    output    = open("output.csv", "w")
    for row in value.iterrows():
	    output.writelines(str(row[0].strftime('%Y,%m,%d')) + ", " + str(row[1]["V"].round()) + "\n" )
    output.close()
