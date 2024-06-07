from typing import Dict

import pandas as pd

from utils.draw import generate_tree_diagram
from utils.trees import id3
from utils.utils import get_time_str, output_tree


def build_tree_for_sample_set() -> Dict:
    file_path = 'Resources/PlayTennis.csv'
    df = pd.read_csv(file_path).astype(str)
    print(df.head())

    target_field = 'Play Tennis'
    features = df.columns[0:-1]
    return id3(df, target_field, features)


def build_tree_for_anime_set(file_name) -> Dict:
    file_path = 'Resources/' + file_name
    df = pd.read_csv(file_path)
    df = df.drop(df.columns[0], axis=1).astype(str)
    print(df.head())

    target_field = 'Names'
    features = df.columns[1:]
    return id3(df, target_field, features)


if __name__ == '__main__':
    print('Waiting for tree to build ... ')
    tree = build_tree_for_anime_set('anime_82_classes_172_features.csv')

    print('Printing the resulted tree:')
    print(tree)

    output_file_name = f'id3_anime_82_172_{get_time_str()}'

    print('Drawing the tree ... ')
    generate_tree_diagram(tree, f'Output/{output_file_name}')

    print('Writing result to file ... ')
    output_tree(tree, f'{output_file_name}.json')
