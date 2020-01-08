[![PyPI version](https://badge.fury.io/py/pywinos.svg)](https://badge.fury.io/py/pywinos)
[![Build Status](https://travis-ci.org/c-pher/PyWinOS.svg?branch=master)](https://travis-ci.org/c-pher/PyWinOS)
[![Coverage Status](https://coveralls.io/repos/github/c-pher/PyWinOS/badge.svg?branch=master)](https://coveralls.io/github/c-pher/PyWinOS?branch=master)

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
pip install pywinos
```
## Import
```python
from pywinos import WinOSClient
```
---
## Usage (remote server)
#### Run PowerShell:
```python
from pywinos import WinOSClient

tool = WinOSClient(host='172.16.0.126', username='administrator', password='rds123RDS', logger_enabled=True)
response = tool.run_ps(command='$PSVersionTable.PSVersion')

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

#### Run command line:
```python
from pywinos import WinOSClient

tool = WinOSClient('172.16.0.126', 'administrator', 'P@ssw0rd', logger_enabled=False)
response = tool.run_cmd(command='whoami')

print(response)  # <Response code 0, out "b'\r\nMajor  Minor  Buil'", err "b''">
print(response.exited)  # 0
print(response.stdout)  # test-vm1\administrator
print(response.stderr)  # None
print(response.ok)  # True

```

## Usage (local server)
#### Run command line:
```python
from pywinos import WinOSClient

tool = WinOSClient(logger_enabled=False)
# tool = WinOSClient(host='', logger_enabled=False)
# tool = WinOSClient(host='localhost', logger_enabled=False)
# tool = WinOSClient(host='127.0.0.1', logger_enabled=False)
response = tool.run_cmd(command='whoami')

print(response)  # (0, b'mypc\\bobby\r\n', b'')
print(response.exited)  # 0
print(response.stdout)  # my_pc\bobby
print(response.stderr)  # None
print(response.ok)  # True
```

### Helpful predefined methods to work with local Windows OS

* list_all_methods
* is_host_available
* get_current_os_name
* get_hostname_ip
* search
* get_absolute_path
* get_md5
* copy
* unzip
* remove
* exists (can check file existing on remote attached network share too)
* list_dir
* create_directory
* clean_directory
* sort_files (list directory and returns sorted files)
* timestamp
* ping
* get_file_size
* get_file_version
* get_last_file_name
* replace_text (replace text in file)
* get_local_hostname_ip
* get_process
* get_service
* is_process_running
* debug_info (service method to get useful env info)
* ...

## NOTE
Main methods (**run_ps** and **run_cmd**) are OS independent.
But there are some methods works only on Windows. e.g. **get_file_version()** depends on **pywin32** that available on Windows only.

---

## Changelog
##### 1.0.4 (8.01.2020)
- **get_process()** method added. Returns 'psutil.Process' class
- **is_process_running()** refactored.
- **get_process_memory_info()** method added: returns namedtuple. **Full** - optional parameter that work with admin
    rights only. **Else returns brief memory info!**
- **get_process_memory_percent()** method added.
- **get_process_cpu_percent()** method added.
