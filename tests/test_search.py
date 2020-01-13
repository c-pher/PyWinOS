def test_search(client_local):
    result = client_local.search('/etc', filter_='host')
    # result = client_local.search('c:\\windows', filter_='fes')
    # result = client_local.search('c:\\windows', starts='Pro')
    # result = client_local.search('c:\\windows', ends='exe')
    assert result, 'Files not found'
