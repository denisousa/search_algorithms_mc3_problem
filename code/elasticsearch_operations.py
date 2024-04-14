import re
import os
import subprocess
from time import sleep
from dotenv import load_dotenv

load_dotenv()
import requests


def put_template(ngram):
    port = 9000 + ngram
    elasticsearch_url = f"http://http://localhost:{port}"

    index_name = os.getenv("INDEX_NAME")
    index_name = f"{index_name}_n_gram_{ngram}"

    create_index_endpoint = f"{elasticsearch_url}/{index_name}"

    response = requests.put(create_index_endpoint)

    if response.status_code == 200:
        print(f"Index '{index_name}' created successfully.")
    elif response.status_code == 400:
        print(f"Index creation failed. Index '{index_name}' may already exist.")
    else:
        print(
            f"Failed to create index '{index_name}'. Status code: {response.status_code}, Response: {response.text}"
        )


def get_ngram_by_port():
    ngram_by_port = {}
    for ngram_i, port in zip(range(4, 25), range(9200, 9221)):
        ngram_by_port[ngram_i] = port
    return ngram_by_port


def create_one_cluster_elasticserach(ngram):
    port = 9000 + ngram
    elasticsearch_path = os.getenv("ELASTICSEARCH_CLUSTERS")

    if not os.path.exists(elasticsearch_path):
        os.makedirs(elasticsearch_path)

    command_delete = f"trash-put {elasticsearch_path}/elasticsearch-ngram-{ngram}"
    command_unzip = f"tar -xvf elasticsearch-2.2.0.tar.gz -C {elasticsearch_path}"
    command_rename = f"mv {elasticsearch_path}/elasticsearch-2.2.0 {elasticsearch_path}/elasticsearch-ngram-{ngram}"
    elasticsearch_yml_path = (
        f"{elasticsearch_path}/elasticsearch-ngram-{ngram}/config/elasticsearch.yml"
    )
    index_name = os.getenv("INDEX_NAME")
    elasticsearch_yml_content = f"cluster.name: stackoverflow \nindex.name: {index_name}_n_gram_{ngram}\nhttp.port: {port}"

    os.system(command_delete)
    sleep(1)

    os.system(command_unzip)
    sleep(1)

    os.system(command_rename)
    open(elasticsearch_yml_path, "w").write(elasticsearch_yml_content)
    print(f"\nCREATE ELASTICSEARCH elasticsearch-ngram-{ngram}\n")


def delete_indices_incorrect(ngram):
    port = 9000 + ngram
    index_name = os.getenv("INDEX_NAME")

    for i in range(4, 25):
        if i == ngram:
            continue

        complete_index_name = f"{index_name}_n_gram_{i}"
        os.system(
            f'curl -sS -X DELETE "http://localhost:{port}/{complete_index_name}" > /dev/null 2>&1'
        )


def execute_cluster_elasticserach(ngram):
    elasticsearch_path = os.getenv("ELASTICSEARCH_CLUSTERS")
    command_execute = (
        f"{elasticsearch_path}/elasticsearch-ngram-{ngram}/bin/elasticsearch -d"
    )
    print(f"EXECUTING elasticsearch-ngram-{ngram}")
    process = subprocess.Popen(command_execute, shell=True, stdout=subprocess.PIPE)
    process.wait()
    sleep(7)


def stop_cluster_elasticserach(ngram):
    port = 9000 + ngram
    command_stop = f"sudo fuser -k -n tcp {port}"
    print(f"STOP elasticsearch-ngram-{ngram}")
    process = subprocess.Popen(
        command_stop,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        close_fds=True,
    )
    process.wait()


def change_cluster_name(ngram_size):
    command = f"sudo -S kill $(sudo lsof -t -i :9200)"
    process = subprocess.Popen(
        command,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=None,
        stderr=None,
        close_fds=True,
    )
    process.wait()

    elasticsearch_yml_path = (
        "../../siamese-optmization/elasticsearch-2.2.0/config/elasticsearch.yml"
    )
    pattern = r"cluster\.name:\s*(.*?)\s*\n"
    elasticsearch_yml_text = open(elasticsearch_yml_path, "r").read()
    cluster_name = re.search(pattern, elasticsearch_yml_text).group(1)
    elasticsearch_yml_text = elasticsearch_yml_text.replace(
        cluster_name, f"n_gram_{ngram_size}"
    )
    elasticsearch_yml_text = elasticsearch_yml_text
    open(elasticsearch_yml_path, "w").write(elasticsearch_yml_text)

    command = f"../../siamese-optmization/elasticsearch-2.2.0/bin/elasticsearch"
    process = subprocess.Popen(
        command, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True
    )
    process.wait()
