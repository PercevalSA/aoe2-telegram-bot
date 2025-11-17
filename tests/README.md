# Testing Guide

## Running Tests

### Install Test Dependencies

```bash
# Using pip
pip install -e ".[test]"

# Or using flit
flit install --extras test
```

### Run All Tests

```bash
# Run all tests with coverage
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_files_id_db.py

# Run specific test function
pytest tests/test_handlers.py::test_get_random_audio
```

### Coverage Reports

```bash
# Generate coverage report
pytest --cov=aoe2_telegram_bot

# Generate HTML coverage report
pytest --cov=aoe2_telegram_bot --cov-report=html
# Open htmlcov/index.html in browser

# Show missing lines
pytest --cov=aoe2_telegram_bot --cov-report=term-missing
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_files_id_db.py      # Cache functionality tests
├── test_handlers.py         # Handler function tests
└── test_folders.py          # Path utility tests
```

## Writing Tests

### Example Test

```python
import pytest
from aoe2_telegram_bot._handlers import get_random_audio

def test_get_random_audio(temp_audio_folder):
    """Test getting random audio file."""
    file_path, file_id = get_random_audio()
    
    assert file_path is not None
    assert file_path.suffix == ".wav"
```

### Available Fixtures

- `temp_audio_folder`: Temporary directory with test audio files
- `mock_update`: Mock Telegram Update object
- `mock_context`: Mock Telegram Context with async methods
- `mock_audio_caption`: Temporary audio caption file
- `clean_cache`: Auto-cleans file ID cache before/after tests

### Async Tests

Use `@pytest.mark.asyncio` for async handlers:

```python
@pytest.mark.asyncio
async def test_send_audio(mock_update, mock_context):
    await send_audio(mock_update, mock_context, audio_file, None)
    mock_context.bot.send_audio.assert_called_once()
```

## Continuous Integration

Tests run automatically on GitHub Actions for:
- Python 3.8, 3.9, 3.10, 3.11, 3.12
- All pull requests
- All commits to main branch

See `.github/workflows/python.yml` for CI configuration.
