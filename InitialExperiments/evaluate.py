import pandas as pd
from C45 import C45Classifier

from utils.trees import id3_evaluate
from utils.utils import import_tree


class TrainingSample:
    def __init__(self, model_path: str, data_path: str, is_tree: bool):
        self.model_path = model_path
        self.data_path = data_path
        self.is_tree = is_tree


def train_for_sample(training_prop: TrainingSample):
    print(f"Evaluate model: {training_prop.model_path}")
    print(f"Test sample: {training_prop.data_path}")

    # Import model.
    model = import_tree(training_prop.model_path, training_prop.is_tree)

    # Get training data.
    df = pd.read_csv(training_prop.data_path)

    if 'anime' in training_prop.model_path:
        df_features = df[df.columns[2:]]
        df_y = df['Names']
    else:
        df_features = df[df.columns[:-1]]
        df_y = df['Play Tennis']

    if training_prop.is_tree:
        id3_evaluate(model, df_features, df_y)
    else:
        model.evaluate(df_features, df_y)

    print()


if __name__ == "__main__":
    training_props = [
        # Play Tennis.
        TrainingSample(
            'Output/play_tennis/id3/id3_play_tennis_2024-06-05 10-23-43.json',
            'Resources/PlayTennisTest.csv',
            True),
        TrainingSample(
            'Output/play_tennis/c45/c45_play_tennis_2024-06-05 10-39-01.pkl',
            'Resources/PlayTennisTest.csv',
            False),

        # anime_25_93
        TrainingSample(
            'Output/anime_25_93/id3/id3_anime_25_93_2024-06-05 11-43-08.json',
            'Resources/anime_25_classes_93_features_test.csv',
            True),
        TrainingSample(
            'Output/anime_25_93/c45/c45_anime_25_93_2024-06-05 11-46-41.pkl',
            'Resources/anime_25_classes_93_features_test.csv',
            False),

        # anime_82_172
        TrainingSample(
            'Output/anime_82_172/id3/id3_anime_82_172_2024-06-05 11-44-29.json',
            'Resources/anime_82_classes_172_features_test.csv',
            True),
        TrainingSample(
            'Output/anime_82_172/c45/c45_anime_82_172_2024-06-05 11-47-56.pkl',
            'Resources/anime_82_classes_172_features_test.csv',
            False),

        # anime_full
        TrainingSample(
            'Output/anime_full/id3/id3_anime_full_2024_06_04.json',
            'Resources/anime_traits_better_test.csv',
            True),
        TrainingSample(
            'Output/anime_full/c45/c45_anime_full_2024-06-04 18-05-28.pkl',
            'Resources/anime_traits_better_test.csv',
            False)
    ]

    # Test for each sample.
    for training_prop in training_props:
        train_for_sample(training_prop)