import logging
import os
import shutil
import subprocess
import sys
import pathlib
from datetime import datetime

from s3fs import S3FileSystem

# Necessary to avoid writing checksums into the COGs when uploading them to the bucket (cf. https://github.com/boto/boto3/issues/4435)
os.environ["AWS_REQUEST_CHECKSUM_CALCULATION"] = "when_required"
os.environ["AWS_RESPONSE_CHECKSUM_VALIDATION"] = "when_required"

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="[%(asctime)s | %(name)s::%(module)s.py:%(lineno)d | %(process)d] %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

rim2d_binary = "/usr/local/bin/RIM2D"


def download_folder_from_s3_bucket(
    local_path, bucket_path, endpoint_url, key, secret, anon=False
):
    """
    Download a folder from an S3 bucket.

    :param local_path:
    :param bucket_path:
    :param endpoint_url:
    :param key:
    :param secret:
    :param anon:
    :return:
    """
    s3 = S3FileSystem(endpoint_url=endpoint_url, key=key, secret=secret, anon=anon)
    s3.get(bucket_path, local_path, recursive=True)


def upload_folder_to_s3_bucket(
    local_path, bucket_path, endpoint_url, key, secret, anon=False
):
    """
    Upload a folder to an S3 bucket.

    :param local_path: use "<folder>/*" to copy only the content of the folder not the folder itself
    :param bucket_path:
    :param endpoint_url:
    :param key:
    :param secret:
    :param anon:
    :return:
    """
    logger.info(
        f"Start uploading outputs from '{local_path}' to '{endpoint_url}/{bucket_path}'"
    )
    files = [file for file in pathlib.Path(local_path).rglob("*") if file.is_file()]
    idx = 1
    count = len(files)
    logger.info(f"Start Uploading {count} files")
    s3 = S3FileSystem(endpoint_url=endpoint_url, key=key, secret=secret, anon=anon)
    for file in files:
        destination = f"{bucket_path}{file.name}"
        print(f"[{idx}/{count}] Uploading {file.name}")
        s3.put(str(file), destination)
        idx += 1
    logger.info(f"Finished uploading {count} files")


def download_from_s3_bucket(
    local_path, bucket_path, endpoint_url, key, secret, anon=False
):
    """
    Download a file from an S3 bucket.

    :param local_path:
    :param bucket_path:
    :param endpoint_url:
    :param key:
    :param secret:
    :param anon:
    :return:
    """
    s3 = S3FileSystem(endpoint_url=endpoint_url, key=key, secret=secret, anon=anon)
    with s3.open(bucket_path, "rb") as bucket_file_obj:
        with open(local_path, "wb") as local_file_obj:
            local_file_obj.write(bucket_file_obj.read())
            logger.info("Download succeeded.")


def upload_to_s3_bucket(local_path, bucket_path, endpoint_url, key, secret, anon=False):
    """
    Upload a file to an S3 bucket.

    :param local_path:
    :param bucket_path:
    :param endpoint_url:
    :param key:
    :param secret:
    :param anon:
    :return:
    """
    logger.info(f"Try to upload {local_path} to {bucket_path}.")
    s3 = S3FileSystem(endpoint_url=endpoint_url, key=key, secret=secret, anon=anon)
    with open(local_path, "rb") as local_file_obj:
        with s3.open(bucket_path, "wb") as bucket_file_obj:
            bucket_file_obj.write(local_file_obj.read())
            logger.info("Upload succeeded.")


def handle_inputs() -> str:
    # inputs
    inputs_bucket_endpoint = os.getenv("PROCESS_INPUTS_BUCKET_ENDPOINT")
    inputs_bucket_key = os.getenv("PROCESS_INPUTS_BUCKET_KEY")
    inputs_bucket_secret = os.getenv("PROCESS_INPUTS_BUCKET_SECRET")
    inputs_bucket_name = os.getenv("PROCESS_INPUTS_BUCKET_NAME")
    inputs_bucket_path_prefix = os.getenv("PROCESS_INPUTS_BUCKET_PATH_PREFIX")
    inputs_local_path_prefix = os.getenv("PROCESS_INPUTS_LOCAL_PATH_PREFIX")

    inputs_bucket_full_path = f"{inputs_bucket_name}/{inputs_bucket_path_prefix}"
    logger.info(
        f"Start downloading inputs  from '{inputs_bucket_endpoint}/{inputs_bucket_full_path}' to '{inputs_local_path_prefix}'"
    )
    download_folder_from_s3_bucket(
        inputs_local_path_prefix,
        inputs_bucket_full_path,
        inputs_bucket_endpoint,
        inputs_bucket_key,
        inputs_bucket_secret,
    )

    config_file_path = None
    for file in os.listdir(inputs_local_path_prefix):
        if file.endswith(".def"):
            config_file_path = os.path.join(inputs_local_path_prefix, file)
            break

    if config_file_path is None:
        raise RuntimeError(
            f"Could not find any *.def file in '{inputs_local_path_prefix}'."
        )
    logger.info(
        f"Finished downloading inputs. Identified config file: '{config_file_path}'"
    )
    return config_file_path


