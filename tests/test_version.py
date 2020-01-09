from pywinos import WinOSClient, __version__


def test_version():
    tool = WinOSClient()
    response = tool.version
    assert response == __version__
