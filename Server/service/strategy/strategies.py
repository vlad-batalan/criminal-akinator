import abc
import enum
import logging
import math
import os
import time
import uuid

from mrjob.job import MRJob
from pandas import DataFrame
from sklearn import preprocessing
from sklearn.tree import DecisionTreeClassifier

from service.mr.query_finder_jobs import InfoGainMapReducer, GiniMapReducer

logger = logging.getLogger(__name__)


class FindStrategy(enum.Enum):
    INFORMATION_GAIN = 0
    GAIN_RATIO = 1
    GINI_IMPURITY = 2
    INFORMATION_GAIN_MR = 3
    GAIN_RATIO_MR = 4
    GINI_IMPURITY_MR = 5


def check_not_null_nan(value):
    """
    Method responsible for checking if a value is not null or none.
    For the nan check, it is enough to verify if value == value.
    :param value: str or int of float
    :return: boolean value
    """

    return value and value == value


class IFindBestQuestionStrategy(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_strategy_type(self) -> FindStrategy:
        pass

    @abc.abstractmethod
    def find_best_feature(self, data: DataFrame, target_feature: str) -> (str, list[str]):
        """
        Provided a dataframe set, method evaluates the best feature to split the set.
        :param data: Dataframe object resembling the clean training set (it includes also the target feature)
        :param target_feature: The name of the feature holding the result class.
        :return: tuple of:
            - str: the name of the best feature (can be the target feature if there is a solution)
            - list[str]: the possible unique values a solution can have (is empty if a guess is provided)
            or, in the case when a guess can be made, a tuple of:
            - nan
            - nan

        """
        pass


class InformationGainQuestionStrategy(IFindBestQuestionStrategy):

    def get_strategy_type(self) -> FindStrategy:
        return FindStrategy.INFORMATION_GAIN

    def find_best_feature(self, data: DataFrame, target_feature: str) -> (str, list[str]):
        # Get the list of column names resembling the features.
        features_list = list(filter(lambda feature: feature != target_feature, data.columns))

        # Get best feature.
        best_feature = max(features_list,
                           key=lambda feature: self.__get_information_gain(data, feature, target_feature))

        # Enlist the next values that best feature can take.
        feature_values = list(filter(check_not_null_nan, data[best_feature].unique()))

        return best_feature, feature_values

    def __get_information_gain(self, data: DataFrame, feature: str, target_feature: str) -> float:
        # Filter data for only known attribute values.
        filtered_data = data[(data[feature] == data[feature])]

        # Calculate weighted average entropy for the feature.
        unique_values = filtered_data[feature].unique()
        weighted_entropy = 0

        for value in unique_values:
            subset = filtered_data[filtered_data[feature] == value]
            proportion = len(subset) / len(filtered_data)
            weighted_entropy += proportion * self.__get_entropy(subset, target_feature)

        # Calculate information gain
        entropy_outcome = self.__get_entropy(filtered_data, target_feature)
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

    def get_strategy_type(self) -> FindStrategy:
        return FindStrategy.GAIN_RATIO

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
        # Select only not null attributes to show.
        feature_values = None
        if best_feature:
            feature_values = list(filter(check_not_null_nan, data[best_feature].unique()))

        return best_feature, feature_values

    def __calculate(self, entries: list[list], feature_list: list[str], weights: list[float]) -> str:
        # Initialize important indices.
        best_attribute = None
        best_gain_ratio = 0.0
        split_info = 0.0

        # Loop through each feature.
        # It assumes that it does not contain the target column.
        for feature_index in range(len(feature_list)):
            # Filter the elements that have a defined value for the attributes.
            filtered_entries_weights = list(
                filter(lambda entry_weight: check_not_null_nan(entry_weight[0][feature_index]), zip(entries, weights)))
            filtered_entries = list(map(lambda item: item[0], filtered_entries_weights))
            filtered_weights = list(map(lambda item: item[1], filtered_entries_weights))

            # Gets the unique values of the feature.
            feature_values = set([record[feature_index] for record in filtered_entries])
            feature_entropy = 0.0

            # For each distinct value of the feature.
            for value in feature_values:
                # 1) Get the subset of the entries which have the current value.
                subset, subset_weights = self.__split_data(filtered_entries, feature_index, value, filtered_weights)

                # 2) Find out the entropy of the subset.
                subset_entropy = self.__get_entropy(subset, subset_weights)

                # 3) Add findings to the feature entropy.
                subset_probability = sum(subset_weights) / sum(weights)
                feature_entropy += subset_probability * subset_entropy

                # 4) Update the split info value based on the probability.
                # Treat also the case when probability is 0 for a subset.
                if subset_probability != 0:
                    split_info -= subset_probability * math.log2(subset_probability)

            # Find out the total entropy of the set excluding unknown values.
            total_entropy = self.__get_entropy(filtered_entries, filtered_weights)

            # Calculate the information gain based on the attribute.
            gain = total_entropy - feature_entropy

            # Normalize the gain if split_info is not 0.
            gain_ratio = 0.0
            if split_info != 0.0:
                gain_ratio = gain / split_info

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
        for count in class_counts.values():
            probability = count / total_weight
            entropy -= probability * math.log2(probability)

        return entropy

    def __split_data(self, entries: list[list], feature_index: int, feature_value: str, weights: list[float]) -> (
            list[list], list[float]):
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

    def get_strategy_type(self) -> FindStrategy:
        return FindStrategy.GINI_IMPURITY

    def __init__(self):
        self.label_encoder = self.label_encoder = preprocessing.LabelEncoder()

    def find_best_feature(self, data: DataFrame, target_feature: str) -> (str, list[str]):
        # Get the list of column names resembling the features.
        features_list = list(filter(lambda feature: feature != target_feature, data.columns))

        # Get best feature.
        best_feature = min(features_list, key=lambda feature: self.__weighted_gini(data, feature, target_feature))

        # Enlist the next values that best feature can take.
        feature_values = list(filter(check_not_null_nan, data[best_feature].unique()))

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

    def __weighted_gini(self, data: DataFrame, feature: str, target_feature: str) -> float:
        # Filter data for only known attribute values.
        filtered_data = data[(data[feature] == data[feature])]

        # Calculate weighted average gini impurity indicator for the feature.
        unique_values = filtered_data[feature].unique()
        weighted_gini = 0.0

        for value in unique_values:
            subset = filtered_data[filtered_data[feature] == value]
            proportion = len(subset) / len(filtered_data)
            weighted_gini += proportion * self.__gini_impurity(subset, target_feature)

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


class IMRJobQuestionStrategy(IFindBestQuestionStrategy, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def init_runner(self, input_file_path, target) -> MRJob:
        pass

    def generate_tmp_input_path(self) -> str:
        return "tmp/" + str(uuid.uuid4()) + ".csv"

    def clean_data(self, data: DataFrame) -> DataFrame:
        if "_id" in data.columns:
            return data.drop("_id", axis=1)
        return data

    def save_input_to_file(self, input_file_path: str, data: DataFrame):
        start_time = time.time()
        data.to_csv(input_file_path, index=False)
        end_time = time.time()
        logging.info(f"[{self.get_strategy_type()}][SaveFileTime]: {end_time - start_time} seconds.")

    def run_job(self, input_file_path: str, data: DataFrame, target_feature: str) -> (str, list[str]):
        try:
            # Initialize job.
            mr_job = self.init_runner(input_file_path, target_feature)
            with mr_job.make_runner() as runner:
                start_time = time.time()
                runner.run()
                end_time = time.time()

                logging.info(f"[{self.get_strategy_type()}][MapReduceTime]: {end_time - start_time} seconds.")

                # Get the result as a single element.
                outputs = list(mr_job.parse_output(runner.cat_output()))

                best_feature, __ = outputs[0]
                best_feature_values = list(filter(check_not_null_nan, data[best_feature].unique()))
                return best_feature, best_feature_values
        finally:
            # Delete the created file on disk.
            os.remove(input_file_path)

    def find_best_feature(self, data: DataFrame, target_feature: str) -> (str, list[str]):
        # Clean data.
        data = self.clean_data(data)

        # Get tmp file path.
        input_tmp_file_path = self.generate_tmp_input_path()

        # Save on disk.
        self.save_input_to_file(input_tmp_file_path, data)

        # Perform prediction. Also deletes the input file when ready.
        return self.run_job(input_tmp_file_path, data, target_feature)


class InformationGainMRQuestionStrategy(IMRJobQuestionStrategy):

    def get_strategy_type(self) -> FindStrategy:
        return FindStrategy.INFORMATION_GAIN_MR

    def init_runner(self, input_file_path, target_feature) -> MRJob:
        return InfoGainMapReducer(args=[input_file_path, "--target", target_feature])


class GiniMRQuestionStrategy(IMRJobQuestionStrategy):

    def get_strategy_type(self) -> FindStrategy:
        return FindStrategy.GINI_IMPURITY_MR

    def init_runner(self, input_file_path, target_feature) -> MRJob:
        return GiniMapReducer(args=[input_file_path, "--target", target_feature])
