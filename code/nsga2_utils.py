import yaml

with open("parameters.yml", "r") as file:
    search_space = yaml.safe_load(file)

search_space_values = list(search_space.values())


def get_all_parameters_combination(all_parameters_position):
    all_combinations = []
    for parameter_position in all_parameters_position:
        all_combinations.append(get_paramerters_by_position(parameter_position))

    return all_combinations


def get_paramerters_by_position(parameter_position):
    combination = [
        search_space["ngram"][parameter_position[0]],
        search_space["minCloneSize"][parameter_position[1]],
        search_space["QRPercentileNorm"][parameter_position[2]],
        search_space["QRPercentileT2"][parameter_position[3]],
        search_space["QRPercentileT1"][parameter_position[4]],
        search_space["QRPercentileOrig"][parameter_position[5]],
        search_space["normBoost"][parameter_position[6]],
        search_space["t2Boost"][parameter_position[7]],
        search_space["t1Boost"][parameter_position[8]],
        search_space["origBoost"][parameter_position[9]],
        search_space["simThreshold"][parameter_position[10]],
    ]

    return combination


def transform_parameters_list_to_dict(parameter_position):
    return {
        "ngramSize": search_space["ngram"][parameter_position[0]],
        "minCloneSize": search_space["minCloneSize"][parameter_position[1]],
        "QRPercentileNorm": search_space["QRPercentileNorm"][parameter_position[2]],
        "QRPercentileT2": search_space["QRPercentileT2"][parameter_position[3]],
        "QRPercentileT1": search_space["QRPercentileT1"][parameter_position[4]],
        "QRPercentileOrig": search_space["QRPercentileOrig"][parameter_position[5]],
        "normBoost": search_space["normBoost"][parameter_position[6]],
        "t2Boost": search_space["t2Boost"][parameter_position[7]],
        "t1Boost": search_space["t1Boost"][parameter_position[8]],
        "origBoost": search_space["origBoost"][parameter_position[9]],
        "simThreshold": search_space["simThreshold"][parameter_position[10]],
    }


def transform_parameters_list_to_dict(parameters):
    return {
        "ngramSize": parameters[0],
        "minCloneSize": parameters[1],
        "QRPercentileNorm": parameters[2],
        "QRPercentileT2": parameters[3],
        "QRPercentileT1": parameters[4],
        "QRPercentileOrig": parameters[5],
        "normBoost": parameters[6],
        "t2Boost": parameters[7],
        "t1Boost": parameters[8],
        "origBoost": parameters[9],
        "simThreshold": parameters[10],
    }


def print_results(result):
    for x in result.X:
        best_solution = x
        print("Best solution found:")
        print(
            "Hyperparameters:",
            transform_parameters_list_to_dict([int(x) for x in best_solution]),
        )
        print("Hyperparameters Positions:", best_solution)
        print("\n")
