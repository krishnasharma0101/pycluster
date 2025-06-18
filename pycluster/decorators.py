"""
Decorators for PyCluster remote execution
"""

import functools
import uuid
import asyncio
from typing import Optional, Callable, Any
from .core.host import Host

# Global host instance (will be set when host starts)
_host_instance: Optional[Host] = None

def set_host(host: Host) -> None:
    """Set the global host instance for remote execution"""
    global _host_instance
    _host_instance = host

def get_host() -> Optional[Host]:
    """Get the global host instance"""
    return _host_instance

def remote(computer: Optional[str] = None):
    """
    Decorator to mark a function for remote execution
    
    Args:
        computer: Optional worker ID to target specific worker
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            if _host_instance is None:
                raise RuntimeError("No host instance available. Call set_host() first.")
            
            task_id = f"{func.__name__}_{uuid.uuid4().hex[:8]}"
            return await _host_instance.execute_task(task_id, func, args, kwargs, computer)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            if _host_instance is None:
                raise RuntimeError("No host instance available. Call set_host() first.")
            
            task_id = f"{func.__name__}_{uuid.uuid4().hex[:8]}"
            
            # Simple approach: just call the host's execute_task directly
            # This avoids event loop issues
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    lambda: asyncio.run(
                        _host_instance.execute_task(task_id, func, args, kwargs, computer)
                    )
                )
                return future.result()
        
        # Return async wrapper if function is async, sync wrapper otherwise
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator 