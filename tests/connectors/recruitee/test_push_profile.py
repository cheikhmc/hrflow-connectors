import pytest

from hrflow_connectors import AuthorizationAuth
from hrflow_connectors import Recruitee
from hrflow_connectors.utils.schemas import HrflowProfile


@pytest.fixture
def auth(config):
    return AuthorizationAuth(value=config.RECRUITEE_TOKEN)


def test_PushProfile(logger, auth, hrflow_client):

    profile = HrflowProfile(
        key="65903f6989594e72ccf64a10875127b1293fdce3",
        source=dict(key="762d2f25b855f7cfd13e5585ef727d8fb6e752cb"),
    )
    response = Recruitee.push_profile(
        company_id="hrflowai",
        offer_id=None,
        auth=auth,
        hrflow_client=hrflow_client(),
        profile=profile,
    )
    assert response.get("status_code") == 201