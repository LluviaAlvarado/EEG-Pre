# imports
from sklearn.externals.six import StringIO
import pydotplus
from sklearn import tree
from sklearn.model_selection import train_test_split
import os

os.environ["PATH"] += os.pathsep + 'Graphviz2.38/bin/'


class DecisionTree:
    '''takes as input two arrays:
    an arrayX of size [n_samples, n_features] holding the training samples
    and an array Y of integer values, size [n_samples],
    holding the class labels for the training samples'''

    def __init__(self, data, target, labels, md, min):
        self.data = data
        self.target = target
        X_train, X_test, y_train, y_test = train_test_split(self.data, self.target, stratify=self.target,
                                                            random_state=42)
        clf = tree.DecisionTreeClassifier(random_state=0, max_depth=md, min_samples_leaf=min)
        clf.fit(X_train, y_train)
        self.ATr = 'Precisión del entrenamiento:   ' + str(format(clf.score(X_train, y_train)))
        self.ATe = 'Precisión :   ' + str(format(clf.score(X_test, y_test)))
        self.dotfile = StringIO()
        set_l = set(self.target)
        set_l = list(set_l)
        tree.export_graphviz(clf, out_file=self.dotfile, feature_names=labels, class_names=set_l, filled=True,
                             rounded=True,
                             special_characters=True)
