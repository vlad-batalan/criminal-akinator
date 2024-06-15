import abc
import enum
import math

from pandas import DataFrame
from sklearn import preprocessing
from sklearn.tree import DecisionTreeClassifier


class FindStrategy(enum.Enum):
    INFORMATION_GAIN = 0
    GAIN_RATIO = 1
    GINI_IMPURITY = 2


class IFindBestQuestionStrategy(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def find_best_feature(self, data: DataFrame, target_feature: str) -> (str, list[str]):
        """
        Provided a dataframe set, method evaluates the best feature to split the set.
        :param data: Dataframe object resembling the clean training set (it includes also the target feature)
        :param target_feature: The name of the feature holding the result class.
        :return: tuple of:
            - str: the name of the best feature (can be the target feature if there is a solution)
            - list[str]: the possible unique values a solution can have (is empty if a guess is provided)
        """
        pass


class InformationGainQuestionStrategy(IFindBestQuestionStrategy):

    def find_best_feature(self, data: DataFrame, target_feature: str) -> (str, list[str]):
        # Get the list of column names resembling the features.
        features_list = list(filter(lambda feature: feature != target_feature, data.columns))

        # Get best feature.
        best_feature = max(features_list, key=lambda feature: self.__get_information_gain(data, feature))

        # Enlist the next values that best feature can take.
        feature_values = list(data[best_feature].unique())

        return best_feature, feature_values

    def __get_information_gain(self, data: DataFrame, feature: str) -> float:
        # Calculate weighted average entropy for the feature.
        unique_values = data[feature].unique()
        weighted_entropy = 0

        for value in unique_values:
            # TODO: Treat the case for unknown values.
            subset = data[data[feature] == value]
            proportion = len(subset) / len(data)
            weighted_entropy += proportion * self.__get_entropy(subset, feature)

        # Calculate information gain
        entropy_outcome = self.__get_entropy(data, feature)
        information_gain = entropy_outcome - weighted_entropy

        return information_gain

    def __get_entropy(self, data: DataFrame, target_feature: str) -> float:
        total_rows = len(data)
        target_values = data[target_feature].unique()

        entropy = 0
        for value in target_values:
            # Calculate the proportion of instances with the current value
            value_count = len(data[data[target_feature] == value])
            proportion = value_count / total_rows

            # Take into consideration the case when there are
            if proportion:
                entropy -= proportion * math.log2(proportion)

        return entropy


class GainRatioQuestionStrategy(IFindBestQuestionStrategy):

    def find_best_feature(self, data: DataFrame, target_feature: str) -> (str, list[str]):
        # Algorithm takes the last column as target feature.
        column_to_move = data.pop(target_feature)
        data.insert(loc=len(data.columns), column=target_feature, value=column_to_move.values)

        # Get the list of column names resembling the features.
        features_list = list(data.columns[:-1])

        # For entry in data, a weight is assigned.
        weights = [1] * len(data)

        # Algorithm runs on a list of elements associated to their weights list.
        # Returns: [[attr_1.value, attr_2.value, ..., attr_n.value], [ ... ], ... ]
        entries = data.values.tolist()

        # Build first layer of c45 tree.
        best_feature = self.__calculate(entries, features_list, weights)
        feature_values = data[best_feature].unique()

        return best_feature, feature_values

    def __calculate(self, entries: list[list], feature_list: list[str], weights: list[float]) -> str:
        # Find out the total entropy of the set.
        total_entropy = self.__get_entropy(entries, weights)

        # Initialize important indices.
        best_attribute = None
        best_gain_ratio = 0.0
        split_info = 0.0

        # Loop through each feature.
        # It assumes that it does not contain the target column.
        for feature_index in range(len(feature_list)):
            # Gets the unique values of the feature.
            feature_values = set([record[feature_index] for record in entries])
            feature_entropy = 0.0

            # For each distinct value of the feature.
            for value in feature_values:
                # TODO: Treat the case for unknown values.
                # 1) Get the subset of the entries which have the current value.
                subset, subset_weights = self.__split_data(entries, feature_index, value, weights)

                # 2) Find out the entropy of the subset.
                subset_entropy = self.__get_entropy(subset, subset_weights)

                print(f"All weights: {weights}")
                print(f"Subset weights: {subset_weights}")

                # 3) Add findings to the feature entropy.
                subset_probability = sum(subset_weights) / sum(weights)
                feature_entropy += subset_probability * subset_entropy

                # 4) Update the split info value based on the probability.
                # Treat also the case when probability is 0 for a subset.
                if subset_probability != 0:
                    split_info -= subset_probability * math.log2(subset_probability)

            # Calculate the information gain based on the attribute.
            gain = total_entropy - feature_entropy

            # Normalize the gain if split_info is not 0.
            gain_ratio = 0.0
            if split_info != 0.0:
                gain_ratio = gain / split_info

            # Get the maximum gain ration.
            if gain_ratio > best_gain_ratio:
                best_gain_ratio = gain_ratio
                best_attribute = feature_list[feature_index]

        return best_attribute

    def __get_entropy(self, entries: list[list], weights: list[float]) -> float:
        class_counts = {}
        total_weight = 0.0

        # Counts how many records are per class totally using weight.
        # Also evaluates the total weight.
        for i, record in enumerate(entries):
            # We assume that target field is the last.
            label = record[-1]
            # Extract the weight of the current attribute.
            weight = weights[i]

            if label not in class_counts:
                class_counts[label] = 0.0
            class_counts[label] += weight
            total_weight += weight

        # Evaluates entropy.
        entropy = 0.0
        # For each result class, use the weight to find out entropy.
        # TODO: Is there possible to be classes with 0 counts?
        for count in class_counts.values():
            probability = count / total_weight
            entropy -= probability * math.log2(probability)

        return entropy

    def __split_data(self, entries: list[list], feature_index: int, feature_value: str, weights: list[float]):
        split_data = []
        split_weights = []

        for i, record in enumerate(entries):
            # Take only the entries with the attribute equal to feature_value.
            if record[feature_index] == feature_value:
                # Remove the feature_index from data.
                split_data.append(record[:feature_index] + record[feature_index + 1:])
                # Add the weight of the entry.
                split_weights.append(weights[i])

        return split_data, split_weights


class GiniQuestionStrategy(IFindBestQuestionStrategy):

    def __init__(self):
        self.label_encoder = self.label_encoder = preprocessing.LabelEncoder()

    def find_best_feature(self, data: DataFrame, target_feature: str) -> (str, list[str]):
        # Get the list of column names resembling the features.
        features_list = list(filter(lambda feature: feature != target_feature, data.columns))

        # Get best feature.
        best_feature = min(features_list, key=lambda feature: self.__weighted_gini(data, feature))

        # Enlist the next values that best feature can take.
        feature_values = list(data[best_feature].unique())

        return best_feature, feature_values



    def __gini_impurity(self, data: DataFrame, target_feature: str) -> float:
        total_rows = len(data)
        target_values = data[target_feature].unique()

        gini_impurity = 0
        for value in target_values:
            # Calculate the proportion of instances with the current value
            value_count = len(data[data[target_feature] == value])
            proportion = value_count / total_rows

            gini_impurity += proportion * proportion

        return 1 - gini_impurity

    def __weighted_gini(self, data: DataFrame, feature) -> float:
        # Calculate weighted average gini impurity indicator for the feature.
        unique_values = data[feature].unique()
        weighted_gini = 0

        # TODO: Treat the case for unknown values.
        for value in unique_values:
            subset = data[data[feature] == value]
            proportion = len(subset) / len(data)
            weighted_gini += proportion * self.__gini_impurity(subset, feature)

        return weighted_gini

    def __evaluate_using_tree(self, data: DataFrame, target_feature: str) -> (str, list[str]):
        # Using the decision tree classifier requires translating all the values to int.
        df_encoded = data.copy(deep=True)
        data_features = df_encoded.drop(target_feature, axis=1)
        for column_name in data_features.columns:
            if data_features[column_name].dtype == object:
                data_features[column_name] = self.label_encoder.fit_transform(data_features[column_name])

        data_target = data[target_feature]

        d_tree = DecisionTreeClassifier(criterion='gini', max_depth=1)
        d_tree.fit(data_features, data_target)

        best_feature = data_features.columns[d_tree.tree_.feature[0]]
        feature_values = data[best_feature].unique()

        return best_feature, feature_values