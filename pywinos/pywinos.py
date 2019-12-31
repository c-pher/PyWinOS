import logging
import os
import platform
import socket
from dataclasses import dataclass
from subprocess import Popen, PIPE, TimeoutExpired

import winrm
from requests.exceptions import ConnectionError
from winrm import Protocol
from winrm.exceptions import (InvalidCredentialsError,
                              WinRMError,
                              WinRMTransportError,
                              WinRMOperationTimeoutError)

__author__ = 'Andrey Komissarov'
__email__ = 'a.komisssarov@gmail.com'
__date__ = '12.2019'


@dataclass
class Logger:
    name: str
    console: bool = True
    file: bool = False
    date_format: str = '%Y-%m-%d %H:%M:%S'
    format: str = ('%(asctime)-15s '
                   '%(name)s] '
                   '[LINE:%(lineno)d] '
                   '[%(levelname)s] '
                   '%(message)s')
    logger_enabled: bool = True

    def __post_init__(self):
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter(fmt=self.format,
                                           datefmt=self.date_format)
        self.logger.disabled = not self.logger_enabled

        # Console handler with a INFO log level
        if self.console:
            # use param stream=sys.stdout for stdout printing
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            ch.setFormatter(self.formatter)  # Add the formatter
            self.logger.addHandler(ch)  # Add the handlers to the logger

        # File handler which logs debug messages
        if self.file:
            fh = logging.FileHandler(f'{self.name}.log', mode='w')
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(self.formatter)  # Add the formatter
            self.logger.addHandler(fh)  # Add the handlers to the logger


class SuppressFilter(logging.Filter):
    def filter(self, record):
        return 'wsman' not in record.getMessage()


class ResponseParser(Logger):
    """Response parser"""

    def __init__(self, response, *args, **kwargs):
        super().__init__(name=self.__class__.__name__, *args, **kwargs)
        self.response = response

    def __repr__(self):
        # '<Response code {0}, out "{1}", err "{2}">'.
        # format(self.status_code, self.std_out[:20], self.std_err[:20])
        return str(self.response)

    @staticmethod
    def _decoder(response):
        # decode = self.decode
        # if self.get_current_os_name() == 'Windows':
        #     decode = 'cp1252'
        return response.decode('cp1252').strip()

    @property
    def stdout(self) -> str:
        try:
            stdout = self._decoder(self.response.std_out)
        except AttributeError:
            stdout = self._decoder(self.response[1])
        out = stdout if stdout else None
        self.logger.info(out)
        return out

    @property
    def stderr(self) -> str:
        try:
            stderr = self._decoder(self.response.std_err)
        except AttributeError:
            stderr = self._decoder(self.response[2])
        err = stderr if stderr else None
        if err:
            self.logger.error(err)
        return err

    @property
    def exited(self) -> int:
        try:
            exited = self.response.status_code
        except AttributeError:
            exited = self.response[0]
        self.logger.info(exited)
        return exited

    @property
    def ok(self) -> bool:
        try:
            return self.response.status_code == 0
        except AttributeError:
            return self.response[0] == 0


