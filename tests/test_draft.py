import pytest

from pywinos import WinOSClient


@pytest.mark.skip('Not implemented')
def test_get_absolute_path():
    tool = WinOSClient()
    response = tool.get_absolute_path('')
    assert response


@pytest.mark.skip('Not implemented')
def test_clean_directory_without_path():
    with pytest.raises(FileNotFoundError):
        tool = WinOSClient()
        response = tool.clean_directory('')
        assert 'The system cannot find the path specified:' in response
