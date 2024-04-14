import pandas as pd
from siamese_operations import format_siamese_output
from oracle_operations import filter_oracle
from parameters_operations import get_parameters_in_dict
import json
import os
import re
import numpy as np
import shutil
import sys


def extract_number(s):
    return int(s.split("_")[0])


def find_lines_with_specific_text(filename, text):
    result = []
    with open(filename, "r") as file:
        for line in file:
            if text in line:
                result.append(line.strip().replace(text, "").strip())
    return result


def get_k_hits(recommended_items, relevant_items):
    recommended_and_relevant = []

    hit = []

    for index, item in enumerate(recommended_items):
        if len(recommended_and_relevant) == len(relevant_items):
            break

        check, relevant_hit = check_clone_is_correct(relevant_items, item)
        if check:
            recommended_and_relevant.append(item)
            hit.append(index + 1)

    return f"{hit}"


def precision_at_k(recommended_items, relevant_items, k):
    recommended_items = recommended_items[:k]
    recommended_and_relevant = []

    for index, item in enumerate(recommended_items):
        if len(recommended_and_relevant) == len(relevant_items):
            break

        check, relevant_hit = check_clone_is_correct(relevant_items, item)
        if check:
            recommended_and_relevant.append(item)

    return len(recommended_and_relevant) / k


def recall_at_k(recommended_items, relevant_items, k):
    recommended_items = recommended_items[:k]
    recommended_and_relevant = []

    hit = []

    for index, item in enumerate(recommended_items):
        if len(recommended_and_relevant) == len(relevant_items):
            break

        check, relevant_hit = check_clone_is_correct(relevant_items, item)
        if check:
            recommended_and_relevant.append(item)
            hit.append(index + 1)

    return len(recommended_and_relevant) / len(relevant_items)


def apk(recommended_items, relevant_items, k):
    precisions = [
        precision_at_k(recommended_items, relevant_items, i) for i in range(1, k + 1)
    ]

    return sum(precisions) / k


def overall_precision(siamese_hit_attempts, oracle_clones, k):
    all_precision_at_k = []
    for i in range(1, k + 1):
        precision = precision_at_k(siamese_hit_attempts, oracle_clones, i)
        all_precision_at_k.append(precision)
    return sum(all_precision_at_k) / len(all_precision_at_k)


def mapk(recommended_items, relevant_items, k):
    return np.mean([apk(a, p, k) for a, p in zip(recommended_items, relevant_items)])


def find_float_numbers(input_string):
    float_numbers = re.findall(r"\b\d+\.\d+\b", input_string)
    return [float(num) for num in float_numbers]


def find_lines_with_runtime(filename):
    result = []
    with open(filename, "r") as file:
        for line in file:
            if "Runtime:" in line:
                result.append(line.strip().replace("Runtime: ", ""))
    return result


def get_files_in_folder(folder_path):
    files = os.listdir(folder_path)
    file_times = [
        (
            os.path.join(folder_path, file),
            os.path.getctime(os.path.join(folder_path, file)),
        )
        for file in files
    ]
    sorted_files = sorted(
        [file[0].split("/")[-1] for file in file_times[:-1]], key=extract_number
    )
    return sorted_files


def check_clone_is_correct(oracle_clones_list, siamese_clone):
    siamese_clone = {
        "file2": siamese_clone[0],
        "start2": siamese_clone[1],
        "end2": siamese_clone[2],
    }

    for oracle_clone in oracle_clones_list:
        oracle_clone = {
            "file2": oracle_clone[0],
            "start2": oracle_clone[1],
            "end2": oracle_clone[2],
        }

        file2_condition = oracle_clone["file2"] == siamese_clone["file2"]
        start2_condition = oracle_clone["start2"] >= siamese_clone["start2"]
        end2_condition = oracle_clone["end2"] <= siamese_clone["end2"]

        if file2_condition and start2_condition and end2_condition:
            return True, list(oracle_clone.values())

        start2_condition = oracle_clone["start2"] <= siamese_clone["start2"]
        end2_condition = oracle_clone["end2"] >= siamese_clone["end2"]

        if file2_condition and start2_condition and end2_condition:
            return True, list(oracle_clone.values())

    return False, list(oracle_clone.values())


