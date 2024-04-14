import gdown
import zipfile
import os
from dotenv import load_dotenv

load_dotenv()


def delete_folder_or_file(filename_path):
    os.system(f"trash-put {filename_path}")


def unzip_file(zip_file_path, extract_to_path):
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        zip_ref.extractall(extract_to_path)


def download_file_from_google_drive(file_id, output_path):
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, output_path, quiet=False)


def download_elasticsearch():
    """Download elasticsearch-2.2.0 and extract to disk."""
    if not os.path.isfile("elasticsearch-2.2.0.tar.gz"):
        os.system(
            "wget https://download.elasticsearch.org/elasticsearch/release/org/elasticsearch/distribution/tar/elasticsearch/2.2.0/elasticsearch-2.2.0.tar.gz"
        )


extract_to_path = os.getenv("PROJECTS_PATH")
if not os.path.exists(extract_to_path):
    os.makedirs(extract_to_path)

datasource_list = [
    {
        "filename": "cut_stackoverflow_filtered.zip",
        "file_id": "19_9nkEytXVWt_GkLxAGdjwnJaGDGUT5n",
    },
    {
        "filename": "qualitas_corpus_clean.zip",
        "file_id": "1Cvm9pYddjB6_PzzqKUd0Ri6BV-fX6MuV",
    },
]

for datasource in datasource_list:
    download_file_from_google_drive(datasource["file_id"], datasource["filename"])
    unzip_file(datasource["filename"], extract_to_path)
    delete_folder_or_file(datasource["filename"])

download_elasticsearch()
