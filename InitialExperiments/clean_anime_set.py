import pandas as pd

from utils.utils import get_time_str


def get_popular_characters():
    popular_characters_path = 'Resources/hyper_popular_characters.txt'
    result = []
    with open(popular_characters_path, 'r') as f:
        for line in f.readlines():
            result.append(line[:-1])
    return result


if __name__ == "__main__":
    popular_characters = get_popular_characters()
    print(popular_characters)

    # Read all the dataset.
    file_path = 'Resources/anime_traits_better.csv'
    df = pd.read_csv(file_path)
    print(df.head())

    # Filter only popular characters.
    filtered = []
    for name in popular_characters:
        df_name = df.loc[df['Names'] == name]
        filtered.append(df_name)

    df_filtered = pd.concat(filtered)

    cols_to_delete = []
    for target_column in df.columns:
        # Unique values.
        if len(df_filtered[target_column].unique()) == 1:
            cols_to_delete.append(target_column)

    trimmed_df = df_filtered.drop(cols_to_delete, axis=1).astype(str)
    print(trimmed_df.head())

    output_path = f'Output/trimmed_{get_time_str()}.csv'
    trimmed_df.to_csv(output_path, index=False)
