import pandas as pd
import numpy as np
from pyHistogrammer import histogrammer
import matplotlib.pyplot as plt
import re

import argparse
parser = argparse.ArgumentParser(description='analyze student data')
parser.add_argument('inputfiles', nargs='*')
args = parser.parse_args()

# print args
pd.set_option('line_width', 120)

cols = ['initialErrMult', 'minErrMult', 'errRate', 'N', 'avgTries',
        'medianTries', 'stdevTries', 'modeTries']
collectedData = pd.DataFrame(columns=cols)
row = { col: None for col in cols }
plt.hold(True)
for inputfile in args.inputfiles:
    m_str = r'_mult(\d*\.\d+)_min(\d*\.\d+)'
    m = re.search(m_str, inputfile)
    print inputfile
    if m:
        # print m.groups()
        initialErrMult = float(m.groups()[0])
        minErrMult = float(m.groups()[1])
    data = pd.read_csv(inputfile)
    # print data.head(10)

    errs = pd.Series.unique(data['errRate'])

    # bins = np.linspace(0,100,50)

    fig = plt.figure()
    histo = histogrammer(nbins=25, range=(0,100), alpha=0.9, 
                         histtype='step',
                         figure=fig,
                         xlabel='attempts for mastery',
                         ylabel='students')
    row['initialErrMult'] = initialErrMult
    row['minErrMult'] = minErrMult
    for err in errs:
        row['errRate'] = err
        histo.label = str(err)
        # print histo.label
        cuts = (data.errRate==err) & (data.mastered==True)
        # print binRate
        edata = data[cuts]['tries']
        row['N'] = edata.count()
        row['avgTries'] = edata.mean()
        row['medianTries'] = edata.median()
        row['stdevTries'] = edata.std(ddof=1)
        histo.fillHist(edata)
        wsum = 0.
        vsum = 0.
        if row['N'] > 75:
            counts, h_bins = np.histogram(edata, bins=20)
            for i in range(counts.argmax()-2, counts.argmax()+3):
                try:
                    bincenter = 0.5*(h_bins[i] + h_bins[i+1])
                    wsum += counts[i]
                    vsum += bincenter*counts[i]
                except:
                    continue
        try:
            row['modeTries'] = vsum/wsum
        except ZeroDivisionError:
            row['modeTries'] = -999.
        collectedData = collectedData.append(row, ignore_index=True)

    plt.legend()
    fig.set_alpha(0.)

    plt.savefig(inputfile + '.svg', frameon=False)
    plt.close(fig)


agg_data = pd.DataFrame(collectedData)
agg_data.fillna(value=-999., axis=1, inplace=True)
print agg_data.head(10)
# print agg_data.describe()

import bisect
def xyzToMeshes(data, x=None, y=None, z=None, addLastEntry=False):
    xs = data[x].unique().tolist()
    xs.sort()
    # print xs
    ys = data[y].unique().tolist()
    ys.sort()
    # print ys
    Z = np.zeros((len(xs),len(ys)))
    # print X
    # print Y
    # print Z
    for idx,row in data.iterrows():
        xi = bisect.bisect_left(xs, row[x])
        yi = bisect.bisect_left(ys, row[y])
        # print row[x],row[y],'->',xi,yi
        Z[xi, yi] = row[z]

    def shiftAndAdd(xs):
        xs.append(2*xs[-1]-xs[-2])
        nl = xs[-2]
        lastw = xs[1]-xs[0]
        for i in range(len(xs)):
            try:
                w = xs[i+1] - xs[i]
            except:
                w = xs[i]-nl
            xs[i] -= lastw/2.
            lastw = w
            # print i,w

        
        return xs

    if addLastEntry:
        # print xs
        xs = shiftAndAdd(xs)
        # print xs
        ys = shiftAndAdd(ys)
    X,Y = np.meshgrid(xs,ys)

    return X,Y,Z


# plt.hold(True)
plt.close('all')
z='medianTries'

print 'plotting ...'
perfectZ = None
targetX, targetY, targetZ = xyzToMeshes(agg_data[agg_data.errRate == 0.2],
                                        x='initialErrMult',y='minErrMult',
                                        z=z, addLastEntry=True)
targetFit = plt.figure()
mTarget = np.ma.masked_where((targetZ<0.01) | (-(np.isfinite(targetZ))),
                             targetZ)
plt.pcolormesh(targetX,targetY,mTarget.T, alpha=0.5)
plt.xlim((targetX[0,0],targetX[0,-1]))
plt.ylim((targetY[0,0],targetY[-1,0]))
plt.xlabel('initialErrMult')
plt.ylabel('minErrMult')
plt.title('raw errRate: {0:.2f}'.format(0.2))
plt.colorbar()

for err in sorted(agg_data['errRate'].unique()):
    print err
    fig = plt.figure()
    tStudents = agg_data[agg_data.errRate == err]
    X,Y,Z = xyzToMeshes(tStudents, x='initialErrMult',y='minErrMult',
                        z=z, addLastEntry=True)
    mZ = np.ma.masked_where((Z<0.01) | (-(np.isfinite(Z))),
                            (Z-targetZ)/targetZ)
    plt.pcolormesh(X,Y,mZ.T, alpha=0.5, edgecolors='none', shading='flat',
                   linewidths=0)
    plt.xlim((X[0,0],X[0,-1]))
    plt.ylim((Y[0,0],Y[-1,0]))
    plt.xlabel('initialErrMult')
    plt.ylabel('minErrMult')
    plt.title('errRate: {0:.2f} <passing> {1:.0f}'.format(
        err, tStudents['N'].mean()))
    plt.colorbar()

    X1,Y1,_ = xyzToMeshes(tStudents, x='initialErrMult',y='minErrMult',
                                   z=z, addLastEntry=False)
    try:
        cs = plt.contour(X1, Y1, mZ.T, [.2, .4, .6, .8],
                         vmin=mZ.min(), vmax=mZ.max())
        plt.clabel(cs, inline=1, fontsize=10)
    except:
        pass

plt.show()