def get_qualitas_clones_in_dataframe_by_so_clone(so_clone, dataframe):
    df_matched_rows = dataframe[
        (dataframe["file1"] == so_clone["file1"])
        & (dataframe["start1"] == so_clone["start1"])
        & (dataframe["end1"] == so_clone["end1"])
    ]
    df_matched_rows = df_matched_rows[["file2", "start2", "end2"]]
    df_matched_rows.reset_index(drop=True, inplace=True)
    return df_matched_rows.values.tolist()


def get_problemns_in_oracle(df_clones):
    problems_in_oracle = {}

    file1_oracles = df_clones["file1"].tolist()

    unique_files = [i for i in file1_oracles if file1_oracles.count(i) == 1]
    len_unique = len([i for i in file1_oracles if file1_oracles.count(i) == 1])
    problems_in_oracle["unique_files"] = unique_files

    duplicate_files_list_by_one = [
        x for i, x in enumerate(file1_oracles) if i != file1_oracles.index(x)
    ]
    duplicate_files_list = list(set(duplicate_files_list_by_one))

    so_clones = df_clones[["file1", "start1", "end1"]]
    duplicate_clones_oracle = so_clones[so_clones.duplicated()]
    exact_clones_oracle = duplicate_clones_oracle.drop_duplicates()
    problems_in_oracle["exact_clones"] = exact_clones_oracle.values.tolist()

    count_duplicastes_clones = 0
    problems_in_oracle["duplicate_files"] = {}
    for row, duplicate_files in enumerate(duplicate_files_list):
        df = df_clones[df_clones["file1"] == duplicate_files]
        df = df.reset_index(drop=True)
        count_duplicastes_clones += df.shape[0]
        try:
            problems_in_oracle["duplicate_files"][df.shape[0]]["amount"] += 1
            problems_in_oracle["duplicate_files"][df.shape[0]]["example"].append(
                df[["file1", "start1", "end1"]].values.tolist()
            )
        except:
            problems_in_oracle["duplicate_files"][df.shape[0]] = {}
            problems_in_oracle["duplicate_files"][df.shape[0]]["amount"] = 1
            problems_in_oracle["duplicate_files"][df.shape[0]]["example"] = []
            problems_in_oracle["duplicate_files"][df.shape[0]]["example"].append(
                df[["file1", "start1", "end1"]].values.tolist()
            )

    problems_in_oracle["total"] = len_unique + count_duplicastes_clones
    problems_in_oracle["unique"] = len_unique
    problems_in_oracle["repeat"] = count_duplicastes_clones

    with open("problems_in_oracle.json", "w") as json_file:
        json.dump(problems_in_oracle, json_file, indent=2)
    return problems_in_oracle


def calculate_hit_number(all_reciprocal_rank, k):
    all_reciprocal_rank[f"status@{k}"] = {}

    if f"results_k@{k}" in all_reciprocal_rank:
        for rr in all_reciprocal_rank[f"results_k@{k}"]:
            if f"hit_{rr['hit_number']}" in all_reciprocal_rank[f"status@{k}"]:
                all_reciprocal_rank[f"status@{k}"][f"hit_{rr['hit_number']}"] += 1

            else:
                all_reciprocal_rank[f"status@{k}"][f"hit_{rr['hit_number']}"] = 1

    return all_reciprocal_rank


