# Isoline Project Guidelines

## Setup & Commands
- Install: `pip install -e .` or `pip install pyglet numpy`
- Run: `python run_isoline.py`
- Test: `pytest` or `pytest tests/test_specific.py -v`
- Lint: `flake8 isoline/` or `ruff check isoline/`
- Type check: `mypy isoline/`

## Code Style
- Follow PEP 8 conventions
- Use type hints for all function parameters and return values
- Import order: stdlib → third-party → local modules
- Docstrings: Use Google style for functions/classes
- Naming: snake_case for functions/variables, CamelCase for classes
- Use explicit exception handling with specific exception types
- Error messages should be descriptive and actionable
- Keep lines under 88 characters
- Add unit tests for new functionality

## Performance Considerations
- Optimize vector operations with NumPy
- Profile performance-critical code paths
- Prefer composition over inheritance