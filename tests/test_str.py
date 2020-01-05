import pytest

from pywinos import WinOSClient


@pytest.mark.parametrize('host, username, password', [
    ('172.16.0.5', 'admin', 'P@ssw0rd'),
    ('10.10.10.10', 'bobby', 'qawsedrftg'),
    ('', 'user', '123456'),
    ('', '', ''),
])
def test_str(host, username, password):
    tool = WinOSClient(host, username, password)
    response = tool.__str__()
    print(response)
    assert 'Local host' in response
    assert host in response
    assert username in response
    assert password in response
