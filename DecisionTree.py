# imports
import os

from sklearn import tree
from sklearn.externals.six import StringIO
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split

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
                                                            random_state=0)
        # clf = tree.DecisionTreeClassifier(random_state=0, max_depth=md, min_samples_leaf=min)
        # clf.fit(X_train, y_train)
        parameters = {'max_depth': range(3, 20)}
        clf = GridSearchCV(tree.DecisionTreeClassifier(), parameters, n_jobs=1, cv=min)
        clf.fit(X=self.data, y=self.target)
        self.ATr = 'Best score:   ' + str(format(clf.best_score_))
        self.dotfile = StringIO()
        set_l = set(self.target)
        set_l = list(set_l)
        tree.export_graphviz(clf.best_estimator_, out_file=self.dotfile, feature_names=labels, class_names=set_l,
                             filled=True,
                             rounded=True,
                             special_characters=True)
