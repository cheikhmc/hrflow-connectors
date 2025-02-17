import pytest

from hrflow_connectors import AuthorizationAuth
from hrflow_connectors import Flatchr
from hrflow_connectors.utils.schemas import HrflowProfile


@pytest.fixture
def auth(config):
    return AuthorizationAuth(value=config.FLATCHR_TOKEN)


def test_PushProfileBaseAction(logger, auth, hrflow_client):
    profile = HrflowProfile(
        key="5746beca5e941a5a55706efd9adfce31f59e6e2b",
        source=dict(key="d42eed17626b7ae3dc05efca363788caef91d44b"),
    )
    response = Flatchr.push_profile(
        auth=auth,
        hrflow_client=hrflow_client(),
        profile=profile,
        vacancy="k0M5O9ylKZnxbQBy",
        company="LEZBvp5b4LdMoVmg",
    )
    assert response.get("status_code") == 201
