from elasticsearch_operations import (
    execute_cluster_elasticserach,
    stop_cluster_elasticserach,
    delete_indices_incorrect,
)
from files_operations import most_recent_file
import subprocess
import uuid
import os
import gc
import re
from dotenv import load_dotenv
import requests
import datetime

load_dotenv()


def clear_cache(port):
    url = f"http://localhost:{port}/_cache/clear"
    response = requests.post(url)
    if response.status_code == 200:
        print("Elasticsearch cache was cleam with success.")
    else:
        print("Error when clean Elasticsearch cache.")


def finish_siamese_process(output_path, properties_path):
    most_recent_siamese_output, _ = most_recent_file(output_path)
    new_output_name = properties_path.split("/")[-1].replace(
        ".properties", f"_{uuid.uuid4()}.csv"
    )
    i = int(len(os.listdir(output_path)))
    os.rename(
        f"{output_path}/{most_recent_siamese_output}",
        f"{output_path}/{i}_{new_output_name}",
    )
    gc.collect()
    os.system("sync")


def get_config_path(parms):
    clonesSize = f'cS_{parms["minCloneSize"]}_'
    ngramSize = f'nS_{parms["ngramSize"]}_'
    QRPercentileNorm = f'qrN_{parms["QRPercentileNorm"]}_'
    QRPercentileT2 = f'qrT2_{parms["QRPercentileT2"]}_'
    QRPercentileT1 = f'qrT1_{parms["QRPercentileT1"]}_'
    QRPercentileOrig = f'qrO_{parms["QRPercentileOrig"]}_'
    normBoost = f'boN_{parms["normBoost"]}_'
    t2Boost = f'boT2_{parms["t2Boost"]}_'
    t1Boost = f'boT1_{parms["t1Boost"]}_'
    origBoost = f'boOr_{parms["origBoost"]}_'
    simThreshold = f'simT_{parms["simThreshold"]}'
    config_name = (
        ngramSize
        + clonesSize
        + QRPercentileNorm
        + QRPercentileT2
        + QRPercentileT1
        + QRPercentileOrig
        + normBoost
        + t2Boost
        + t1Boost
        + origBoost
        + simThreshold
    )
    destination_file = f'./configurations_{parms["algorithm"]}'
    return f"{destination_file}/{config_name}.properties"


def generate_config_file(parms):
    elasticsearch_path = os.getenv("ELASTICSEARCH_CLUSTERS")
    elasticsearch_path = (
        f'{elasticsearch_path}/elasticsearch-ngram-{parms["ngramSize"]}'
    )

    config = open("config-search.properties", "r").read()
    config = config.replace(
        "elasticsearchLoc=", f"elasticsearchLoc={elasticsearch_path}"
    )
    config = config.replace("outputFolder=", f'outputFolder={parms["output_folder"]}')
    config = config.replace("cluster=cluster", f"cluster=stackoverflow")
    config = config.replace("ngramSize=", f'ngramSize={parms["ngramSize"]}')
    config = config.replace("t2NgramSize=", f't2NgramSize={parms["ngramSize"]}')
    config = config.replace("t1NgramSize=", f't1NgramSize={parms["ngramSize"]}')
    config = config.replace("minCloneSize=", f'minCloneSize={parms["minCloneSize"]}')
    config = config.replace(
        "QRPercentileNorm=", f'QRPercentileNorm={parms["QRPercentileNorm"]}'
    )
    config = config.replace(
        "QRPercentileT2=", f'QRPercentileT2={parms["QRPercentileT2"]}'
    )
    config = config.replace(
        "QRPercentileT1=", f'QRPercentileT1={parms["QRPercentileT1"]}'
    )
    config = config.replace(
        "QRPercentileOrig=", f'QRPercentileOrig={parms["QRPercentileOrig"]}'
    )
    config = config.replace("normBoost=", f'normBoost={parms["normBoost"]}')
    config = config.replace("t2Boost=", f't2Boost={parms["t2Boost"]}')
    config = config.replace("t1Boost=", f't1Boost={parms["t1Boost"]}')
    config = config.replace("origBoost=", f'origBoost={parms["origBoost"]}')
    config = config.replace("simThreshold=", f'simThreshold={parms["simThreshold"]}')
    config = config.replace(
        "index=", f'index=qualitas_corpus_n_gram_{parms["ngramSize"]}'
    )

    properties_path = get_config_path(parms)
    open(properties_path, "w").write(config)
    return properties_path


def execute_siamese_search(**parms):
    stop_cluster_elasticserach(parms["ngramSize"])
    execute_cluster_elasticserach(parms["ngramSize"])
    delete_indices_incorrect(parms["ngramSize"])
    port = 9000 + int(parms["ngramSize"])
    properties_path = generate_config_file(parms)
    output_path = parms["output_folder"]

    project_path = os.getenv("PROJECT_TO_SEARCH")
    index_name = os.getenv("INDEX_NAME")
    index_name = f'{index_name}_n_gram_{parms["ngramSize"]}'

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    i = int(len(os.listdir(output_path))) + 1
    print(f"Count {i}")
    print(f"Combination {parms}")

    print(datetime.datetime.now())
    print()

    command = f"sudo nice -n -10 java -XX:ParallelGCThreads=10 -Xmx4g -jar ./siamese-0.0.6-SNAPSHOT.jar -i {project_path} -cf ./{properties_path}"
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=None, close_fds=True
    )
    process.wait()

    stdout = process.stdout.read().decode("utf-8")
    print(f"\n\n{stdout}\n\n")

    clear_cache(port)

    if "does not exist" in stdout:
        execute_siamese_search(**parms)

    siamese_result_filename, siamese_result_text = most_recent_file(output_path)
    format_result_text = re.sub(r"\s", "", siamese_result_text)
    if format_result_text == "":
        os.remove(f"{output_path}/{siamese_result_filename}")
        execute_siamese_search(**parms)

    stop_cluster_elasticserach(parms["ngramSize"])
    finish_siamese_process(output_path, properties_path)
