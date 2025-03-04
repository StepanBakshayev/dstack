import sys
import time
from pathlib import Path
from typing import List, Optional

from dstack.backend.aws import artifacts
from dstack.backend.aws.storage import AWSStorage
from dstack.backend.base import BackendType, jobs, runs, tags
from dstack.core.artifact import ArtifactHead, ArtifactSpec
from dstack.core.job import Job, JobStatus
from dstack.core.repo import LocalRepoData, RepoAddress
from dstack.core.tag import TagHead


# TODO move this func to base backend after implementing
# generic upload_job_artifact_files()
def create_tag_from_local_dirs(
    storage: AWSStorage,
    repo_data: LocalRepoData,
    tag_name: str,
    local_dirs: List[str],
):
    local_paths = []
    tag_artifacts = []
    for local_dir in local_dirs:
        path = Path(local_dir)
        if path.is_dir():
            local_paths.append(path)
            tag_artifacts.append(path.name)
        else:
            sys.exit(f"The '{local_dir}' path doesn't refer to an existing directory")

    run_name = runs.create_run(storage, repo_data, BackendType.REMOTE)
    job = Job(
        job_id=None,
        repo_data=repo_data,
        run_name=run_name,
        workflow_name=None,
        provider_name="bash",
        local_repo_user_name=repo_data.local_repo_user_name,
        local_repo_user_email=repo_data.local_repo_user_email,
        status=JobStatus.DONE,
        submitted_at=int(round(time.time() * 1000)),
        image_name="scratch",
        commands=None,
        env=None,
        working_dir=None,
        artifact_specs=[ArtifactSpec(artifact_path=a, mount=False) for a in tag_artifacts],
        port_count=None,
        ports=None,
        host_name=None,
        requirements=None,
        dep_specs=None,
        master_job=None,
        app_specs=None,
        runner_id=None,
        request_id=None,
        tag_name=tag_name,
    )
    jobs.create_job(storage, job, create_head=False)
    for index, local_path in enumerate(local_paths):
        artifacts.upload_job_artifact_files(
            storage.s3_client,
            storage.bucket_name,
            repo_data,
            job.job_id,
            tag_artifacts[index],
            local_path,
        )
    tag_head = TagHead(
        repo_address=repo_data,
        tag_name=tag_name,
        run_name=run_name,
        workflow_name=job.workflow_name,
        provider_name=job.provider_name,
        local_repo_user_name=job.local_repo_user_name,
        created_at=job.submitted_at,
        artifact_heads=[
            ArtifactHead(job_id=job.job_id, artifact_path=a.artifact_path)
            for a in job.artifact_specs
        ]
        if job.artifact_specs
        else None,
    )
    tag_head_key = tags._get_tag_head_key(tag_head)
    storage.put_object(key=tag_head_key, content="")
