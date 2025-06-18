.PHONY: install install-dev test lint format clean help

# Default target
help:
	@echo "PyCluster Development Commands"
	@echo "=============================="
	@echo "install      - Install PyCluster in development mode"
	@echo "install-dev  - Install PyCluster with development dependencies"
	@echo "test         - Run tests"
	@echo "lint         - Run linting checks"
	@echo "format       - Format code with black"
	@echo "clean        - Clean build artifacts"
	@echo "demo         - Run the basic demo"
	@echo "test-install - Test the installation"

# Install PyCluster in development mode
install:
	pip install -e .

# Install with development dependencies
install-dev:
	pip install -e ".[dev]"

# Run tests
test:
	pytest tests/ -v

# Run linting
lint:
	flake8 pycluster/ --max-line-length=88 --ignore=E203,W503
	mypy pycluster/ --ignore-missing-imports

# Format code
format:
	black pycluster/ examples/ tests/

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Run the basic demo
demo:
	python examples/basic_test.py

# Test installation
test-install:
	python test_installation.py

# Install dependencies
deps:
	pip install -r requirements.txt

# Create distribution
dist: clean
	python setup.py sdist bdist_wheel

# Upload to PyPI (if configured)
upload: dist
	twine upload dist/*

# Show package info
info:
	python -c "import pycluster; print(f'Version: {pycluster.__version__}')" 