def call_rim2d(config_file_path: str):
    rim2d_exit_code = None
    command = [rim2d_binary, config_file_path]
    if ".flex." in config_file_path:
        command.extend(["--def", "flex"])

    logger.info(f"Calling RIM2D: '{command}'")
    with subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    ) as p:
        while True:
            output = p.stdout.read(1).decode("utf-8")
            if output == "" and p.poll() is not None:
                rim2d_exit_code = p.poll()
                logger.info(f"Subprocess terminated with '{rim2d_exit_code}'")
                break
            if output != "":
                sys.stdout.write(output)
                sys.stdout.flush()
    if rim2d_exit_code != 0:
        raise RuntimeError(f"RIM2D exited with non zero exit code '{rim2d_exit_code}'")
    logger.info("RIM2D finished without error")


def handle_outputs(pygeoapi_process_id, pygeoapi_job_id) -> str:
    # outputs
    outputs_bucket_endpoint = os.getenv("PROCESS_OUTPUTS_BUCKET_ENDPOINT")
    outputs_bucket_key = os.getenv("PROCESS_OUTPUTS_BUCKET_KEY")
    outputs_bucket_secret = os.getenv("PROCESS_OUTPUTS_BUCKET_SECRET")
    outputs_bucket_name = os.getenv("PROCESS_OUTPUTS_BUCKET_NAME")
    outputs_bucket_path_prefix = os.getenv("PROCESS_OUTPUTS_BUCKET_PATH_PREFIX")
    outputs_local_path_prefix = os.getenv("PROCESS_OUTPUTS_LOCAL_PATH_PREFIX")

    outputs_bucket_full_path = f"{outputs_bucket_name}/{outputs_bucket_path_prefix}{pygeoapi_process_id}/outputs/{datetime.now().strftime('%Y-%m-%d')}_{pygeoapi_job_id}/"
    upload_folder_to_s3_bucket(
        outputs_local_path_prefix,
        outputs_bucket_full_path,
        outputs_bucket_endpoint,
        outputs_bucket_key,
        outputs_bucket_secret,
    )
    return f"{outputs_bucket_endpoint}/{outputs_bucket_full_path}"


def calc_timing(
    start: datetime, inputs_done: datetime, rim2d_done: datetime, outputs_done: datetime
) -> tuple[float, float, float, float]:
    return (
        (outputs_done - start).total_seconds(),
        (inputs_done - start).total_seconds(),
        (rim2d_done - inputs_done).total_seconds(),
        (outputs_done - rim2d_done).total_seconds(),
    )


def prepare_folders() -> None:
    outputs_folder = os.path.dirname(
        os.getenv("PROCESS_OUTPUTS_LOCAL_PATH_PREFIX", "/tmp/outputs/*")
    )
    os.makedirs(outputs_folder, exist_ok=True)
    logger.info(f"Ensured existence of output folder '{outputs_folder}'")

    inputs_folder = os.path.dirname(
        os.getenv("PROCESS_INPUTS_LOCAL_PATH_PREFIX", "/tmp/inputs/")
    )
    os.makedirs(inputs_folder, exist_ok=True)
    logger.info(f"Ensured existence of input folder '{inputs_folder}'")


def clean_up_folders() -> None:
    outputs_folder = os.path.dirname(
        os.getenv("PROCESS_OUTPUTS_LOCAL_PATH_PREFIX", "/tmp/outputs/")
    )
    shutil.rmtree(outputs_folder)
    logger.info(f"Removed output folder '{outputs_folder}'")

    inputs_folder = os.path.dirname(
        os.getenv("PROCESS_INPUTS_LOCAL_PATH_PREFIX", "/tmp/inputs/")
    )
    shutil.rmtree(inputs_folder)
    logger.info(f"Removed input folder '{inputs_folder}'")


if __name__ == "__main__":
    start = datetime.now()
    pygeoapi_job_id = os.getenv("PYGEOAPI_JOB_ID", "JOB_ID_NOT_FOUND")
    pygeoapi_process_id = os.getenv("PYGEOAPI_PROCESS_ID", "PROCESS_ID_NOT_FOUND")
    logger.info(f"Start RIM2D wrapper script for job '{pygeoapi_job_id}'")
    logger.info(f"CWD  : '{os.getcwd()}'")
    logger.info(f"RIM2D: '{rim2d_binary}'")
    prepare_folders()

    config_file_path = handle_inputs()
    inputs_done = datetime.now()
    call_rim2d(config_file_path)
    rim2d_done = datetime.now()
    output_target = handle_outputs(pygeoapi_process_id, pygeoapi_job_id)

    clean_up_folders()

    logger.info(f"Finished RIM2D wrapper script for job '{pygeoapi_job_id}'")
    overall, inputs, rim2d, outputs = calc_timing(
        start, inputs_done, rim2d_done, outputs_done=datetime.now()
    )
    logger.info(f"Inputs handling : {inputs:8.3f}s")
    logger.info(f"RIM2D processing: {rim2d:8.3f}s")
    logger.info(f"Outputs handling: {outputs:8.3f}s")
    logger.info("---------------------------")
    logger.info(f"Overall runtime : {overall:8.3f}s")
    logger.info("PYGEOAPI_K8S_MANAGER_RESULT_MIMETYPE:application/json")
    process_id = os.getenv("PYGEOAPI_PROCESS_ID", "process-id-not-defined-in-env")
    logger.info(
        f'PYGEOAPI_K8S_MANAGER_RESULT_START\n{{"id":"{process_id}","value":"{output_target}"}}'
    )
