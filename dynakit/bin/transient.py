import sys
from numpy import *
import statsmodels.api as sm
from numpy.polynomial.chebyshev import chebval

def movingWindowStats(x, windowSize, orders):
    cum = zeros([x.size, orders.size])
    for i in range(x.size):
        cum[i] = x[i] ** orders
        if i > 0:
            cum[i] += cum[i-1]
    return cum[windowSize:] - cum[:-windowSize]

def stationarityTest(x):
    windowSize = int(ceil(x.size / 128))
    xStats = movingWindowStats(x, windowSize, arange(1, 4))
    t = linspace(-1, 1, 128)
    i = array(linspace(0, xStats.shape[0] - 1, 128), int)
    cla()
    plot(t, xStats[i,:], '.-')
    ct = chebval(t, eye(2)).T
    minPvalues = 1
    for j in range(xStats.shape[1]):
        est = sm.OLS(xStats[i,j], ct)
        est2 = est.fit()
        print(j, est2.pvalues[1:])
        minPvalues = min(minPvalues, est2.pvalues[1:].min())
    return minPvalues

if __name__ == '__main__':
    fname = sys.argv[1]
    pThresh = float(sys.argv[2])
    x = loadtxt(fname)

    iLower, iUpper = 0, x.size - 1
    while iUpper - iLower > 1:
        iMid = (iUpper + iLower) // 2
        p = stationarityTest(x[iMid:])
        print(iMid, p)
        if p < pThresh:
            iLower = iMid
        else:
            iUpper = iMid
