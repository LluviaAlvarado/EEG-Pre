#imports
from sklearn.cluster import KMeans as KM
import numpy as np


class KMeans:
    '''data needs to be a list of arrays, each array contains
    characteristics of a single window
    k = number of clusters
    t = type of algorithm (0,1)
    iter = max iterations
    maxE = max epochs'''

    def __init__(self, data, k, t, iter, maxE):
        #if t == 0:
         #   t = 'k-means++'
        #else:
         #   t = 'random'
        self.kmean = KM(k, t, iter, maxE).fit(np.array(data))
        self.labels = self.kmean.labels_
        self.clusters = self.kmean.cluster_centers_

    def predict(self, data):
        return self.kmean.fit_predict(np.array(data))