import os

from pywinos import WinOSClient


def test_get_current_os_name():
    tool = WinOSClient()
    response = tool.get_current_os_name()

    if os.name == 'nt':
        assert 'Windows' in response, 'Current OS name is not Windows'
    else:
        assert 'Linux' in response, 'Current OS name is not Windows'
