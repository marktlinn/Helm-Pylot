import os
from enum import StrEnum
from pathlib import Path
from typing import Callable

from ..logger import logger

# Constants and Env Vars
TEMP_CHART_PATH = "/tmp/downloaded_chart.tgz"


type RunCmdFunc = Callable[[list[str]], None]


class ChartSourceType(StrEnum):
    PUBLIC = "PUBLIC_REPO"
    PRIVATE = "PRIVATE_BUCKET"


class ChartArtifactManager:
    def __init__(self, run_cmd: RunCmdFunc):
        self.run_cmd = run_cmd

    def get_chart(
        self,
        src_type: ChartSourceType,
        location: str,
        local_path: str = TEMP_CHART_PATH,
    ):
        logger.info(
            f"Retrieving chart from source type '{src_type}' at location {location}"
        )

        match src_type:
            case ChartSourceType.PUBLIC:
                repo_url = os.environ.get("REPO_URL")
                if not repo_url:
                    raise ValueError(
                        "REPO_URL environment variable required for PUBLIC_REPO"
                    )

                repo_name = "REPO_NAME"  # TODO: take name dynamically

                self.run_cmd(["helm", "repo", "add", repo_name, repo_url])
                self.run_cmd(["helm", "repo", "update"])

                self.run_cmd(
                    ["helm", "pull", location, "--untar", "--destination", "/tmp"]
                )

                # location = /tmp/chart-name
                chart_name = Path(location).name  # e.g. "chart-name"

                return f"/tmp/{chart_name}"

            case ChartSourceType.PRIVATE:
                # handle aws bucket
                if location.startswith("s3://"):
                    self.run_cmd(["aws", "s3", "cp", location, local_path])

                elif location.startswith("gs://"):
                    # handle GCP bucket
                    self.run_cmd(["gcloud", "storage", "cp", location, local_path])
                else:
                    raise ValueError(
                        f"Unsupported cloud location scheme in location: '{location}'"
                    )

                logger.info("Successfully downloaded chart package to 'local_path'")
                return local_path

            case _:
                raise ValueError(
                    f"Unsupported 'src_type' for chart: '{src_type}' - expects one of {ChartSourceType.PRIVATE}, {ChartSourceType.PUBLIC}"
                )

    def deploy_chart(self, chart_path: str, release_name: str, namespace: str) -> None:
        cmds = [
            "helm",
            "upgrade",
            "--install",
            release_name,
            chart_path,
            "--namespace",
            namespace,
            "--atomic",  # ensure all of nothing
            "--wait",  # TODO: make optional
        ]

        values_file_path = os.environ.get("HELM_VALUES_FILE")
        if values_file_path and os.path.exists(values_file_path):
            logger.info(f"Applying override values from file: {values_file_path}")
            cmds.extend(["-f", values_file_path])
        elif values_file_path:
            logger.warning(
                f"HELM_VALUES_FILE specified, but file not found at path '{values_file_path}'"
            )

        self.run_cmd(cmds)
