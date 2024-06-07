from __future__ import annotations

import os
import sys
from typing import Dict

import C45

from utils.utils import import_tree


def start_guess_game_id3(tree: Dict):
    head = tree
    print("\nStart guessing game!")

    key = list(head)[0]
    while not isinstance(head, str):
        print(f"What is {key}?")
        print(f"Possible values: {list(head[key])}")

        option = input("Your response: ")
        while option not in list(head[key]):
            print(f"{option} is not present in list: {list(head[key])}")
            option = input("Please provide valid value: ")

        head = head[key][option]
        key = list(head)[0]
        print()

    print(f"My guess is: {head}")


def start_guess_game_c45(model: C45.C45Classifier):
    def get_attribute_name(n):
        if hasattr(n, 'attribute'):
            return n.attribute
        else:
            return n.label

    print("\nStart guessing game!")
    node = model.tree

    while hasattr(node, 'children') and node.children:
        keys = list(node.children.keys())
        print(f"{node.attribute}?")
        print(f"Possible values: {keys}")

        option = input("Your response: ")
        while option not in keys:
            print(f"{option} is not present in list: {keys}")
            option = input("Please provide valid value: ")

        node = node.children[option]
        print()

    print(f"My guess is: {node.label}")


def display_help():
    print("The game requires the following arguments: ")
    print("1) --c45 (for c45 model) | --id3 (for id3 model)")
    print("2) <location to model>")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        display_help()
        input("Press any key to close...")
        exit(1)

    if sys.argv[1] not in ["--c45", "--id3"]:
        display_help()
        input("Press any key to close...")
        exit(1)

    if not os.path.exists(sys.argv[2]):
        print("Provided file location does not exist!")
        display_help()
        input("Press any key to close...")
        exit(1)

    command = sys.argv[1]
    path = sys.argv[2]
    is_id3 = (command == "--id3")

    model = import_tree(path, isTree=is_id3)

    if is_id3:
        start_guess_game_id3(model)
    else:
        start_guess_game_c45(model)