def get_so_clones_from_oracle(df_clones, df_siamese):
    exact_predict_data = []
    inside_predict_data = []
    not_predict_data = []

    df_siamese = df_siamese.drop_duplicates(subset=["file1", "start1", "end1"])

    for _, oracle_row in df_clones.iterrows():
        df_filtered = df_siamese[df_siamese["file1"] == oracle_row["file1"]]

        if df_filtered.shape[0] == 0:
            not_predict_data.append(
                {
                    "file1": oracle_row["file1"],
                    "start1": oracle_row["start1"],
                    "end1": oracle_row["end1"],
                }
            )

        for _, siamese_row in df_filtered.iterrows():
            if (
                oracle_row["start1"] == siamese_row["start1"]
                and oracle_row["end1"] == siamese_row["end1"]
            ):
                exact_predict_data.append(siamese_row)
                break

            elif (
                oracle_row["start1"] >= siamese_row["start1"]
                and oracle_row["end1"] <= siamese_row["end1"]
            ):
                inside_predict_data.append(siamese_row)
                break

            elif (
                oracle_row["start1"] <= siamese_row["start1"]
                and oracle_row["end1"] >= siamese_row["end1"]
            ):
                inside_predict_data.append(siamese_row)
                break

            else:
                print("problem")

    df_exact_predict = pd.DataFrame(exact_predict_data).sort_values(by="file1")
    df_exact_predict = df_exact_predict.drop_duplicates(
        subset=["file1", "start1", "end1"]
    )

    try:
        df_inside_predict = pd.DataFrame(inside_predict_data).sort_values(by="file1")
        df_inside_predict = df_inside_predict.drop_duplicates(
            subset=["file1", "start1", "end1"]
        )
    except:
        df_inside_predict = pd.DataFrame()

    try:
        df_not_predict = pd.DataFrame(not_predict_data).sort_values(by="file1")
        df_not_predict = df_not_predict.drop_duplicates(subset=["file1"])
    except:
        df_inside_predict = pd.DataFrame()

    df_concat_predict = pd.concat(
        [df_exact_predict, df_inside_predict], ignore_index=True
    )

    df_exact_and_inside_predict = df_concat_predict[df_concat_predict.duplicated()]

    df_concat_predict = df_concat_predict.drop_duplicates(
        subset=["file1", "start1", "end1"]
    )
    return {
        "correct_predictions": df_concat_predict,
        "exact_predictions": df_exact_predict,
        "inside_predictions": df_inside_predict,
        "exact_inside_predictions": df_exact_and_inside_predict,
        "not_predictions": df_not_predict,
    }


def get_list_items_relevants(df_clones, clones_in_oracle, not_predicted_clones):
    relevants_clones = set()

    for _, row in clones_in_oracle.iterrows():
        oracle_clones = get_qualitas_clones_in_dataframe_by_so_clone(row, df_clones)
        relevants_clones.add(len(oracle_clones))

    for _, row in not_predicted_clones.iterrows():
        oracle_clones = get_qualitas_clones_in_dataframe_by_so_clone(row, df_clones)
        relevants_clones.add(len(oracle_clones))

    return list(relevants_clones)


def separate_filename_and_path(clone):
    return {
        "filename": f'{clone[0].split("/")[-1]}_{clone[1]}_{clone[2]}',
        "path": "/".join(clone[0].split("/")[-1]),
    }


def add_all_precision_at_k(siamese_hit_attempts, oracle_clones, k):
    all_precision_at_k = []
    for i in range(1, k + 1):
        precision = {
            f"Precision@{i}": precision_at_k(siamese_hit_attempts, oracle_clones, i)
        }
        all_precision_at_k.append(precision)
    return all_precision_at_k


def add_all_recall_at_k(siamese_hit_attempts, oracle_clones, k):
    all_recall_at_k = []
    for i in range(1, k + 1):
        if len(oracle_clones) < i:
            break

        recall = {f"Recall@{i}": recall_at_k(siamese_hit_attempts, oracle_clones, i)}
        all_recall_at_k.append(recall)
    return all_recall_at_k


def compute_query(
    index, unique_so_clone, reciprocal_rank, oracle_clones, siamese_hit_attempts
):
    return {
        "clone_SO": f"{unique_so_clone}",
        "oracle_clones_QC": [
            f'{clone[0].split("/")[-1]}_{clone[1]}_{clone[2]}'
            for clone in oracle_clones
        ],
        "siamese_clones_QC": [
            f'{clone[0].split("/")[-1]}_{clone[1]}_{clone[2]}'
            for clone in siamese_hit_attempts
        ],
        "relevants_clones_number": len(oracle_clones),
        "attempts_number": len(siamese_hit_attempts),
        "hit_number": index + 1,
        "k_hits_correct": get_k_hits(siamese_hit_attempts, oracle_clones),
        "RR (Reciprocal Rank)": reciprocal_rank,
        "Precision@K": add_all_precision_at_k(
            siamese_hit_attempts, oracle_clones, len(siamese_hit_attempts)
        ),
        "Recall@K": add_all_recall_at_k(
            siamese_hit_attempts, oracle_clones, len(siamese_hit_attempts)
        ),
        "OP (Overall Precision)": overall_precision(
            siamese_hit_attempts, oracle_clones, len(siamese_hit_attempts)
        ),
    }


