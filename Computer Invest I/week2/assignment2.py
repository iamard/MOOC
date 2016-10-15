import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def fetchData(symbols, startdate, enddate):
    timeOfDay   = dt.timedelta(hours=16)
    timeStamp   = du.getNYSEdays(startdate, enddate, timeOfDay)
    dataAccess  = da.DataAccess('Yahoo', cachestalltime = 0)
    keyValue    = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    dataFrame   = dataAccess.get_data(timeStamp, symbols, keyValue)
    dictionary  = dict(zip(keyValue, dataFrame))

    closePrice  = dictionary['close'].values
    normalized  = closePrice / closePrice[0, :]
    return [closePrice, normalized, timeStamp]

def calcInfo(originalPrice, normalized, timeStamp, ratio):
    tempValue   = np.sum(normalized * ratio, axis = 1);

    #Calculate daily return
    dailyReturn = tempValue.copy()
    tsu.returnize0(dailyReturn);

    volatility  = np.std(dailyReturn)
    average     = np.mean(dailyReturn)
    sharpeRatio = (average / volatility) * np.sqrt(len(timeStamp))
    totalReturn = np.cumprod(dailyReturn + 1, axis = 0)
    return sharpeRatio

def printInfo(symbols, startDate, endDate, info):
     print "Start Date: ", startDate;
     print "End Date: ", endDate;
     print "Symbols: ", symbols;
     print "Sharpe Ratio: " , info[0];
     print "Volatility (stdev of daily returns): " , info[1];
     print "Average Daily Return: " , info[2];
     print "Cumulative Return: " , info[3];

def simulate(startDate, endDate, symbols, ratio):
    price = fetchData(symbols,
                      startDate,
                      endDate)
    info  = calcInfo(price[0], price[1], price[2], ratio)
    return info

def partitions(n):
	# base case of recursion: zero is the sum of the empty list
	if n == 0:
		yield []
		return
		
	# modify partitions of n-1 to form partitions of n
	for p in partitions(n-1):
		yield [1] + p
		if p and (len(p) < 2 or p[1] > p[0]):
			yield [p[0] + 1] + p[1:]

def all_perms(str):
    if len(str) <=1:
        yield str
    else:
        for perm in all_perms(str[1:]):
            for i in range(len(perm)+1):
                yield perm[:i] + str[0:1] + perm[i:]

def unique(s):
    """Return a list of the elements in s, but without duplicates.

    For example, unique([1,2,3,1,2,3]) is some permutation of [1,2,3],
    unique("abcabc") some permutation of ["a", "b", "c"], and
    unique(([1, 2], [2, 3], [1, 2])) some permutation of
    [[2, 3], [1, 2]].

    For best speed, all sequence elements should be hashable.  Then
    unique() will usually work in linear time.

    If not possible, the sequence elements should enjoy a total
    ordering, and if list(s).sort() doesn't raise TypeError it's
    assumed that they do enjoy a total ordering.  Then unique() will
    usually work in O(N*log2(N)) time.

    If that's not possible either, the sequence elements must support
    equality-testing.  Then unique() will usually work in quadratic
    time.
    """

    n = len(s)
    if n == 0:
        return []

    # Try using a dict first, as that's the fastest and will usually
    # work.  If it doesn't work, it will usually fail quickly, so it
    # usually doesn't cost much to *try* it.  It requires that all the
    # sequence elements be hashable, and support equality comparison.
    u = {}
    try:
        for x in s:
            u[x] = 1
    except TypeError:
        del u  # move on to the next method
    else:
        return u.keys()

    # We can't hash all the elements.  Second fastest is to sort,
    # which brings the equal elements together; then duplicates are
    # easy to weed out in a single pass.
    # NOTE:  Python's list.sort() was designed to be efficient in the
    # presence of many duplicate elements.  This isn't true of all
    # sort functions in all languages or libraries, so this approach
    # is more effective in Python than it may be elsewhere.
    try:
        t = list(s)
        t.sort()
    except TypeError:
        del t  # move on to the next method
    else:
        assert n > 0
        last = t[0]
        lasti = i = 1
        while i < n:
            if t[i] != last:
                t[lasti] = last = t[i]
                lasti += 1
            i += 1
        return t[:lasti]

    # Brute force is all that's left.
    u = []
    for x in s:
        if x not in u:
            u.append(x)
    return u

def optimize(startDate, endDate, symbols):
    N = len(symbols)
    output = None
    max = 0.0
    for p in partitions(10):
        if (len(p) > N):
            continue
        elif (len(p) < N):
            p = p + ([0] * (N - len(p)))

        for pp in unique(list(all_perms(p))):
            ratio = [x / 10.0 for x in pp]
            info = simulate(startDate, endDate, symbols, ratio).item()
            if (info > max):
                max = info
                output = ratio

    print max, output

if __name__ == '__main__':
    optimize(dt.datetime(2011,1,1), dt.datetime(2011,12,31), ['AAPL', 'GOOG', 'IBM', 'MSFT'])
    optimize(dt.datetime(2010,1,1), dt.datetime(2010,12,31), ['BRCM', 'ADBE', 'AMD', 'ADI'])
    optimize(dt.datetime(2011,1,1), dt.datetime(2011,12,31), ['BRCM', 'TXN', 'AMD', 'ADI'])
    optimize(dt.datetime(2010,1,1), dt.datetime(2010,12,31), ['BRCM', 'TXN', 'IBM', 'HNZ'])
    optimize(dt.datetime(2010,1,1), dt.datetime(2010,12,31),  ['C', 'GS', 'IBM', 'HNZ'])
    optimize(dt.datetime(2011,1,1), dt.datetime(2011,12,31),  ['AAPL', 'GOOG', 'IBM', 'MSFT'])
    optimize(dt.datetime(2011,1,1), dt.datetime(2011,12,31), ['BRCM', 'ADBE', 'AMD', 'ADI'])
    optimize(dt.datetime(2011,1,1), dt.datetime(2011,12,31), ['BRCM', 'TXN', 'AMD', 'ADI'])
    optimize(dt.datetime(2010,1,1), dt.datetime(2010,12,31),  ['BRCM', 'TXN', 'IBM', 'HNZ'])
    optimize(dt.datetime(2010,1,1), dt.datetime(2010,12,31), ['C', 'GS', 'IBM', 'HNZ'])
