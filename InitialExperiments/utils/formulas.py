import math


def calculate_entropy(data, target_column):
    total_rows = len(data)
    target_values = data[target_column].unique()

    entropy = 0
    for value in target_values:
        # Calculate the proportion of instances with the current value
        value_count = len(data[data[target_column] == value])
        proportion = value_count / total_rows
        if proportion:
            entropy -= proportion * math.log2(proportion)

    return entropy


def calculate_information_gain(data, feature, target_column):
    # Calculate weighted average entropy for the feature
    unique_values = data[feature].unique()
    weighted_entropy = 0

    for value in unique_values:
        subset = data[data[feature] == value]
        proportion = len(subset) / len(data)
        weighted_entropy += proportion * calculate_entropy(subset, target_column)

    # Calculate information gain
    entropy_outcome = calculate_entropy(data, target_column)
    information_gain = entropy_outcome - weighted_entropy

    return information_gain
