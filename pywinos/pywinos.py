import hashlib
import logging
import os
import platform
import shutil
import socket
import sys
import zipfile
from dataclasses import dataclass
from datetime import datetime
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
    """The cross-platform tool to work with remote and local Windows OS.

    Returns response object with exit code, sent command, stdout/sdtderr.
    Check response methods.
    """

    _URL = 'https://pypi.org/project/pywinrm/'

    def __init__(
            self,
            host: str = "",
            username: str = "",
            password: str = "",
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

    def list_all_methods(self):
        """Returns all available public methods"""

        return [method for method in dir(self) if not method.startswith('_')]

    def is_host_available(
            self,
            port: int = 5985,
            timeout: int = 5
    ) -> bool:
        """Check remote host is available using specified port.

        Port 5985 used by default
        """

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            response = sock.connect_ex((self.host, port))
            result = False if response else True
            self.logger.info(f'{self.host} is available: {result}')
            return result

    @staticmethod
    def get_current_os_name():
        """Returns current OS name"""

        return platform.system()

    # ---------- Remote section ----------
    @property
    def session(self):
        """Create WinRM session connection to a remote server"""

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
        """The client to send PowerShell or command-line commands

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
        :return: Object with exit code, stdout and stderr
        """

        if not self.host or self.host == 'localhost' \
                or self.host == '127.0.0.1':
            return self._client_local(command, timeout)
        return self._client(command, cmd=True, *args)

    def run_ps(self, command, use_cred_ssp: bool = False) -> ResponseParser:
        """Allows to execute PowerShell command or script using a remote shell.

        :param command: Command
        :param use_cred_ssp: Use CredSSP
        :return: Object with exit code, stdout and stderr
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

    @staticmethod
    def get_hostname_ip() -> tuple:
        """Get tuple of IP and hostname"""

        host_name = socket.gethostname()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0], host_name

    @staticmethod
    def search(directory, ends=None, starts=None, filter_=None) -> list:
        """Search for file(s)

        :param directory: Root directory to search
        :param ends: Ends with
        :param starts: Start with
        :param filter_: Search files by containing
        :return: list of files
        """

        result = []
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)

            if ends:
                if file_path.endswith(ends):
                    result.append(file)
            elif starts:
                if file_path.startswith(starts):
                    result.append(file)
            elif filter_:
                if filter_ in file_path:
                    result.append(file)

        return result

    def get_last_file(self, path, prefix='', ends=''):
        """Get last file from specified directory

        :param path: Full path to the share (directory)
        :param prefix: Prefix
        :param ends:
        :return:
        """

        all_builds = [
            os.path.join(path, file) for file in os.listdir(path) if
            os.path.isfile(os.path.join(path, file)) and
            file.startswith(prefix) and file.endswith(ends)
        ]

        try:
            last_build = max(all_builds, key=os.path.getctime)
            return os.path.basename(last_build)
        except ValueError as err:
            self.logger.error(f'{err}. '
                              f'Maybe file with specified criteria not found.')
            return 'File not found. Try another search parameters.'

    @staticmethod
    def get_absolute_path():
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @staticmethod
    def get_md5(file):
        """
        Open file and calculate MD5

        :param file: Full file path
        :type file: str
        :return: File's MD5 hash
        """

        with open(file, 'rb') as f:
            m = hashlib.md5()
            while True:
                data = f.read(8192)
                if not data:
                    break
                m.update(data)
            return m.hexdigest()

    @staticmethod
    def clean_directory(path):
        """Clean (remove) all files from a windows directory"""

        try:
            for the_file in os.listdir(path):
                file_path = os.path.join(path, the_file)
                basename = os.path.basename(file_path)

                if os.path.isfile(file_path):
                    if basename != 'pagefile.sys':
                        os.remove(file_path)
                elif os.path.isdir(file_path):
                    if basename != 'System Volume Information':
                        shutil.rmtree(file_path)
            return True
        except OSError as e:
            print(f'The user name or password to {path} is incorrect', e)
            raise e

    def copy(self, source, destination, new_name=None):
        """Copy file to a remote windows directory.

        Creates destination directory if does not exist.

        :param source: Source file to copy
        :param destination: Destination directory.
        :param new_name: Copy file with a new name if specified.
        :return: Check copied file exists
        """

        # Get full destination path
        dst_full = (os.path.join(destination, new_name)
                    if new_name
                    else
                    destination)

        # Create directory
        dir_name = os.path.dirname(dst_full) if new_name else destination
        self.create_directory(dir_name)

        try:
            shutil.copy(source, dst_full)
        except FileNotFoundError as err:
            self.logger.error(f'ERROR occurred during file copy. {err}')
            raise err

        return self.exists(dst_full)

    @staticmethod
    def unzip(path_to_zip_file, target_directory=None):
        """
        Extract .zip archive to destination folder
        Creates destination folder if it does not exist
        """

        directory_to_extract_to = target_directory

        if not target_directory:
            directory_to_extract_to = os.path.dirname(path_to_zip_file)

        with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
            zip_ref.extractall(directory_to_extract_to)
        print('Unzipped to:', directory_to_extract_to)

        return target_directory

    def create_directory(self, path):
        """Create directory. No errors if it already exists."""

        os.makedirs(path, exist_ok=True)

        return self.exists(path)

    @staticmethod
    def timestamp(sec=False):
        """Get time stamp"""

        if sec:
            return datetime.now().strftime('%Y%m%d_%H%M%S')
        return datetime.now().strftime('%Y%m%d_%H%M')

    @staticmethod
    def ping_host(ip, packets_number=4):
        response = os.system(f'ping -n {packets_number} {ip}')
        if response:
            return False
        return True

    def debug_info(self):
        self.logger.info('Linux client created')
        self.logger.info(f'Local host: {self.get_current_os_name()}')
        self.logger.info(f'Remote IP: {self.host}')
        self.logger.info(f'Username: {self.username}')
        self.logger.info(f'Password: {self.password}')
        self.logger.info(f'Available: {self.is_host_available()}')
        self.logger.info(sys.version)
