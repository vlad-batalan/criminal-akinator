import json
import re

import pandas

# Python program to get average of a list
def Average(lst):
    return sum(lst) / len(lst)

if __name__ == "__main__":
    result_structured = []
    log_file_path = "Resources/app.log"
    filtered_logs_path = "Output/app.csv"

    # Open the log file.
    with open(log_file_path, "r") as log_file:
        last_value = {"instances": None, "strategy": None, "time": None}

        for line in log_file.readlines():
            # Trim the last symbol.
            line = line[0:-1]

            # Filter only the number of retrieved instances and the time taken to provide an answer.
            if "[RetrieveInstances]" in line:
                last_value["instances"] = int(line.split(": ")[-1])
            if "[BestQuestionTime]" in line:
                strategy_right_split = line.split("[FindStrategy.")[-1]
                strategy_seconds_split = strategy_right_split.split("]: ")
                strategy = strategy_seconds_split[0]
                number_seconds = float(strategy_seconds_split[1].split("seconds.")[0])

                last_value["strategy"] = strategy
                last_value["time"] = number_seconds
                result_structured.append(last_value)
                last_value = {"instances": None, "strategy": None, "time": None}

    # Prepare values for each data.
    post_processed_data = {}

    for item in result_structured:
        if item["strategy"] not in post_processed_data:
            post_processed_data[item["strategy"]] = {}
        if item["instances"] not in post_processed_data[item["strategy"]]:
            post_processed_data[item["strategy"]][item["instances"]] = []
        post_processed_data[item["strategy"]][item["instances"]].append(item["time"])

    # Evaluate average per instances.
    for strategy in post_processed_data:
        for instances, values in post_processed_data[strategy].items():
            post_processed_data[strategy][instances] = Average(values)

    final_result = []
    for strategy, attributes in post_processed_data.items():
        for instances, avg in attributes.items():
            final_result.append({"strategy": strategy, "instances": instances, "avg_time": avg})

    print(final_result)

    df = pandas.read_json(json.dumps(final_result))
    df.to_csv(filtered_logs_path, index=False)
