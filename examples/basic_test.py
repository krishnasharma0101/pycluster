"""
Basic PyCluster demo script

This script demonstrates:
1. Starting a host
2. Connecting a worker
3. Running a remote function
4. Getting results back
"""

import asyncio
import time
import sys
import os

# Add the parent directory to the path so we can import pycluster
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pycluster import Host, Worker, remote, set_host

# Example function that will run on a remote worker
def calculate_fibonacci(n):
    """Calculate the nth Fibonacci number"""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

def heavy_computation(data):
    """Simulate a heavy computation"""
    result = 0
    for i in range(data):
        result += i ** 2
    return result

@remote()
def remote_function(x, y):
    """A function that will run on a remote worker"""
    print(f"Running on remote worker with x={x}, y={y}")
    time.sleep(2)  # Simulate some work
    return x * y + 42

async def demo():
    """Run the PyCluster demo"""
    print("🚀 PyCluster Basic Demo")
    print("=" * 50)
    
    # Start the host
    print("\n1. Starting host...")
    host = Host(port=8888)
    set_host(host)
    
    # Start host in background
    host_task = asyncio.create_task(host.start())
    
    # Wait a moment for host to start
    await asyncio.sleep(1)
    
    print(f"   Host started on port 8888")
    print(f"   OTP: {host.get_otp()}")
    
    # Start a worker
    print("\n2. Starting worker...")
    worker = Worker(
        worker_id="demo-worker",
        host="127.0.0.1",
        port=8888,
        otp=host.get_otp()
    )
    
    # Start worker in background
    worker_task = asyncio.create_task(worker.start())
    
    # Wait for worker to connect
    await asyncio.sleep(2)
    
    print("   Worker connected successfully")
    
    # Test remote execution
    print("\n3. Testing remote execution...")
    
    # Test simple function
    print("   Testing fibonacci calculation...")
    result1 = await host.execute_task(
        "fib_task",
        calculate_fibonacci,
        (10,),
        {}
    )
    print(f"   Fibonacci(10) = {result1}")
    
    # Test heavy computation
    print("   Testing heavy computation...")
    result2 = await host.execute_task(
        "heavy_task",
        heavy_computation,
        (1000,),
        {}
    )
    print(f"   Heavy computation result: {result2}")
    
    # Test decorated function
    print("   Testing decorated function...")
    result3 = await remote_function(5, 10)
    print(f"   Remote function result: {result3}")
    
    print("\n✅ Demo completed successfully!")
    
    # Cleanup
    print("\n4. Cleaning up...")
    host_task.cancel()
    worker_task.cancel()
    
    try:
        await host_task
    except asyncio.CancelledError:
        pass
    
    try:
        await worker_task
    except asyncio.CancelledError:
        pass
    
    print("   Cleanup completed")

def main():
    """Main entry point"""
    try:
        asyncio.run(demo())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 