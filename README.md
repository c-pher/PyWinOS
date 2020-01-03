[![Build Status](https://travis-ci.org/c-pher/PyWinOS.svg?branch=master)](https://travis-ci.org/agegemon/PyWinOS)
[![Coverage Status](https://coveralls.io/repos/github/c-pher/PyWinOS/badge.svg?branch=master)](https://coveralls.io/github/agegemon/PyWinOS?branch=master)

# PyWinOS
The cross-platform tool to work with remote and local Windows OS.

PyWinOS uses the Windows Remote Manager (WinRM) service. It can establish connection to a remote server based on Windows OS and execute commands:
- PowerShell
- Command line
- WMI.

It can execute commands locally using subprocess and command-line too.

For more information on WinRM, please visit [Microsoft’s WinRM site](https://docs.microsoft.com/en-us/windows/win32/winrm/portal?redirectedfrom=MSDN)
It based on [pywinrm](https://pypi.org/project/pywinrm/).

PyWinOS returns object with **exit code, stdout and sdtderr** response.

## Installation
For most users, the recommended method to install is via pip:
```cmd
pip install PyWinOS
```
## Import
```python
from pywinos import WinOSClient
```
---
## Usage (remote)
#### PowerShell:
```python
from pywinos import WinOSClient

tool = WinOSClient(host='172.16.0.126', username='administrator', password='rds123RDS', logger_enabled=True)
response = tool.run_ps('$PSVersionTable.PSVersion')

print(response)  
# ResponseParser(response=(0, 'Major  Minor  Build  Revision\r\n-----  -----  -----  --------\r\n5      1      17763  592', None, '$PSVersionTable.PSVersion'))
print(response.exited)  # 0
print(response.stdout)
# Major  Minor  Build  Revision
# -----  -----  -----  --------
# 5      1      17763  592

# stderr in PowerShell contains some text by default    
print(response.stderr)  # <Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04"><Ob...
print(response.ok)  # True
```

#### Command line:
```python
from pywinos import WinOSClient

tool = WinOSClient('172.16.0.126', 'administrator', 'P@ssw0rd', logger_enabled=False)
response = tool.run_cmd('whoami')

print(response)  # <Response code 0, out "b'\r\nMajor  Minor  Buil'", err "b''">
print(response.exited)  # 0
print(response.stdout)  # test-vm1\administrator
print(response.stderr)  # None
print(response.ok)  # True

```

## Usage (local)
#### Command line:
```python
from pywinos import WinOSClient

tool = WinOSClient(logger_enabled=False)
# tool = WinOSClient(host='', logger_enabled=False)
# tool = WinOSClient(host='localhost', logger_enabled=False)
# tool = WinOSClient(host='127.0.0.1', logger_enabled=False)
response = tool.run_cmd('whoami')

print(response)  # (0, b'mypc\\bobby\r\n', b'')
print(response.exited)  # 0
print(response.stdout)  # my_pc\bobby
print(response.stderr)  # None
print(response.ok)  # True
```

## Helpful methods to work with local Windows OS 
(some method will work on Linux too. But it is necessary to test)

- list_all_methods
- is_host_available
- get_current_os_name
- get_hostname_ip
- search
- get_last_file
- get_absolute_path
- get_md5
- copy
- unzip
- exists
- create_directory
- clean_directory
- timestamp
- ping
- debug_info
- copy
- get_file_size
- get_file_version
- get_last_file_name
- get_local_hostname_ip
- get_md5
- get_process
- get_service
- is_host_available
- is_process_running
- list_dir
- remove
- replace_text
- search
- sort_files

...
