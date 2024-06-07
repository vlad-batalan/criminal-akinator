import json
import uuid
from collections import Counter
from datetime import datetime

import pandas as pd
from pandas import DataFrame


def get_time_str():
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H-%M-%S')
    return formatted_date


def create_json_from_df(data: DataFrame, output_dir_path: str, id_column: str = None):
    attribute_values = {}

    # If data already has id column, we remove it.
    if id_column:
        print(f'Drop {id_column} from the input.')
        data = data.drop(id_column, axis='columns')

    # Transform 0 and 1 to Yes and No.
    to_transform = []
    for column_name in data.columns:
        unique_vals = data[column_name].unique()
        counter1 = Counter(unique_vals)
        counter2 = Counter([0, 1])

        if counter1 == counter2:
            to_transform.append(column_name)

    print(f'Transform 1/0 column values to Yes/No: \n{to_transform}.')
    for column_name in to_transform:
        data = data.replace({column_name: {0: 'No', 1: 'Yes'}})

    json_file_raw_name = f'tmp/result_raw_{get_time_str()}.json'
    json_file_raw_path = output_dir_path + '/' + json_file_raw_name
    print(f'Convert to raw json: {json_file_raw_path}')
    data.to_json(json_file_raw_path)

    # Read raw json.
    with open(json_file_raw_path, 'r') as json_file:
        raw_json = json.load(json_file)

    knowledge_items = {}
    for attrib_name, attrib_dict in raw_json.items():
        # Save attribute possible values.
        if attrib_name not in attribute_values:
            attribute_values[attrib_name] = list(set(attrib_dict.values()))

        for idx, value in attrib_dict.items():
            if not idx in knowledge_items:
                knowledge_items[idx] = {}
                knowledge_items[idx]['_id'] = str(uuid.uuid4())
            knowledge_items[idx][attrib_name] = value

    knowledge_items_result = list(knowledge_items.values())
    attr_items_result = [{'_id': key, 'values': list(values)} for key, values in attribute_values.items()]

    return knowledge_items_result, attr_items_result


if __name__ == '__main__':
    input_file_path = 'Resources/anime_traits_better_repaired.csv'
    output_dir_path = 'Output'

    # Read CSV file.
    df = pd.read_csv(input_file_path)
    print(df.head())

    # TODO: Transform multi-value attributes to Yes/No attributes.

    # Create JSON instances based on items.
    json_result, attributes_result = create_json_from_df(df, output_dir_path, id_column='Id')
    print(f'Elements saved in the knowledge base: {len(json_result)}')
    print(f'Number of attributes saved in the knowledge base: {len(attributes_result)}')

    # Store the results in a separate file.
    date_str = get_time_str()
    json_result_name = 'json_' + date_str + '.json'
    attrib_result_name = 'attr_' + date_str + '.json'

    with open(output_dir_path + '/' + json_result_name, 'w+') as json_result_file:
        json.dump(json_result, json_result_file)

    with open(output_dir_path + '/' + attrib_result_name, 'w+') as attr_result_file:
        json.dump(attributes_result, attr_result_file)

    # TODO: This is required only if there are multiple values.
    # In general, we want to use Yes/No/Don't know answers.
