from __future__ import annotations

import json
import pickle
from datetime import datetime
from typing import Dict

import C45


def print_tree(tree, tabs=0):
    def print_tabs():
        for i in range(0, tabs):
            print('  |', end='')
        print('->', end='')

    if isinstance(tree, str):
        print_tabs()
        print(tree)
        return

    for key in tree:
        print_tabs()
        print(key)
        print_tree(tree[key], tabs + 1)


def import_tree(file_path: str, isTree: bool = True):
    if isTree:
        with open(file_path, "r") as import_file:
            tree_json = json.load(import_file)
            return tree_json

    with open(file_path, "rb") as import_file:
        return pickle.load(import_file)


def output_tree(tree: Dict | C45.C45Classifier, output_name):
    path = 'Output/' + output_name

    if isinstance(tree, Dict):
        with open(path, "w+") as outfile:
            json.dump(tree, outfile)
        return

    if isinstance(tree, C45.C45Classifier):
        with open(path, "wb+") as outfile:
            pickle.dump(tree, outfile)


def get_time_str():
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H-%M-%S')
    return formatted_date
