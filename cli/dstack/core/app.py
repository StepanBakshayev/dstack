from typing import Dict, Optional, Union

from pydantic import BaseModel

from dstack.utils.common import _quoted


class AppSpec(BaseModel):
    port_index: int
    app_name: str
    url_path: Union[str, None] = (None,)
    url_query_params: Union[Dict[str, str], None] = (None,)

    def __str__(self) -> str:
        return (
            f"AppSpec(app_name={self.app_name}, port_index={self.port_index}, "
            f"url_path={_quoted(self.url_path)}, url_query_params={self.url_query_params})"
        )


class AppHead(BaseModel):
    job_id: str
    app_name: str

    def __str__(self) -> str:
        return f'AppHead(job_id="{self.job_id}", app_name="{self.app_name})'
