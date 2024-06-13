import abc
import enum
import math

from pandas import DataFrame


class FindStrategy(enum.Enum):
    ID3_ENTROPY = 0
    C45_WIGHTED_GAIN_ALL_TREE = 1
    CART = 2


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
