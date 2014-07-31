import matplotlib.pyplot as plt

class histogrammer(object):

    def __init__(self, **kwargs):
        self.setParameter('nbins', kwargs)
        self.setParameter('range', kwargs)
        self.setParameter('bins', kwargs)
        if hasattr(self, 'bins'):
            self.range = (self.bins[0], self.bins[-1])
            self.nbins = len(self.bins)-1
        if not hasattr(self, 'bins') and hasattr(self, 'nbins'):
            self.bins = self.nbins
        self.setParameter('title', kwargs)
        self.setParameter('xlabel', kwargs)
        self.setParameter('ylabel', kwargs)
        self.setParameter('alpha', kwargs)
        self.setParameter('color', kwargs)
        self.setParameter('histtype', kwargs)
        self.setParameter('label', kwargs)
        self.setParameter('facecolor', kwargs)
        self.setParameter('edgecolor', kwargs)

    def setParameter(self, pname, kwargs):
        try:
            setattr(self, pname, kwargs[pname])
        except KeyError:
            pass

    def addToDict(self, pname, kwargs):
        if hasattr(self, pname):
            kwargs[pname] = getattr(self, pname)
        return kwargs

    def fillHist(self, data, columnName = None):
        possible_kwargs = ('bins', 'range', 'alpha', 'color', 'histtype',
                           'label', 'facecolor', 'edgecolor')
        kwargs = {}
        for pname in possible_kwargs:
            kwargs = self.addToDict(pname, kwargs)
        self.fig = plt.figure()
        self.counts, self.h_bins, self.patches = plt.hist(data, **kwargs)

        if hasattr(self, 'range'):
            self.patches[0].axes.set_xlim( self.range )
        possible_setters = ('title', 'xlabel')
        for setter in possible_setters:
            if hasattr(self, setter):
                getattr(self.patches[0].axes, 'set_{0}'.format(setter))(
                    getattr(self, setter))
        if hasattr(self, 'ylabel'):
            bw = (self.range[1]-self.range[0])/float(self.nbins)
            self.patches[0].axes.set_ylabel(
                '{0} / ({1:.3g})'.format(self.ylabel, bw))

        return self.fig

if __name__ == '__main__':
    import numpy as np
    import matplotlib as mpl

    data = np.random.normal(0, 1, 10000)

    histo = histogrammer(nbins=50, range=(-5,5), histtype='stepfilled',
                         color='g', alpha=0.75, xlabel='x',
                         ylabel='counts', title='std nrm dist')
    
    fig = histo.fillHist(data)

    plt.show()
