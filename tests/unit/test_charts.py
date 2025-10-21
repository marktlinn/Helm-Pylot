import os
from typing import Any, Generator

import pytest

from app.charts.charts import ChartArtifactManager, ChartSourceType


@pytest.fixture(scope="function", autouse=True)
def setup_temp_env_var():
    ENV_VAR_KEY = "REPO_URL"
    os.environ[ENV_VAR_KEY] = "https://myrepo.com"
    yield
    os.environ.pop(ENV_VAR_KEY, None)


@pytest.fixture(scope="session", autouse=True)
def setup_chart_manager() -> Generator[ChartArtifactManager, Any, None]:
    chart_manager = ChartArtifactManager(
        run_cmd=lambda cmd_list: print(f"Executing: {' '.join(cmd_list)}")
    )
    yield chart_manager


def test_charts_setup(setup_chart_manager):
    chart_manager: ChartArtifactManager = setup_chart_manager
    assert chart_manager


def test_get_charts(setup_chart_manager, setup_temp_env_var):
    chart_manager: ChartArtifactManager = setup_chart_manager
    assert chart_manager.get_chart(ChartSourceType.PUBLIC, "test_location")
