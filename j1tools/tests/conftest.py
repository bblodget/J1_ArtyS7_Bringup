import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--j1debug",
        "-J",
        action="store_true",
        default=False,
        help="Enable debug mode for J1Assembler",
    )


@pytest.fixture
def j1debug(request):
    return request.config.getoption("--j1debug")

