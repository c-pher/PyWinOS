def test_exists_true(client_local):
    assert client_local.exists('/root')


def test_exists_false(client_local):
    assert client_local.exists('/root')
