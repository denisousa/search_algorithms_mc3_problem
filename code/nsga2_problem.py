import numpy as np
from pymoo.core.problem import Problem
from files_operations import most_recent_file
from datetime import datetime
from siamese_operations import format_siamese_output
from siamese_search import execute_siamese_search
from oracle_operations import filter_oracle
from generate_metrics import calculate_all_metrics
from nsga2_utils import (
    get_all_parameters_combination,
    transform_parameters_list_to_dict,
)
import pandas as pd
import time
import yaml

with open("parameters.yml", "r") as file:
    search_space = yaml.safe_load(file)

search_space_values = list(search_space.values())
params_positions = {
    "initial": [0] * 11,
    "final": [20, 10, 9, 9, 9, 9, 11, 11, 11, 11, 8],
}
current_datetime = datetime.now()
random_seed = int(time.time())
algorithm_name = "nsga2"
df_clones = pd.read_csv("../oracle_new.csv")
df_clones = filter_oracle(df_clones)


class MyProblem(Problem):
    def __init__(self):
        super().__init__(
            n_var=11,
            n_obj=2,
            n_constr=0,
            xl=params_positions["initial"],
            xu=params_positions["final"],
            vtype=int,
        )

    def _evaluate(self, x, out, *args, **kwargs):
        all_parameters_combination = get_all_parameters_combination(x)

        all_mrr, all_mop = [], []
        for combination in all_parameters_combination:
            combination_dict = transform_parameters_list_to_dict(combination)

            combination_dict["algorithm"] = algorithm_name
            combination_dict[
                "output_folder"
            ] = f'./output_{combination_dict["algorithm"]}/{current_datetime}'
            siamese_output_path = combination_dict["output_folder"]

            start_time = datetime.now()
            execute_siamese_search(**combination_dict)
            end_time = datetime.now()
            exec_time = end_time - start_time

            result_time_path = f"time_record/{algorithm_name}/{current_datetime}.txt"
            print(f"Runtime: {exec_time}")
            open(result_time_path, "a").write(f"Success execution ")
            open(result_time_path, "a").write(
                f"{combination} \nRuntime: {exec_time}\n\n"
            )

            most_recent_siamese_output, _ = most_recent_file(siamese_output_path)
            df_siamese = format_siamese_output(
                siamese_output_path, most_recent_siamese_output
            )
            folder_result = f"result_metrics/{algorithm_name}/{current_datetime}"
            metrics = calculate_all_metrics(
                most_recent_siamese_output, df_siamese, df_clones, folder_result
            )

            all_mrr.append(-metrics["MRR (Mean Reciprocal Rank)"])
            all_mop.append(-metrics["MOP (Mean Overall Precision)"])

        fitness = np.column_stack((all_mrr, all_mop))
        out["F"] = fitness
