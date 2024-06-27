import os
import time
import uuid

import pandas as pd
from mrjob.job import MRJob

from mr_jobs import InfoGainMapReducer, GiniMapReducer, GainRatioMapReducer


def get_map_reducer(name: str, tmp_input_path: str, target_field: str) -> MRJob | None:
    if name == "information_gain":
        return InfoGainMapReducer(args=[tmp_input_path, "--target", target_field])

    if name == "gini_impurity":
        return GiniMapReducer(args=[tmp_input_path, "--target", target_field])

    if name == "gain_ratio":
        return GainRatioMapReducer(args=[tmp_input_path, "--target", target_field])

    return None


def execute_with_runner(job_name: str, dataset_path: str, target_field: str):
    df = pd.read_csv(dataset_path)
    if "_id" in df.columns:
        df = df.drop("_id", axis=1)

    if "Id" in df.columns:
        df = df.drop("Id", axis=1)

    # 1 write data to Temp file.
    tmp_mrjob_input_path = "Temp/" + str(uuid.uuid4()) + ".csv"

    start_time = time.time()
    df.to_csv(tmp_mrjob_input_path, index=False)
    end_time = time.time()
    print(f"Writing to disk: {end_time - start_time} seconds.")

    mr_job = get_map_reducer(job_name, tmp_mrjob_input_path, target_field)
    if mr_job is None:
        raise Exception("Invalid job name!")

    with mr_job.make_runner() as runner:
        start_time = time.time()
        runner.run()
        end_time = time.time()
        print(f"Map Reduce time: {end_time - start_time} seconds.")

        for key, value in mr_job.parse_output(runner.cat_output()):
            print(f"({key}, {value})")

    # Clean the data.
    os.remove(tmp_mrjob_input_path)


if __name__ == "__main__":
    dataset_path = "Resources/CriminalAkinatorDB.knowledge.16-06-2024.csv"
    job_name = "gain_ratio"
    target_value = "ProfileId"

    execute_with_runner(job_name, dataset_path, target_value)
