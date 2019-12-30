from pywinos import WinOSClient


def test_local_cmd():
    tool = WinOSClient()
    response = tool.run_cmd('whoami')
    assert response.ok