def compute_query_not_predict(oracle_clone, oracle_clones):
    return {
        "clone_SO": f"{oracle_clone}",
        "oracle_clones_QC": [
            f'{clone[0].split("/")[-1]}_{clone[1]}_{clone[2]}'
            for clone in oracle_clones
        ],
        "siamese_clones_QC": [],
        "relevants_clones_number": len(oracle_clones),
        "attempts_number": 0,
        "hit_number": None,
        "RR (Reciprocal Rank)": 0,
        "Precision@K": [],
        "Recall@K": [],
    }


def add_attempts(all_reciprocal_rank, siamese_hit_attempts):
    try:
        attempts = len(siamese_hit_attempts)
        all_reciprocal_rank["siamese_status"][f"number_attempts_{attempts}"] += 1
    except:
        all_reciprocal_rank["siamese_status"][f"number_attempts_{attempts}"] = 1
    return all_reciprocal_rank


def calculate_all_metrics(result_siamese_csv, df_siamese, df_clones, folder_result):
    if not os.path.exists(folder_result):
        os.makedirs(folder_result)

    total_reciprocal_rank = 0.0

    so_clones = get_so_clones_from_oracle(df_clones, df_siamese)
    clones_in_oracle = so_clones["correct_predictions"]
    not_predicted_clones = so_clones["not_predictions"]

    df_queries = df_clones.drop_duplicates(subset=["file1", "start1", "end1"])
    num_queries = df_queries.shape[0]

    all_reciprocal_rank = {
        "siamese_status": {
            "num_queries": num_queries,
            "predictions": clones_in_oracle.shape[0],
            "not_predict": not_predicted_clones.shape[0],
        },
        "parameters": get_parameters_in_dict(result_siamese_csv),
        "predict_results": [],
        "not_predict_results": [],
    }

    number_relevants_clones = get_list_items_relevants(
        df_clones, clones_in_oracle, not_predicted_clones
    )

    for _, row in clones_in_oracle.iterrows():
        reciprocal_rank = 0

        unique_so_clone = f"{row['file1']}_{row['start1']}_{row['end1']}"
        oracle_clones = get_qualitas_clones_in_dataframe_by_so_clone(row, df_clones)
        siamese_hit_attempts = get_qualitas_clones_in_dataframe_by_so_clone(
            row, df_siamese
        )

        for index, siamese_hit in enumerate(siamese_hit_attempts):
            clone_is_correct, _ = check_clone_is_correct(oracle_clones, siamese_hit)
            if clone_is_correct:
                reciprocal_rank += 1 / (index + 1)
                total_reciprocal_rank += 1 / (index + 1)
                rr = compute_query(
                    index,
                    unique_so_clone,
                    reciprocal_rank,
                    oracle_clones,
                    siamese_hit_attempts,
                )
                all_reciprocal_rank["predict_results"].append(rr)
                break

            if (index + 1) == len(siamese_hit_attempts):
                reciprocal_rank += 0
                total_reciprocal_rank += 0
                rr = compute_query(
                    index,
                    unique_so_clone,
                    reciprocal_rank,
                    oracle_clones,
                    siamese_hit_attempts,
                )
                all_reciprocal_rank["predict_results"].append(rr)
                break

        add_attempts(all_reciprocal_rank, siamese_hit_attempts)

    for _, row in not_predicted_clones.iterrows():
        oracle_clone = f"{row['file1']}_{row['start1']}_{row['end1']}"
        oracle_clones = get_qualitas_clones_in_dataframe_by_so_clone(row, df_clones)

        rr = compute_query_not_predict(oracle_clone, oracle_clones)
        all_reciprocal_rank["not_predict_results"].append(rr)

    result_siamese_csv = result_siamese_csv.replace(".csv", "")

    all_op = [
        result["OP (Overall Precision)"]
        for result in all_reciprocal_rank["predict_results"]
    ]
    mop = sum(all_op) / len(all_op)
    mrr = total_reciprocal_rank / num_queries
    all_reciprocal_rank[f"MRR (Mean Reciprocal Rank)"] = mrr
    all_reciprocal_rank[f"MOP (Mean Overall Precision)"] = mop

    with open(f"{folder_result}/{result_siamese_csv}.json", "w") as json_file:
        json.dump(all_reciprocal_rank, json_file, indent=4)
    return all_reciprocal_rank


