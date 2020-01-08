from os import path, name

from setuptools import setup

INSTALL_REQUIRES = [
    'pywinrm>=0.4.1',
    'requests-credssp>=1.1.1',
    'requests>=2.22.0',
    'psutil'
]

if name == 'nt':
    INSTALL_REQUIRES.append('pywin32')

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pywinos',
    version='1.0.4',
    packages=['pywinos'],
    url='https://github.com/c-pher/PyWinOS.git',
    license='MIT',
    author='Andrey Komissarov',
    author_email='a.komisssarov@gmail.com',
    description='The cross-platform tool to execute PowerShell '
                'and command line remotely and locally.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Topic :: System :: Systems Administration',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    install_requires=INSTALL_REQUIRES,
    python_requires='>=3.7',
)
