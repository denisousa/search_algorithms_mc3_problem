import re


def cofigure_siamese_text(siamese_csv_name):
    siamese_csv_name = siamese_csv_name.replace("cloneSize-", "")
    siamese_csv_name = siamese_csv_name.replace("ngramSize-", "")
    siamese_csv_name = siamese_csv_name.replace("qrNorm-", "")
    siamese_csv_name = siamese_csv_name.replace("normBoost-", "")
    siamese_csv_name = siamese_csv_name.replace("t2Boost-", "")
    siamese_csv_name = siamese_csv_name.replace("t1Boost-", "")
    siamese_csv_name = siamese_csv_name.replace("origBoost-", "")
    return siamese_csv_name


def extract_numbers(siamese_csv_name):
    pattern = r"-?\d+"
    numbers = re.findall(pattern, siamese_csv_name)
    return numbers


def format_dimension(parms):
    return {
        "cloneSize": parms[1],
        "ngramSize": parms[2],
        "qrNorm": parms[3],
        "normBoost": parms[4],
        "t2Boost": parms[5],
        "t1Boost": parms[6],
        "origBoost": parms[7],
    }


def get_parameters_in_list(siamese_csv_name):
    siamese_csv_name = cofigure_siamese_text(siamese_csv_name)
    return [int(i) for i in extract_numbers(siamese_csv_name)]


def get_parameters_in_dict(siamese_csv_name):
    parms = get_parameters_in_list(siamese_csv_name)
    return format_dimension(parms)
