import matplotlib.pyplot as plt

class histogrammer(object):

    def __init__(self, **kwargs):
        self.check_for = ('range','bins','color','histtype',
                          'label','facecolor','edgecolor','normed',
                          'cumulative','alpha','BLAH','nbins','title',
                          'xlabel','ylabel')
        for kwarg in self.check_for:
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
        possible_kwargs = self.check_for[0:self.check_for.index('BLAH')]
        kwargs = {}
        for pname in possible_kwargs:
            kwargs = self.addToDict(pname, kwargs)
        # self.fig = plt.figure()

        if columnName:
            data = data[columnName]

        if len(data) < 1:
            return None

        # print kwargs
        self.counts, self.h_bins, self.patches = plt.hist(data, **kwargs)

        if hasattr(self, 'range'):
            self.patches[0].axes.set_xlim( self.range )
        possible_setters = ('title', )
        for setter in possible_setters:
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

    plt.show()
