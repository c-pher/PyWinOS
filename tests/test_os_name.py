import os

import pytest


@pytest.mark.skipif(os.name != 'nt', reason='Can be verified on windows only')
def test_is_windows_true(client_local):
    assert client_local.is_windows, 'response is not Windows'


@pytest.mark.skipif(os.name == 'nt', reason='Cannot be verified on windows')
def test_is_windows_false(client_local):
    assert not client_local.is_windows, 'response is not Windows'


@pytest.mark.skipif(os.name != 'posix', reason='Can be verified on Linux only')
def test_is_linux_true(client_local):
    assert client_local.is_linux, 'response is not Linux'


@pytest.mark.skipif(os.name == 'posix', reason='Cannot be verified on Linux')
def test_is_linux_false(client_local):
    assert not client_local.is_linux, 'response is not Linux'
