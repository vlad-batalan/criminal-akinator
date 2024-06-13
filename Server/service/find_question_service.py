from __future__ import annotations

import enum
import logging
import math

import C45
import fastapi
from pandas import DataFrame

from sklearn import preprocessing
from sklearn.tree import DecisionTreeClassifier

from model.dto.guess_model import GuessOutput
from service.strategy.strategies import FindStrategy, InformationGainQuestionStrategy

logger = logging.getLogger(__name__)

def to_dataframe(section: list[dict]) -> DataFrame:
    return DataFrame(section)


def trim_data(data: DataFrame):
    if '_id' in data.columns:
        data.drop('_id', axis=1, inplace=True)


class FindQuestionService:

    def __init__(self, target_field: str):
        self.target_field = target_field
        self.label_encoder = preprocessing.LabelEncoder()

    def find_best_question(self, section: list[dict],
                           strategy: FindStrategy = FindStrategy.ID3_ENTROPY) -> GuessOutput:
        data = self.__preprocess_input(section)
        guess = self.__handle_guess_cases(data)

        # Return guess if one of the conditions matched.
        if guess:
            result = GuessOutput()
            result.guess = guess
            return result

        # Evaluate the best question.
        if strategy == FindStrategy.ID3_ENTROPY:
            evaluator = InformationGainQuestionStrategy()
            best_feature, __ = evaluator.find_best_feature(data, self.target_field)
        elif strategy == FindStrategy.C45_WIGHTED_GAIN_ALL_TREE:
            c45_classifier = C45.C45Classifier()
            data_features = data.drop(self.target_field, axis=1)
            data_target = data[self.target_field]

            # TODO: It creates the whole tree, limit to only next row.
            c45_classifier.fit(data_features, data_target)
            best_feature = c45_classifier.tree.attribute
        elif strategy == FindStrategy.CART:
            # Requires encoding the attribute values to int.
            df_encoded = data.copy(deep=True)
            data_features = df_encoded.drop(self.target_field, axis=1)
            for column_name in data_features.columns:
                if data_features[column_name].dtype == object:
                    data_features[column_name] = self.label_encoder.fit_transform(data_features[column_name])

            data_target = data[self.target_field]

            d_tree = DecisionTreeClassifier(criterion='entropy', max_depth=2)
            d_tree.fit(data_features, data_target)

            best_feature = data_features.columns[d_tree.tree_.feature[0]]
        else:
            raise fastapi.HTTPException(500, "Unknown operation!")

        logger.info(f"[Best][{strategy}]: {best_feature}")

        # Treat the case when only one possible value is returned (two classes have the same attributes).
        values = list(data[best_feature].unique())
        if len(values) == 1:
            logger.info(f"Classes with same feature: {list(data[self.target_field].values)}")
            result = GuessOutput()
            result.guess = data[self.target_field].mode().iloc[0]
            return result

        # Return the result.
        result = GuessOutput()
        result.question = best_feature
        result.values = values
        return result

    def __preprocess_input(self, section: list[dict]):
        # Preprocess data.
        # TODO: Beware that there are attributes with nan value.
        data = to_dataframe(section)
        trim_data(data)
        return data

    def __handle_guess_cases(self, data: DataFrame) -> str | None:
        def unique_cols(df: DataFrame):
            a = df.to_numpy()  # df.values (pandas<0.24)
            return (a[0] == a).all(0)

        # If there is only one class or no features left, return the guess.
        # Is there a moment when no classes could be provided? Yes, clients can provide whatever selection.
        # - Treated in GuessService.
        # Find a way to treat that use-case.
        if len(data[self.target_field].unique()) == 1:
            return data[self.target_field].iloc[0]

        # If there are no feature left, return the majority class as guess.
        # or
        # If there are multiple classes with the same features, return the majority.
        if len(data.columns) == 1 or all(unique_cols(data.drop(self.target_field, axis=1))):
            return data[self.target_field].mode().iloc[0]

        return None

    def __get_entropy(self, data: DataFrame):
        total_rows = len(data)
        target_values = data[self.target_field].unique()

        entropy = 0
        for value in target_values:
            # Calculate the proportion of instances with the current value
            value_count = len(data[data[self.target_field] == value])
            proportion = value_count / total_rows

            # Take into consideration the case when there are
            if proportion:
                entropy -= proportion * math.log2(proportion)

        return entropy

    def __get_information_gain(self, data: DataFrame, feature: str):
        # Calculate weighted average entropy for the feature
        unique_values = data[feature].unique()
        weighted_entropy = 0

        for value in unique_values:
            subset = data[data[feature] == value]
            proportion = len(subset) / len(data)
            weighted_entropy += proportion * self.__get_entropy(subset)

        # Calculate information gain
        entropy_outcome = self.__get_entropy(data)
        information_gain = entropy_outcome - weighted_entropy

        return information_gain
