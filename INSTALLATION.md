# PyCluster Installation Guide

This guide covers all the different ways to install PyCluster and how to verify the installation.

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Git (for GitHub installation)

## 🚀 Installation Methods

### Method 1: Install from GitHub (Recommended)

This is the easiest way to get the latest version of PyCluster:

```bash
# Basic installation
pip install git+https://github.com/pycluster/pycluster.git

# Installation with development dependencies
pip install git+https://github.com/pycluster/pycluster.git#egg=pycluster[dev]
```

**Advantages:**
- Always gets the latest version
- No need to clone the repository
- Automatic dependency resolution

### Method 2: Clone and Install Locally

If you want to modify the code or contribute:

```bash
# Clone the repository
git clone https://github.com/pycluster/pycluster.git
cd pycluster

# Install in development mode
pip install -e .

# Or install with all dependencies
pip install -r requirements.txt
pip install -e .
```

**Advantages:**
- Can modify the source code
- Easy to contribute
- Can run tests locally

### Method 3: Install from PyPI (Coming Soon)

Once PyCluster is published to PyPI:

```bash
pip install pycluster
```

## ✅ Verification

After installation, verify that everything works:

### 1. Test Import

```bash
python -c "import pycluster; print('✅ PyCluster imported successfully!')"
```

### 2. Test CLI

```bash
python -m pycluster.cli --help
```

### 3. Run Installation Test

```bash
# If you cloned the repository
python test_installation.py

# Or run a simple test
python -c "
from pycluster import Host, Worker, remote
host = Host(port=8888)
print('✅ All components working!')
"
```

## 🔧 Development Setup

For developers who want to contribute:

```bash
# Clone the repository
git clone https://github.com/pycluster/pycluster.git
cd pycluster

# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8 pycluster/
black --check pycluster/

# Run type checking
mypy pycluster/
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem:** `ModuleNotFoundError: No module named 'pycluster'`

**Solution:**
```bash
# Reinstall the package
pip uninstall pycluster
pip install git+https://github.com/pycluster/pycluster.git
```

#### 2. CLI Not Found

**Problem:** `pycluster: command not found`

**Solution:**
```bash
# Use Python module syntax
python -m pycluster.cli --help

# Or add Scripts directory to PATH (Windows)
# Add C:\Users\<username>\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\Scripts to PATH
```

#### 3. Dependency Conflicts

**Problem:** Version conflicts with other packages

**Solution:**
```bash
# Create a virtual environment
python -m venv pycluster-env
source pycluster-env/bin/activate  # On Windows: pycluster-env\Scripts\activate
pip install git+https://github.com/pycluster/pycluster.git
```

#### 4. Permission Errors

**Problem:** Permission denied when installing

**Solution:**
```bash
# Use user installation
pip install --user git+https://github.com/pycluster/pycluster.git

# Or use virtual environment
python -m venv pycluster-env
source pycluster-env/bin/activate
pip install git+https://github.com/pycluster/pycluster.git
```

### Platform-Specific Issues

#### Windows

- **PATH Issues:** The CLI script might not be in PATH. Use `python -m pycluster.cli` instead.
- **Firewall:** Windows Firewall might block connections. Allow Python through the firewall.

#### macOS

- **Permission Issues:** Use `pip install --user` or virtual environments.
- **Homebrew Python:** Make sure you're using the correct Python version.

#### Linux

- **Package Manager Conflicts:** Use virtual environments to avoid conflicts with system packages.
- **Firewall:** Check if ufw or iptables is blocking connections.

## 📦 Package Contents

After installation, you'll have access to:

- **Core Classes:** `Host`, `Worker`
- **Decorators:** `@remote()`
- **CLI Tool:** `pycluster` command
- **Network Utilities:** Encryption, file transfer, socket management
- **Helper Functions:** OTP generation, port checking, etc.

## 🔄 Updating

To update to the latest version:

```bash
# If installed from GitHub
pip install --upgrade git+https://github.com/pycluster/pycluster.git

# If installed locally
cd pycluster
git pull
pip install -e .
```

## 🧪 Testing Your Installation

Create a simple test script:

```python
#!/usr/bin/env python3
"""Test PyCluster installation"""

import asyncio
from pycluster import Host, Worker, remote, set_host

@remote()
def add_numbers(a, b):
    return a + b

async def test():
    # Create host
    host = Host(port=8888)
    set_host(host)
    
    # Test OTP generation
    otp = host.get_otp()
    print(f"Generated OTP: {otp}")
    
    # Test remote function (will fail without workers, but import should work)
    try:
        result = await add_numbers(5, 10)
        print(f"Remote function result: {result}")
    except Exception as e:
        print(f"Remote function test (expected to fail without workers): {e}")
    
    print("✅ Installation test completed!")

if __name__ == "__main__":
    asyncio.run(test())
```

Run it with:
```bash
python test_script.py
```

## 📞 Getting Help

If you encounter issues:

1. Check the [troubleshooting section](#-troubleshooting) above
2. Search [GitHub Issues](https://github.com/pycluster/pycluster/issues)
3. Create a new issue with:
   - Your operating system
   - Python version (`python --version`)
   - Installation method used
   - Full error message
   - Steps to reproduce

## 🎯 Next Steps

After successful installation:

1. Read the [Quick Start Guide](../README.md#quick-start)
2. Check out the [examples](../examples/) directory
3. Try the [basic test](../examples/basic_test.py)
4. Explore the [API documentation](../README.md#api-reference) 