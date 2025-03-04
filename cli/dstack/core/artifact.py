from pydantic import BaseModel


class ArtifactSpec(BaseModel):
    artifact_path: str
    mount: bool

    def __str__(self) -> str:
        return f'ArtifactSpec(artifact_path="{self.artifact_path}", ' f"mount={self.mount})"


class ArtifactHead(BaseModel):
    job_id: str
    artifact_path: str

    def __str__(self) -> str:
        return f'ArtifactHead(job_id="{self.job_id}", artifact_path="{self.artifact_path})'


class Artifact(BaseModel):
    job_id: str
    name: str
    file: str
    filesize_in_bytes: int
