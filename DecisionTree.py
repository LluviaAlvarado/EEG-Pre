#imports
from sklearn import tree
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.metrics import  accuracy_score

class DecisionTree:
    '''takes as input two arrays:
    an arrayX of size [n_samples, n_features] holding the training samples
    and an array Y of integer values, size [n_samples],
    holding the class labels for the training samples'''

    def __init__(self, data, target):
        self.data = data
        self.target = target
        le = preprocessing.LabelEncoder()
        self.target = le.fit_transform(self.target)

        data_train, data_test, target_train, target_test = train_test_split(self.data, self.target, test_size=0.1, random_state=0)
        self.clf = tree.DecisionTreeClassifier(criterion='gini', min_samples_split=30, splitter="best")
        self.clf.fit(data_train, target_train)
        target_predict = self.clf.predict(data_test)
        accuracy = accuracy_score(target_test, target_predict)
        print(str(accuracy*100)+"% de precision")
