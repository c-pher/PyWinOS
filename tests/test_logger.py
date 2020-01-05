import os

from pywinos import Logger


def test_logger():
    """Create logger with file handler. Check file creation"""
    logger = Logger(__file__, file=True)
    print(logger)
    assert 'test_logger.py.log' in os.listdir('tests')
