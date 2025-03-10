import os
from pathlib import Path
from typing import Generator, List, Optional, Tuple

from boto3.s3 import transfer
from botocore.client import BaseClient
from tqdm import tqdm

from dstack.core.artifact import Artifact
from dstack.core.repo import RepoAddress


def dest_file_path(key: str, output_dir: Path, output_job_dirs: bool) -> Path:
    if output_dir:
        file_path = "/".join(key.split("/")[4:])
    else:
        file_path = "/".join(key.split("/")[5:])
    return output_dir / file_path


def download_run_artifact_files(
    s3_client: BaseClient,
    bucket_name: str,
    repo_address: RepoAddress,
    run_name: str,
    output_dir: Optional[str],
    output_job_dirs: bool,
):
    artifact_prefix = f"artifacts/{repo_address.path()}/{run_name},"

    output_path = Path(output_dir or os.getcwd())

    total_size = 0
    keys = []
    paginator = s3_client.get_paginator("list_objects")
    page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=artifact_prefix)
    for page in page_iterator:
        for obj in page.get("Contents") or []:
            key = obj["Key"]
            total_size += obj["Size"]
            if obj["Size"] > 0 and not key.endswith("/"):
                keys.append(key)

    downloader = transfer.S3Transfer(s3_client, transfer.TransferConfig(), transfer.OSUtils())

    # TODO: Make download files in parallel
    with tqdm(
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        desc=f"Downloading artifacts",
    ) as pbar:

        def callback(size):
            pbar.update(size)

        for key in keys:
            file_path = dest_file_path(key, output_path, output_job_dirs)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            downloader.download_file(bucket_name, key, str(file_path), callback=callback)


def list_run_artifact_files(
    s3_client: BaseClient, bucket_name: str, repo_address: RepoAddress, run_name: str
) -> Generator[Artifact, None, None]:
    artifact_prefix = f"artifacts/{repo_address.path()}/{run_name},"
    paginator = s3_client.get_paginator("list_objects")
    page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=artifact_prefix)
    for page in page_iterator:
        for obj in page.get("Contents") or []:
            if obj["Size"] > 0:
                t = obj["Key"].split("/")
                job_id = t[4]
                artifact_name = t[5]
                artifact_file = "/".join(t[6:])
                yield Artifact(
                    job_id=job_id,
                    name=artifact_name,
                    file=artifact_file,
                    filesize_in_bytes=obj["Size"],
                )


def __remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


def upload_job_artifact_files(
    s3_client: BaseClient,
    bucket_name: str,
    repo_address: RepoAddress,
    job_id: str,
    artifact_name: str,
    local_path: Path,
):
    total_size = 0
    for root, sub_dirs, files in os.walk(local_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            file_size = os.path.getsize(file_path)
            total_size += file_size

    uploader = transfer.S3Transfer(s3_client, transfer.TransferConfig(), transfer.OSUtils())

    with tqdm(
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        desc=f"Uploading artifact '{artifact_name}'",
    ) as pbar:

        def callback(size):
            pbar.update(size)

        prefix = f"artifacts/{repo_address.path()}/{job_id}/{artifact_name}"
        for root, sub_dirs, files in os.walk(local_path):
            for filename in files:
                file_path = Path(os.path.join(root, filename)).absolute()

                key = prefix + __remove_prefix(
                    file_path.as_posix(), local_path.absolute().as_posix()
                )
                uploader.upload_file(
                    str(file_path),
                    bucket_name,
                    key,
                    callback=callback,
                )


def list_run_artifact_files_and_folders(
    s3_client: BaseClient,
    bucket_name: str,
    repo_address: RepoAddress,
    job_id: str,
    path: str,
) -> List[Tuple[str, bool]]:
    prefix = (
        f"artifacts/{repo_address.path()}/{job_id}/" + path + ("" if path.endswith("/") else "/")
    )
    response = s3_client.list_objects(Bucket=bucket_name, Prefix=prefix, Delimiter="/")
    folders = []
    files = []
    if "CommonPrefixes" in response:
        for f in response["CommonPrefixes"]:
            folder_name = f["Prefix"][len(prefix) :]
            if folder_name.endswith("/"):
                folder_name = folder_name[:-1]
            folders.append(folder_name)
    if "Contents" in response:
        for f in response["Contents"]:
            files.append(f["Key"][len(prefix) :])
    return [(folder, True) for folder in folders] + [(file, False) for file in files]
