import pandas as pd
import numpy as np
from pyHistogrammer import histogrammer
import matplotlib.pyplot as plt

pd.set_option('line_width', 120)
data = pd.read_csv('studentSimulator_mult2.0_min0.0.csv')
print data.head(10)

errs = pd.Series.unique(data['errRate'])

bins = np.linspace(0,99,100)
histo = histogrammer(bins=bins, alpha=0.9, histtype='step', cumulative=True)

figs = []
plt.hold(True)
for err in errs:
    histo.label = str(err)
    print histo.label
    binRate = (data.errRate==err) & (data.mastered==True)
    # print binRate
    edata = data[binRate]['tries']
    print edata.describe()
    figs.append(histo.fillHist(edata.as_matrix()))

plt.legend()
plt.show()
