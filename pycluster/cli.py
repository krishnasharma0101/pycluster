"""
Command-line interface for PyCluster
"""

import asyncio
import argparse
import sys
import socket
import os
import json
from typing import Optional
from .core.host import Host
from .core.worker import Worker
from .decorators import set_host
from .network import EncryptionManager

def save_encryption_key(key: bytes, key_file: str):
    """Save encryption key to file"""
    key_data = {
        "encryption_key": key.hex()
    }
    with open(key_file, 'w') as f:
        json.dump(key_data, f)

def load_encryption_key(key_file: str) -> bytes:
    """Load encryption key from file"""
    with open(key_file, 'r') as f:
        key_data = json.load(f)
    return bytes.fromhex(key_data["encryption_key"])

async def start_host(args):
    """Start the host dispatcher"""
    if args.key_file and os.path.exists(args.key_file):
        encryption_key = load_encryption_key(args.key_file)
        print(f"Using existing encryption key from {args.key_file}")
    else:
        encryption_key = EncryptionManager.generate_key()
        if args.key_file:
            save_encryption_key(encryption_key, args.key_file)
            print(f"Generated new encryption key and saved to {args.key_file}")
    
    host = Host(port=args.port, encryption_key=encryption_key)
    set_host(host)
    
    print(f"Starting PyCluster host on port {args.port}")
    print(f"One-time password: {host.get_otp()}")
    print(f"Encryption key: {encryption_key.hex()[:16]}...")
    print("Waiting for workers to connect...")
    print("Press Ctrl+C to stop")
    
    try:
        await host.start()
    except KeyboardInterrupt:
        print("\nStopping host...")
        await host.stop()

async def join_worker(args):
    """Join as a worker"""
    if not args.key_file or not os.path.exists(args.key_file):
        print(f"Error: Key file {args.key_file} not found!")
        print("Make sure to start the host with --key-file first.")
        sys.exit(1)
    
    encryption_key = load_encryption_key(args.key_file)
    worker = Worker(
        worker_id=args.worker_id,
        host=args.host,
        port=args.port,
        otp=args.key,
        encryption_key=encryption_key
    )
    
    print(f"Connecting to host {args.host}:{args.port} as worker {args.worker_id}")
    print(f"Using encryption key from {args.key_file}")
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        print("\nDisconnecting worker...")
        await worker.stop()
    except Exception as e:
        print(f"Failed to connect: {e}")
        sys.exit(1)

async def list_workers(args):
    """List connected workers"""
    # This would need to connect to the host to get worker info
    # For now, just show a placeholder
    print("Worker listing functionality requires connection to host")
    print("This feature will be implemented in a future version")

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote address to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "127.0.0.1"

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="PyCluster - Distributed parallel execution across LAN devices",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pycluster host --key-file cluster.key                    # Start host and save key
  pycluster host --port 9999 --key-file cluster.key       # Start host on port 9999
  pycluster join --host 192.168.1.100 --key ABC12345 --key-file cluster.key  # Join as worker
  pycluster list                   # List connected workers
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Host command
    host_parser = subparsers.add_parser("host", help="Start the host dispatcher")
    host_parser.add_argument("--port", type=int, default=8888, help="Port to listen on (default: 8888)")
    host_parser.add_argument("--key-file", default="pycluster.key", help="File to save/load encryption key (default: pycluster.key)")
    
    # Join command
    join_parser = subparsers.add_parser("join", help="Join as a worker")
    join_parser.add_argument("--host", required=True, help="Host IP address")
    join_parser.add_argument("--port", type=int, default=8888, help="Host port (default: 8888)")
    join_parser.add_argument("--key", required=True, help="One-time password from host")
    join_parser.add_argument("--worker-id", default=socket.gethostname(), help="Worker ID (default: hostname)")
    join_parser.add_argument("--key-file", default="pycluster.key", help="File to load encryption key from (default: pycluster.key)")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List connected workers")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "host":
            asyncio.run(start_host(args))
        elif args.command == "join":
            asyncio.run(join_worker(args))
        elif args.command == "list":
            asyncio.run(list_workers(args))
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 