import pytest

from pywinos import WinOSClient


@pytest.mark.parametrize('command', ['whoami', 'hostname', 'arp -a'])
def test_run_cmd_local(command):
    tool = WinOSClient()
    response = tool.run_cmd(command=command)
    assert response.ok, 'Response is not OK'
