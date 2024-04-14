from siamese_search import execute_siamese_search
from datetime import datetime, timedelta
from itertools import product
import random
import yaml
import re


def remove_duplicates(original_list):
    tuple_list = [tuple(sublist) for sublist in original_list]
    unique_tuples = set(tuple_list)
    return [list(item) for item in unique_tuples]


def generate_all_combinations(all_combinations):
    len_all_combinations = len(all_combinations)
    new_all_combinations = []

    while True:
        new_combination = generate_unique_combination(all_combinations)
        new_all_combinations.append(new_combination)
        all_combinations.append(new_combination)

        new_all_combinations = remove_duplicates(new_all_combinations)

        if len(new_all_combinations) > (len_all_combinations * 1.1):
            break

    return new_all_combinations


def generate_unique_combination(all_combinations):
    while True:
        combination = generate_combination()
        if combination not in all_combinations:
            return combination


def generate_combination():
    combination = [
        random.choice(param["ngram"]),
        random.choice(param["minCloneSize"]),
        random.choice(param["QRPercentileNorm"]),
        random.choice(param["QRPercentileT2"]),
        random.choice(param["QRPercentileT1"]),
        random.choice(param["QRPercentileOrig"]),
        random.choice(param["normBoost"]),
        random.choice(param["t2Boost"]),
        random.choice(param["t1Boost"]),
        random.choice(param["origBoost"]),
        random.choice(param["simThreshold"]),
    ]

    return combination


def cofigure_text(text):
    text = text.replace("cloneSize-", "")
    text = text.replace("ngramSize-", "")
    text = text.replace("qrNorm-", "")
    text = text.replace("normBoost-", "")
    text = text.replace("t2Boost-", "")
    text = text.replace("t1Boost-", "")
    text = text.replace("origBoost-", "")
    return text


def extract_numbers(text):
    pattern = r"-?\d+"
    numbers = re.findall(pattern, text)
    return numbers


def get_parameters_in_dict(text):
    numbers = [int(i) for i in extract_numbers(text)]
    return {
        "cloneSize": numbers[0],
        "ngramSize": numbers[1],
        "qrNorm": numbers[2],
        "normBoost": numbers[3],
        "t2Boost": numbers[4],
        "t1Boost": numbers[5],
        "origBoost": numbers[6],
    }


def get_parameters_in_list(text):
    numbers = [int(i) for i in extract_numbers(text)]
    return {
        "cloneSize": numbers[0],
        "ngramSize": numbers[1],
        "qrNorm": numbers[2],
        "normBoost": numbers[3],
        "t2Boost": numbers[4],
        "t1Boost": numbers[5],
        "origBoost": numbers[6],
    }


def get_combination(text):
    text = cofigure_text(text)
    return [int(i) for i in extract_numbers(text)]


def format_dimension(parms):
    return {
        "ngramSize": parms[0],
        "minCloneSize": parms[1],
        "QRPercentileNorm": parms[2],
        "QRPercentileT2": parms[3],
        "QRPercentileT1": parms[4],
        "QRPercentileOrig": parms[5],
        "normBoost": parms[6],
        "t2Boost": parms[7],
        "t1Boost": parms[8],
        "origBoost": parms[9],
        "simThreshold": parms[10],
    }


def evaluate_tool(parms):
    parms = format_dimension(parms)
    parms["algorithm"] = "random_search"
    parms["output_folder"] = f'output_{parms["algorithm"]}/{current_datetime}'
    execute_siamese_search(**parms)


def execute_random_search(combinations):
    algorithm = "random_search"

    grid_search_time = timedelta(days=2, hours=6, minutes=10, seconds=49)
    start_total_time = datetime.now()

    for i, combination in enumerate(combinations):
        i += 1

        print(f"\n\nCount {i}")
        print(f"Combination {combination}")

        start_time = datetime.now()
        evaluate_tool(combination)
        end_time = datetime.now()
        exec_time = end_time - start_time
        total_execution_time = end_time - start_total_time

        print(f"Runtime: {exec_time}")
        result_time_path = f"time_record/{algorithm}/{current_datetime}.txt"
        open(result_time_path, "a").write(f"Success execution ")
        open(result_time_path, "a").write(f"{combination} \nRuntime: {exec_time}\n\n")

        if grid_search_time < total_execution_time:
            break

    print(f"Total execution time: {total_execution_time}")
    open(result_time_path, "a").write(
        f"\nTotal execution time: {total_execution_time}\n"
    )


with open("parameters_grid_search.yml", "r") as file:
    grid_search_params = list(yaml.safe_load(file).values())

with open("parameters.yml", "r") as file:
    param = yaml.safe_load(file)

combinations = list(product(*grid_search_params))
combinations = generate_all_combinations(combinations)
print(len(combinations))
current_datetime = datetime.now()

execute_random_search(combinations)
