from __future__ import annotations

import abc
import logging
import fastapi
from pandas import DataFrame

from sklearn import preprocessing

from model.dto.guess_model import GuessOutput
from service.strategy.strategies import FindStrategy, InformationGainQuestionStrategy, GainRatioQuestionStrategy, \
    GiniQuestionStrategy, InformationGainMRQuestionStrategy

logger = logging.getLogger(__name__)


def to_dataframe(section: list[dict]) -> DataFrame:
    return DataFrame(section)


def trim_data(data: DataFrame):
    if '_id' in data.columns:
        data.drop('_id', axis=1, inplace=True)


class IFindQuestionService(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def find_best_question(self, section: list[dict], target_field: str,
                           strategy: FindStrategy = FindStrategy.INFORMATION_GAIN) -> GuessOutput:
        pass


class FindQuestionService(IFindQuestionService):

    def __init__(self):
        self.label_encoder = preprocessing.LabelEncoder()
        self.evaluator_list = [
            InformationGainQuestionStrategy(),
            GainRatioQuestionStrategy(),
            GiniQuestionStrategy(),
            InformationGainMRQuestionStrategy()
        ]

    def find_best_question(self, section: list[dict], target_field: str,
                           strategy: FindStrategy = FindStrategy.INFORMATION_GAIN) -> GuessOutput:
        data = self.__preprocess_input(section)
        guess = self.__handle_guess_cases(data, target_field)

        # Return guess if one of the conditions matched.
        if guess:
            result = GuessOutput()
            result.guess = guess
            return result

        # Get the strategy based on input.
        evaluator = None
        for item in self.evaluator_list:
            if item.get_strategy_type() == strategy:
                evaluator = item
                break

        # No evaluator was found.
        if evaluator is None:
            raise fastapi.HTTPException(500, "Unknown operation!")

        best_feature, feature_values = evaluator.find_best_feature(data, target_field)

        logger.info(f"[Best][{strategy}][Feature]: {best_feature}")
        logger.info(f"[Best][{strategy}][Values]: {feature_values}")

        # Treat the case when only one possible value is returned (two classes have the same attributes).
        if not feature_values or len(feature_values) == 1:
            logger.info(f"Classes with same feature: {set(data[target_field].values)}")
            result = GuessOutput()
            result.guess = data[target_field].mode().iloc[0]
            return result

        # Return the result.
        result = GuessOutput()
        result.question = best_feature
        result.values = list(feature_values)
        return result

    def __preprocess_input(self, section: list[dict]):
        # Preprocess data.
        # TODO: Beware that there are attributes with nan value.
        data = to_dataframe(section)
        trim_data(data)
        return data

    def __handle_guess_cases(self, data: DataFrame, target_field: str) -> str | None:
        def unique_cols(df: DataFrame):
            a = df.to_numpy()  # df.values (pandas<0.24)
            return (a[0] == a).all(0)

        # If there is only one class or no features left, return the guess.
        # Is there a moment when no classes could be provided? Yes, clients can provide whatever selection.
        # - Treated in GuessService.
        # Find a way to treat that use-case.
        if len(data[target_field].unique()) == 1:
            return data[target_field].iloc[0]

        # If there are no feature left, return the majority class as guess.
        # or
        # If there are multiple classes with the same features, return the majority.
        if len(data.columns) == 1 or all(unique_cols(data.drop(target_field, axis=1))):
            return data[target_field].mode().iloc[0]

        return None
