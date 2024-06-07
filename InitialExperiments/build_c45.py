from C45 import C45Classifier
import os

# Required for Graphviz tool
from utils.trees import c45

os.environ['PATH'] += os.pathsep + 'G:\\Programe\\Graphviz\\bin'

import pandas as pd
import graphviz

from utils.utils import output_tree, get_time_str


def build_tree_for_sample_set() -> C45Classifier:
    file_path = 'Resources/PlayTennis.csv'
    df = pd.read_csv(file_path)
    print(df.head())

    target_field = 'Play Tennis'
    features = df[df.columns[0:-1]]
    return c45(df, target_field, features)


def build_tree_for_anime_set(file_name) -> C45Classifier:
    file_path = 'Resources/' + file_name
    df = pd.read_csv(file_path).astype(str)
    print(df.head())

    target_field = 'Names'
    # Drop Id and Names.
    features = df[df.columns[2:]]
    return c45(df, target_field, features)


if __name__ == '__main__':
    time_string = get_time_str()
    print('Waiting for tree to build ... ')
    model = build_tree_for_anime_set('anime_82_classes_172_features.csv')

    print('Printing the resulted tree:')
    print(model.summary())

    # Make sure file exists.
    image_path = f'Output/c45_anime_82_172_{time_string}'
    # Generate also an image.
    model.generate_tree_diagram(graphviz, image_path)

    print('Writing result to file ... ')
    output_tree(model, f'c45_anime_82_172_{time_string}.pkl')