def weighted_average(values, weights):
    if len(values) != len(weights):
        raise ValueError("Number of values must be equal to the number of weights.")

    total = sum(value * weight for value, weight in zip(values, weights))
    weight_sum = sum(weights)

    if weight_sum == 0:
        raise ValueError("Total weight cannot be zero.")

    return total / weight_sum


def validade_time(all_result_time, index):
    try:
        time = all_result_time[index - 1]
    except:
        print("Problem in time")
        time = None

    return time


def get_metrics(optimization_algorithms, temp):
    columns = [
        "execution",
        "filename",
        "ngramSize",
        "cloneSize",
        "QRPercentileNorm",
        "QRPercentileT2",
        "QRPercentileT1",
        "QRPercentileOrig",
        "normBoost",
        "T2Boost",
        "T1Boost",
        "origBoost",
        "simThreshold",
        "time",
        "WA(MRR,MOP) - (0.5,0.5)",
        "WA(MRR,MOP) - (0.7,0.3)",
        "WA(MRR,MOP) - (0.3,0.7)",
        "MRR",
        "MOP",
    ]

    df_clones = pd.read_csv("../oracle_new.csv")
    df_clones = filter_oracle(df_clones)

    for algorithm, filename_temp in zip(optimization_algorithms, temp):
        if os.path.exists(f"result_metrics/{algorithm}/{filename_temp}"):
            shutil.rmtree(f"result_metrics/{algorithm}/{filename_temp}")

        if os.path.exists(f"{algorithm}_result.xlsx"):
            os.remove(f"{algorithm}_result.xlsx")

        if not os.path.exists("results_excel"):
            os.mkdir("results_excel")

        os.mkdir(f"result_metrics/{algorithm}/{filename_temp}")

        directory = f"output_{algorithm}/{filename_temp}"
        folder_result = f"result_metrics/{algorithm}/{filename_temp}"
        results_siamese_csv = get_files_in_folder(directory)
        mrr_by_siamese_result = {}

        time_path = f"./time_record/{algorithm}/{filename_temp}.txt"
        all_result_time = find_lines_with_specific_text(time_path, "Runtime:")
        for index, result_siamese_csv in enumerate(results_siamese_csv):
            mrr_results_by_algorithm = []

            print(index, len(results_siamese_csv), algorithm)

            if result_siamese_csv == "README.md":
                continue

            try:
                df_siamese = format_siamese_output(directory, result_siamese_csv)
                all_metrics = calculate_all_metrics(
                    result_siamese_csv, df_siamese, df_clones, folder_result
                )
            except Exception as inst:
                print(inst)
                open("error_siamese_execution.txt", "a").write(
                    f"{result_siamese_csv}\n"
                )
                print(f"error in {result_siamese_csv}")
                sys.exit()

            mrr = all_metrics["MRR (Mean Reciprocal Rank)"]
            mop = all_metrics["MOP (Mean Overall Precision)"]

            mrr_by_siamese_result[result_siamese_csv] = mrr
            params_str = result_siamese_csv.replace(".csv", "").split("_")
            params = [param for i_, param in enumerate(params_str) if i_ % 2 == 0][1:]

            result_siamese_csv = "_".join(result_siamese_csv.split("_")[1:])
            mrr_result_row = [
                index + 1,
                result_siamese_csv,
                *params,
                validade_time(all_result_time, index),
                weighted_average([mrr, mop], [0.5, 0.5]),
                weighted_average([mrr, mop], [0.7, 0.3]),
                weighted_average([mrr, mop], [0.3, 0.7]),
                mrr,
                mop,
            ]

            mrr_results_by_algorithm.append(mrr_result_row)

            df_metric = pd.DataFrame(mrr_results_by_algorithm, columns=columns)
            df_metric.loc[len(df_metric)] = [None for _ in range(len(columns))]

            excel_file = f"results_excel/{algorithm}_{filename_temp}_result.xlsx"
            if index == 0:
                df_metric.to_excel(excel_file, index=False)

            if index != 0:
                df_final_metric = pd.read_excel(excel_file)
                df_metric = pd.concat([df_final_metric, df_metric])
                df_metric.to_excel(excel_file, index=False)
                del df_metric
                del mrr_results_by_algorithm
