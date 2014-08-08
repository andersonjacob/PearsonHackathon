import matplotlib.pyplot as plt

class histogrammer(object):

    def __init__(self, **kwargs):
        self.hist_kw = ('range','bins','color','histtype',
                          'label','facecolor','edgecolor','normed',
                          'cumulative','alpha','figure')
        self.axis_set_kw = ('title', )
        self.other_kw = ('nbins','xlabel','ylabel')
        for kwarg in self.hist_kw + self.axis_set_kw + self.other_kw:
            self.setParameter(kwarg,kwargs)
        if hasattr(self, 'bins'):
            self.range = (self.bins[0], self.bins[-1])
            self.nbins = len(self.bins)-1
        if not hasattr(self, 'bins') and hasattr(self, 'nbins'):
            self.bins = self.nbins

    def setParameter(self, pname, kwargs):
        try:
            setattr(self, pname, kwargs[pname])
        except KeyError:
            pass

    def addToDict(self, pname, kwargs):
        try:
            kwargs[pname] = getattr(self, pname)
        except AttributeError:
            pass
        return kwargs

    def fillHist(self, data, columnName = None):
        kwargs = {}
        for pname in self.hist_kw:
            kwargs = self.addToDict(pname, kwargs)
        # self.fig = plt.figure()

        if columnName:
            data = data[columnName]

        if len(data) < 1:
            return None

        # print kwargs
        try:
            data.reset_index(drop=True, inplace=True)
        except AttributeError:
            pass
        # print data.head()
        self.counts, self.h_bins, self.patches = plt.hist(data, **kwargs)

        if hasattr(self, 'range'):
            self.patches[0].axes.set_xlim( self.range )
        for setter in self.axis_set_kw:
            try:
                getattr(self.patches[0].axes, 'set_{0}'.format(setter))(
                    getattr(self, setter))
            except AttributeError:
                pass
        if hasattr(self, 'xlabel'):
            self.patches[0].axes.set_xlabel(self.xlabel, ha='right',
                                            position = (1,1))
        if hasattr(self, 'ylabel'):
            bw = (self.range[1]-self.range[0])/float(self.nbins)
            self.patches[0].axes.set_ylabel(
                '{0} / ({1:.3g})'.format(self.ylabel, bw),
                ha='right', position = (1,1))

        return self.patches[0].axes.get_figure()

if __name__ == '__main__':
    import numpy as np
    import matplotlib as mpl

    data = np.random.normal(0, 1, 10000)

    histo = histogrammer(nbins=50, range=(-5,5), histtype='stepfilled',
                         color='g', alpha=0.75, xlabel='x',
                         ylabel='counts', title='std nrm dist')
    
    histo.fillHist(data)

    wsum = 0.
    vsum = 0.
    print histo.h_bins
    print histo.counts
    for i in range(histo.counts.argmax()-2, histo.counts.argmax()+3):
        bincenter = 0.5*(histo.h_bins[i] + histo.h_bins[i+1])
        print i,histo.counts[i], histo.h_bins[i],bincenter
        wsum += histo.counts[i]
        vsum += bincenter*histo.counts[i]

    print 'mode:', vsum/wsum
    plt.show()
