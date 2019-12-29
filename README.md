# PyWinOS
The cross-platform tool to work with remote Windows OS.

PyWinOS uses the Windows Remote Manager (WinRM) service. It can establish connection to a remote server based on Windows OS and execute commands:
- PowerShell
- Command line
- WMI.

For more information on WinRM, please visit [Microsoft’s WinRM site](https://docs.microsoft.com/en-us/windows/win32/winrm/portal?redirectedfrom=MSDN)
It based on [pywinrm](https://pypi.org/project/pywinrm/).

PyWinOS returns object with exit code, sent command, stdout/sdtderr response.

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
## Usage
#### PowerShell:
```python
from pywinos import WinOSClient

tool = WinOSClient('172.16.0.126', 'administrator', 'P@ssw0rd', logger_enabled=True)
response = tool.run_cmd('$PSVersionTable.PSVersion')

print(response)  
# ResponseParser(response=(0, 'Major  Minor  Build  Revision\r\n-----  -----  -----  --------\r\n5      1      17763  592', None, '$PSVersionTable.PSVersion'))
print(response.exited)  # 0
print(response.stdout)
# Major  Minor  Build  Revision
# -----  -----  -----  --------
# 5      1      17763  592
print(response.stderr)  # None
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