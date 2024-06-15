import os
import time
import uuid

import pandas as pd

from info_gain_map_reduce import MRJobCounter

if __name__ == "__main__":
    dataset_path = "Resources/CriminalAkinatorDB.knowledge.csv"
    df = pd.read_csv(dataset_path).drop("_id", axis=1)

    # 1 write data to Temp file.
    tmp_mrjob_input_path = "Temp/" + str(uuid.uuid4()) + ".csv"

    start_time = time.time()
    df.to_csv(tmp_mrjob_input_path, index=False)
    end_time = time.time()
    print(f"Writing to disk: {end_time - start_time} seconds.")

    mr_job = MRJobCounter(args=[tmp_mrjob_input_path, "--target", "ProfileId"])
    with mr_job.make_runner() as runner:
        start_time = time.time()
        runner.run()
        end_time = time.time()
        print(f"Map Reduce time: {end_time - start_time} seconds.")

        for key, value in mr_job.parse_output(runner.cat_output()):
            print(f"({key}, {value})")

    # Clean the data.
    os.remove(tmp_mrjob_input_path)
