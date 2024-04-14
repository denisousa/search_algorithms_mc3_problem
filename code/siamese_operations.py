import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()


def remove_absolute_path(path, project_ref):
    only_project_to_search = project_ref.split("/")[-1]
    clean_path = path.split(only_project_to_search)[-1].split(".java")[0][1:] + ".java"
    return clean_path


def get_numbers_from_absolute_path(path):
    return int(path.split("#")[-2]), int(path.split("#")[-1])


def get_method_name(path, project_ref):
    only_project_to_search = project_ref.split("/")[-1]
    method_clean = path.split(only_project_to_search)[-1].split("#")[0].split("_")[-1]
    return method_clean


def format_clones(search_clone, clone):
    clean_path1 = remove_absolute_path(search_clone, os.getenv("PROJECT_TO_SEARCH"))
    start1, end1 = get_numbers_from_absolute_path(search_clone)
    method1 = get_method_name(search_clone, os.getenv("PROJECT_TO_SEARCH"))

    clean_path2 = remove_absolute_path(clone, os.getenv("PROJECT_TO_INDEX"))
    start2, end2 = get_numbers_from_absolute_path(clone)
    method2 = get_method_name(clone, os.getenv("PROJECT_TO_INDEX"))

    return {
        "file1": clean_path1,
        "start1": start1,
        "end1": end1,
        "method1": method1,
        "file2": clean_path2,
        "start2": start2,
        "end2": end2,
        "method2": method2,
    }


def get_path_from_project_to_search(path):
    return path.split("/")[-1]


def get_path_from_project_to_index(path):
    projects_path = os.getenv("PROJECT_TO_INDEX")

    if "./" in projects_path:
        projects_path = projects_path.replace("./", "")

    path = path.split("/qualitas_corpus_clean/")[-1]

    return path


def format_siamese_output(output_path, siamese_output_name):
    siamese_clones = []
    csv_lines = [
        line
        for line in open(f"{output_path}/{siamese_output_name}", "r")
        .read()
        .rstrip()
        .split("\n")
    ]

    for line in csv_lines:
        search_clone, indexed_clones = line.split(",")[0], line.split(",")[1:]
        [
            siamese_clones.append(format_clones(search_clone, clone))
            for clone in indexed_clones
        ]

    df_siamese_clones = pd.DataFrame(data=siamese_clones)
    return df_siamese_clones
