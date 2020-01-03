from pywinos import WinOSClient


def test_is_host_available_remote():
    tool = WinOSClient('8.8.8.8')
    response = tool.is_host_available(port=53)
    print(response)
    assert response, 'Response is not True'


def test_is_host_unavailable_remote():
    tool = WinOSClient('8.8.8.8')
    response = tool.is_host_available(port=22)
    assert not response, 'Response is not False'


def test_is_host_available_locally():
    """Execute method locally. Must be True"""

    tool = WinOSClient(host='')
    response = tool.is_host_available()
    assert response, 'Local host is available always'
