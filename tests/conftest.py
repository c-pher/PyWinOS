import pytest


@pytest.fixture
def response_cmd_local():
    return 0, b'mypc\\bobby\r\n', b''


@pytest.fixture
def response_cmd_local_err():
    return (
        1,
        b'',
        b"'whoami1' is not recognized as an internal or external command,\r\n"
        b"operable program or batch file.\r\n"
    )


@pytest.fixture()
def create_response_class():
    class Response:
        # Response code 0, out "b'ss-vm1\\administrator'", err "b''"

        def __init__(self, positive: bool):
            self.positive = positive

        @property
        def std_out(self):
            if self.positive:
                return b'my-pc\\bobby'
            return b''

        @property
        def std_err(self):
            if self.positive:
                return b''
            return (
                b"'whoami1' is not recognized as an internal or "
                b"external command,\r\n"
                b"operable program or batch file.\r\n")

        @property
        def status_code(self):
            if self.positive:
                return 0
            return 1

    return Response


@pytest.fixture
def response_cmd_remote(create_response_class):
    r = create_response_class(positive=True)
    return r


@pytest.fixture
def response_cmd_remote_err(create_response_class):
    return create_response_class(positive=False)
