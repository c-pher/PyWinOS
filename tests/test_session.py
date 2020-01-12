import pytest

from pywinos import WinOSClient


def test_session():
    """Host and credentials are mandatory"""

    with pytest.raises(AttributeError):
        assert WinOSClient().session
