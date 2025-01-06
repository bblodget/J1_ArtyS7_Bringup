import pytest
import logging
import sys


def pytest_addoption(parser):
    parser.addoption(
        "--j1debug",
        "-J",
        action="store_true",
        default=False,
        help="Enable debug mode for J1Assembler",
    )


@pytest.fixture(autouse=True)
def setup_logging(request):
    """Configure logging for all tests"""
    # Clear any existing handlers
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    # Configure logging based on debug flag
    debug_enabled = request.config.getoption("--j1debug")
    logging.basicConfig(
        level=logging.DEBUG if debug_enabled else logging.INFO,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
        force=True,  # Override any existing configuration
    )


@pytest.fixture
def j1debug(request):
    return request.config.getoption("--j1debug")
