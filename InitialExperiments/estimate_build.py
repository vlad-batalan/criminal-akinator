import time

import pandas as pd
from pandas import DataFrame

from utils.trees import id3, c45


def transform_play_tennis(data: DataFrame) -> (DataFrame, list[str], str):
    data = data.astype(str)
    column_features = data.columns[0:-1]
    target_field = 'Play Tennis'

    return data, column_features, target_field


def transform_anime(data: DataFrame) -> (DataFrame, list[str], str):
    # Drop Id field.
    data = data.drop(data.columns[0], axis=1).astype(str)
    column_features = data.columns[1:]
    target_field = 'Names'

    return data, column_features, target_field


if __name__ == '__main__':
    train_sets = {
        'Resources/PlayTennis.csv': transform_play_tennis,
        'Resources/anime_25_classes_93_features.csv': transform_anime,
        'Resources/anime_82_classes_172_features.csv': transform_anime,
        'Resources/anime_traits_better.csv': transform_anime
    }

    for training_set_path in train_sets:
        df = pd.read_csv(training_set_path)
        data, column_features, target_field = train_sets[training_set_path](df)

        # Get id3 creation time.
        print(f"{training_set_path} -> ID3")
        start_time = time.time()
        id3(data, target_field, column_features)
        end_time = time.time()
        spent_time = end_time - start_time
        print(f"Build time: {spent_time} seconds.")
        # Write value to file.
        with open('Output/creation_time.txt', 'a+') as f:
            f.write(f"{training_set_path} -> ID3 -> {spent_time} s\n")

        # Get C45 creation time.
        print(f"{training_set_path} -> C45")
        start_time = time.time()
        c45(data, target_field, data[column_features])
        end_time = time.time()
        spent_time = end_time - start_time
        print(f"Build time: {spent_time} seconds.")
        # Write value to file.
        with open('Output/creation_time.txt', 'a+') as f:
            f.write(f"{training_set_path} -> C45 -> {spent_time} s\n")
