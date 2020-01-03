import re

import pytest

from pywinos import WinOSClient


@pytest.mark.parametrize('command', ['whoami', 'hostname', 'arp -a'])
def test_run_cmd_local(command):
    tool = WinOSClient(host='')
    response = tool.run_cmd(command=command)
    assert response.ok, 'Response is not OK'


def test_run_cmd_invalid_command():
    tool = WinOSClient(host='')
    response = tool.run_cmd('whoamia')
    assert not response.ok, 'Response is OK. Must be False'
    assert not response.stdout, 'STDOUT is not empty. Must be empty'
    assert 'is not recognized as an internal' in response.stderr, \
        'Response is OK. Must be False'


def test_get_local_hostname_ip():
    tool = WinOSClient(host='')
    response = tool.get_local_hostname_ip()
    ip_regex = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')

    assert ip_regex.match(response.ip), 'IP address not found'
