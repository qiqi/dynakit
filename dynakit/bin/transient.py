import sys
from numpy import *
import statsmodels.api as sm
from numpy.polynomial.chebyshev import chebval

def movingWindowStats(x, windowSize, orders):
    cum = zeros([x.shape[0], x.shape[1], orders.size])
    for i in range(x.shape[0]):
        cum[i] = x[i,:,newaxis] ** orders[newaxis,:]
        if i > 0:
            cum[i] += cum[i-1]
    return cum[windowSize:] - cum[:-windowSize]

def stationarityTest(x):
    windowSize = 10
    xStats = movingWindowStats(x, windowSize, arange(1, 5))
    nSamples = min(128, x.shape[0] // windowSize)
    t = linspace(-1, 1, nSamples)
    i = array(linspace(0, xStats.shape[0] - 1, nSamples), int)
    ct = chebval(t, eye(2)).T
    minPvalues = 1
    for j in range(xStats.shape[1]):
        for k in range(xStats.shape[2]):
            est = sm.OLS(xStats[i,j,k], ct)
            est2 = est.fit()
            print(j, k, est2.pvalues[1:])
            minPvalues = min(minPvalues, est2.pvalues[1:].min())
            # cla()
            # plot(t, xStats[i,j,k], '.-')
            # stop
    return minPvalues

if __name__ == '__main__':
    fname = sys.argv[1]
    x = loadtxt(fname)
    if x.ndim == 1:
        x = x[:,newaxis]
    assert x.ndim == 2

    if len(sys.argv) > 2:
        pThresh = float(sys.argv[2])
    else:
        pThresh = 0.01

    iLower, iUpper = 0, x.shape[0] - 1
    while iUpper - iLower > 1:
        iMid = (iUpper + iLower) // 2
        p = stationarityTest(x[iMid:])
        print(iMid, p)
        if p < pThresh:
            iLower = iMid
        else:
            iUpper = iMid
