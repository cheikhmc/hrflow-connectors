import pytest

from hrflow_connectors import OAuth2EmailPasswordBody
from hrflow_connectors import Breezyhr
from hrflow_connectors.utils.schemas import HrflowProfile


@pytest.fixture
def auth(config):
    auth = OAuth2EmailPasswordBody(
        access_token_url="https://api.breezy.hr/v3/signin",
        email=config.BREEZYHR_EMAIL,
        password=config.BREEZYHR_PASSWORD,
    )
    return auth


def test_PushProfileBaseAction(logger, auth, hrflow_client):
    profile = HrflowProfile(
        key="a7e7fa4af68e7c450f2b708d14a3bda9b6ade5d9",
        source=dict(key="762d2f25b855f7cfd13e5585ef727d8fb6e752cb"),
    )
    response = Breezyhr.push_profile(
        auth=auth,
        position_id="edc0330a0f3801",
        company_name="Hrflow.ai",
        hrflow_client=hrflow_client("dev-demo"),
        profile=profile,
    )
    assert response.get("status_code") == 201
