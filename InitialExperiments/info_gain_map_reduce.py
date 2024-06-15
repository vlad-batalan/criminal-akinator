import math

import pandas as pd
from mrjob.job import MRJob
from mrjob.step import MRStep


class MRJobCounter(MRJob):

    def configure_args(self):
        super(MRJobCounter, self).configure_args()
        self.add_passthru_arg("-t", "--target", help="Define the target column for the question extraction.")

    def read_csv_data_mapper_raw(self, input_path, input_uri):
        data = pd.read_csv(input_path)
        for column in data.columns:
            if column != self.options.target:
                yield column, list(zip(list(data[column].values), list(data[self.options.target].values)))

    def mapper_split_count(self, attribute_name, list_of_tuple_value_target):
        for value, target_value in list_of_tuple_value_target:
            if value == value:
                yield (attribute_name, value, target_value), 1
                # Generate 1 count for each value of the attribute.
                # yield (attribute_name, "ATTR_VALUE", value), 1
                # yield (attribute_name, "ATTR_VALUE", None), 1

                # Generate 1 count for each value of the target attribute.
                # yield (attribute_name, "TARGET_VALUE", target_value), 1
                # yield (attribute_name, "TARGET_VALUE", None), 1

                # TODO: To decide if this is required later.
                # yield (attribute_name, "ALL", None), 1
                # yield (None, None), 1

    def reducer_count(self, tuple_attr_type_val, count):
        yield tuple_attr_type_val, sum(count)

    def mapper_count_per_attribute_per_value(self, tuple_attr_val_target, count):
        attribute_name, attribute_val, target_val = tuple_attr_val_target
        yield (attribute_name, attribute_val), (target_val, count)

    def reducer_entropy_per_attribute_per_value(self, tuple_name_val, tuple_target_count):
        count_values = list(map(lambda x: x[1], tuple_target_count))
        total_count = sum(count_values)
        entropy = 0.0

        for count in count_values:
            probability = count / total_count
            entropy -= probability * math.log2(probability)

        yield tuple_name_val, {"count": total_count, "entropy": entropy}

    def mapper_gain_per_attribute(self, tuple_name_val, prop):
        attribute_name, attribute_value = tuple_name_val
        yield attribute_name, prop

    def reducer_info_gain_per_attribute(self, attribute_name, props):
        # Total number of entries.
        total_count = 0
        results = list(props)

        # Get total number of values.
        for attribute_value_prop in results:
            total_count += attribute_value_prop["count"]

        total_entropy = 0.0
        weighted_entropy = 0.0
        for attribute_value_prop in results:
            weight = attribute_value_prop["count"] / total_count
            weighted_entropy += weight * attribute_value_prop["entropy"]
            total_entropy -= weight * math.log2(weight)

        information_gain = total_entropy + weighted_entropy

        yield attribute_name, information_gain

    def mapper_all(self, attribute_name, info_gain):
        yield None, (attribute_name, info_gain)

    def reducer_result(self, __, tuple_attr_gain):
        best_gain = 0.0
        best_attrib = None
        for attribute_name, info_gain in tuple_attr_gain:
            if info_gain >= best_gain:
                best_gain = info_gain
                best_attrib = attribute_name

        yield best_attrib, best_gain


    def steps(self):
        return [
            # Step 1: Read the data as a csv, returns:
            # {key: column_name, value: ([str] as attr_values, [str] as target_values)
            MRStep(mapper_raw=self.read_csv_data_mapper_raw),

            # Step 2: Count all, count per attribute, count per attribute and value.
            MRStep(mapper=self.mapper_split_count,
                   reducer=self.reducer_count),

            # Step 3: Calculate entropy per attribute per attribute value.
            MRStep(mapper=self.mapper_count_per_attribute_per_value,
                   reducer=self.reducer_entropy_per_attribute_per_value),

            # Step 4: Calculate Info gain per attribute.
            MRStep(mapper=self.mapper_gain_per_attribute,
                   reducer=self.reducer_info_gain_per_attribute),

            # Step 5: Get the best attribute.
            MRStep(mapper=self.mapper_all,
                   reducer=self.reducer_result),
        ]


if __name__ == "__main__":
    MRJobCounter.run()
