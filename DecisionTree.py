#imports
from sklearn.externals.six import StringIO
import pydotplus
from sklearn import tree
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.model_selection import cross_val_score
import os
os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'

class DecisionTree:
    '''takes as input two arrays:
    an arrayX of size [n_samples, n_features] holding the training samples
    and an array Y of integer values, size [n_samples],
    holding the class labels for the training samples'''

    def __init__(self, data, target, labels):
        self.data = data
        self.target = target
        X_train, X_test, y_train, y_test = train_test_split(self.data, self.target, stratify=self.target,
                                                            random_state=42)
        clf = tree.DecisionTreeClassifier(random_state=0)
        clf.fit(X_train, y_train)
        #print('Accuracy on the training subset: '+ str(format(clf.score(X_train, y_train))))
        #print('Accuracy on the test subset:'+str(format(clf.score(X_test, y_test))))
        self.dotfile = StringIO()
        set_l = set(self.target)
        set_l = list(set_l)
        tree.export_graphviz(clf, out_file=self.dotfile, feature_names=labels, class_names=set_l)