class WinOSClient(Logger):
    _URL = 'https://pypi.org/project/pywinrm/'

    def __init__(
            self,
            host: str = '',
            username: str = '',
            password: str = '',
            logger_enabled: bool = True,
            *args, **kwargs):
        super().__init__(
            name=self.__class__.__name__,
            logger_enabled=logger_enabled,
            *args, **kwargs)

        self.host = host
        self.username = username
        self.password = password
        self.logger_enabled = logger_enabled
        self.logger.disabled = not logger_enabled

    def __str__(self):
        return (
            f'Local host: {self.get_current_os_name()}\n'
            f'Remote IP: {self.host}\n'
            f'Username: {self.username}\n'
            f'Password: {self.password}'
        )

    def is_host_available(self, port: int = 5985, timeout: int = 5):
        """Check remote host is available using specified port"""

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            response = sock.connect_ex((self.host, port))
            result = False if response else True
            self.logger.info(f'{self.host} is available: {result}')
            return result

    @staticmethod
    def get_current_os_name():
        return platform.system()

    # ---------- Remote section ----------
    @property
    def session(self):
        """Create connection to a remote server"""

        session = winrm.Session(self.host, auth=(self.username, self.password))
        return session

    def _protocol(self, endpoint, transport):
        """Create Protocol using low-level API"""

        session = self.session

        protocol = Protocol(
            endpoint=endpoint,
            transport=transport,
            username=self.username,
            password=self.password,
            server_cert_validation='ignore',
            message_encryption='always')

        session.protocol = protocol
        return session

    def _client(
            self,
            command,
            ps: bool = False,
            cmd: bool = False,
            use_cred_ssp: bool = False,
            *args) -> ResponseParser:
        """
        The client to send PowerShell or command-line commands

        :param command: Command to execute
        :param ps: Specify if PowerShel is used
        :param cmd: Specify if command-line is used
        :param use_cred_ssp: Specify if CredSSP is used
        :param args: Arguments for command-line
        :return:
        """

        response = None

        try:
            self.logger.info('[COMMAND] ' + command)
            if ps:  # Use PowerShell
                endpoint = (f'https://{self.host}:5986/wsman'
                            if use_cred_ssp
                            else f'http://{self.host}:5985/wsman')
                transport = 'credssp' if use_cred_ssp else 'ntlm'
                client = self._protocol(endpoint, transport)
                response = client.run_ps(command)
            elif cmd:  # Use command-line
                client = self._protocol(
                    endpoint=f'http://{self.host}:5985/wsman',
                    transport='ntlm')
                response = client.run_cmd(command, [arg for arg in args])
            return ResponseParser(response, logger_enabled=self.logger_enabled)

        # Catch exceptions
        except InvalidCredentialsError as err:
            self.logger.error(f'Invalid credentials: '
                              f'{self.username}@{self.password}. '
                              + str(err))
            raise InvalidCredentialsError
        except ConnectionError as err:
            self.logger.error('Connection error: ' + str(err))
            raise ConnectionError
        except (WinRMError,
                WinRMOperationTimeoutError,
                WinRMTransportError) as err:
            self.logger.error('WinRM error: ' + str(err))
            raise err
        except Exception as err:
            self.logger.error('Unhandled error: ' + str(err))
            self.logger.error('Try to use "run_cmd_local" method instead.')
            raise err

    def run_cmd(self, command, timeout: int = 60, *args) -> ResponseParser:
        """
        Allows to execute cmd command on a remote server.

        Executes command locally if host was not specified
        or host == "localhost/127.0.0.1"

        :param command: command
        :param args: additional command arguments
        :param timeout: timeout
        :return: ResponseParser object
        """

        if not self.host or self.host == 'localhost' \
                or self.host == '127.0.0.1':
            return self._client_local(command, timeout)
        return self._client(command, cmd=True, *args)

    def run_ps(self, command, use_cred_ssp: bool = False):
        """Allows to execute PowerShell command or script using a remote shell

        :param command: Command
        :param use_cred_ssp:
        :return:
        """

        return self._client(command, ps=True, use_cred_ssp=use_cred_ssp)

    # ---------- Local section ----------
    def _client_local(self, cmd, timeout=60):
        """Main function to send command-line commands using subprocess LOCALLY

        :param cmd: string, command
        :param timeout: timeout for command
        :return: Decoded response

        """

        with Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE) as process:
            try:
                self.logger.info('[COMMAND] ' + cmd)
                stdout, stderr = process.communicate(timeout=timeout)
                exitcode = process.wait(timeout=timeout)
                response = exitcode, stdout, stderr
                return ResponseParser(response,
                                      logger_enabled=self.logger_enabled)

            except TimeoutExpired as err:
                process.kill()
                self.logger.error('Timeout exception: ' + str(err))
                raise err

    @staticmethod
    def exists(path) -> bool:
        """Check file/directory exists

        :param path: Full path. Can be network path. Share must be attached!
        :return:
        """

        return os.path.exists(path)

    def debug_info(self):
        self.logger.info('Linux client created')
        self.logger.info(f'Local host: {self.get_current_os_name()}')
        self.logger.info(f'Remote IP: {self.host}')
        self.logger.info(f'Username: {self.username}')
        self.logger.info(f'Password: {self.password}')
        self.logger.info(f'Available: {self.is_host_available()}')
