from typing import List, Dict

import pandas as pd
from C45 import C45Classifier
from pandas import DataFrame
from sklearn.tree import DecisionTreeClassifier

from utils.formulas import calculate_information_gain


def c45(data: DataFrame, target_column: str, features: DataFrame):
    model = C45Classifier()
    model.fit(features, data[target_column])
    return model


def id3_sklearn(data: pd.DataFrame, target_column: str, features: List[str]):
    clf = DecisionTreeClassifier(criterion='entropy')
    clf.fit(data[features], data[target_column])
    return clf


def id3(data: pd.DataFrame, target_column: str, features: List[str]):
    # print(f'Left features to compute: {len(features)}')

    if len(data[target_column].unique()) == 1:
        return data[target_column].iloc[0]

    if len(features) == 0:
        return data[target_column].mode().iloc[0]

    best_feature = max(features, key=lambda x: calculate_information_gain(data, x, target_column))

    tree = {best_feature: {}}

    features = [f for f in features if f != best_feature]

    for value in data[best_feature].unique():
        subset = data[data[best_feature] == value]
        tree[best_feature][value] = id3(subset, target_column, features)

    return tree


def id3_predict(tree, data: DataFrame):
    # Prediction for each record.
    data = data.astype(str).reset_index()
    predictions = []

    for index, record in data.iterrows():
        head = tree

        while not isinstance(head, str):
            # Select feature.
            feature = list(head.keys())[0]
            option = record[feature]
            head = head[feature][option]

        predictions.append(head)
    return predictions


def id3_evaluate(tree, x_test: DataFrame, y_test):
    y_pred = id3_predict(tree, x_test)

    if isinstance(y_test, pd.Series):
        y_test = y_test.values.tolist()

    acc = {}
    true_pred = 0
    real_acc = {}
    for i in range(len(y_test)):
        if y_test[i] not in real_acc:
            real_acc[y_test[i]] = 0
        real_acc[y_test[i]] += 1
        if y_test[i] == y_pred[i]:
            if y_test[i] not in acc:
                acc[y_test[i]] = 0
            acc[y_test[i]] += 1
            true_pred += 1
    for key in acc:
        acc[key] /= real_acc[key]
    #     mean acc
    total_acc = true_pred / len(y_test)
    print("Evaluation result: ")
    print("Total accuracy: ", total_acc)
    for key in acc:
        print("Accuracy ", key, ": ", acc[key])
