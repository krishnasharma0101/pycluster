"""
Basic tests for PyCluster package
"""

import pytest
import asyncio
from pycluster import Host, Worker, remote, set_host


def test_import():
    """Test that the package can be imported"""
    from pycluster import Host, Worker, remote
    assert Host is not None
    assert Worker is not None
    assert remote is not None


def test_host_creation():
    """Test Host class creation"""
    host = Host(port=8888)
    assert host.port == 8888
    assert host.workers == {}


def test_worker_creation():
    """Test Worker class creation"""
    worker = Worker(
        worker_id="test-worker",
        host="127.0.0.1",
        port=8888,
        otp="TEST123"
    )
    assert worker.worker_id == "test-worker"
    assert worker.host == "127.0.0.1"
    assert worker.port == 8888
    assert worker.otp == "TEST123"


def test_remote_decorator():
    """Test remote decorator"""
    @remote()
    def test_function(x, y):
        return x + y
    
    # The decorator should not change the function signature
    assert test_function.__name__ == "test_function"


@pytest.mark.asyncio
async def test_host_otp_generation():
    """Test that host generates OTP"""
    host = Host(port=8888)
    otp = host.get_otp()
    assert len(otp) == 8
    assert otp.isalnum()


@pytest.mark.asyncio
async def test_set_host():
    """Test set_host function"""
    host = Host(port=8888)
    set_host(host)
    # This should not raise an error
    assert True 