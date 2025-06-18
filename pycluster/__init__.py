"""
PyCluster - Distributed parallel execution across LAN devices
"""

__version__ = "0.1.0"
__author__ = "PyCluster Team"

from .core.host import Host
from .core.worker import Worker
from .decorators import remote, set_host
from .config import Config

__all__ = ["Host", "Worker", "remote", "set_host", "Config"] 