"""
Shared pytest fixtures and configuration for all tests.
"""
import json
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, Generator
from unittest.mock import Mock, MagicMock

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def temp_file(temp_dir: Path) -> Generator[Path, None, None]:
    """Create a temporary file in the temp directory."""
    temp_file = temp_dir / "test_file.txt"
    temp_file.write_text("test content")
    yield temp_file
    if temp_file.exists():
        temp_file.unlink()


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Provide a mock configuration dictionary."""
    return {
        "debug": True,
        "version": "1.0.0",
        "settings": {
            "max_retries": 3,
            "timeout": 30,
            "batch_size": 100,
        },
        "paths": {
            "data": "/tmp/data",
            "logs": "/tmp/logs",
            "cache": "/tmp/cache",
        }
    }


@pytest.fixture
def mock_json_file(temp_dir: Path, mock_config: Dict[str, Any]) -> Path:
    """Create a temporary JSON file with mock configuration."""
    json_file = temp_dir / "config.json"
    with open(json_file, 'w') as f:
        json.dump(mock_config, f, indent=2)
    return json_file


@pytest.fixture
def mock_logger() -> Mock:
    """Provide a mock logger object."""
    logger = Mock()
    logger.debug = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.critical = Mock()
    return logger


@pytest.fixture
def mock_blender_context() -> Mock:
    """Mock Blender context object for add-on testing."""
    context = Mock()
    context.scene = Mock()
    context.object = Mock()
    context.selected_objects = []
    context.view_layer = Mock()
    context.window_manager = Mock()
    return context


@pytest.fixture
def mock_blender_operator() -> Mock:
    """Mock Blender operator for add-on testing."""
    operator = Mock()
    operator.report = Mock()
    operator.bl_idname = "test.operator"
    operator.bl_label = "Test Operator"
    return operator


@pytest.fixture
def sample_mediapipe_data() -> Dict[str, Any]:
    """Sample MediaPipe pose detection data."""
    return {
        "landmarks": [
            {"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 1.0},
            {"x": 0.6, "y": 0.4, "z": 0.1, "visibility": 0.9},
            {"x": 0.4, "y": 0.6, "z": -0.1, "visibility": 0.8},
        ],
        "world_landmarks": [
            {"x": 0.0, "y": 0.0, "z": 0.0, "visibility": 1.0},
            {"x": 0.1, "y": -0.1, "z": 0.1, "visibility": 0.9},
            {"x": -0.1, "y": 0.1, "z": -0.1, "visibility": 0.8},
        ],
        "timestamp": 0.0,
    }


@pytest.fixture
def mock_opencv_image() -> MagicMock:
    """Mock OpenCV image array."""
    import numpy as np
    
    # Create a mock that behaves like a numpy array
    mock_img = MagicMock(spec=np.ndarray)
    mock_img.shape = (480, 640, 3)  # Height, Width, Channels
    mock_img.dtype = np.uint8
    return mock_img


@pytest.fixture
def cleanup_files(request) -> Generator[list, None, None]:
    """Fixture to track and cleanup files created during tests."""
    files_to_cleanup = []
    
    def add_file(filepath: Path):
        files_to_cleanup.append(filepath)
    
    # Make the add_file function available to tests
    request.node.add_cleanup_file = add_file
    
    yield files_to_cleanup
    
    # Cleanup
    for filepath in files_to_cleanup:
        if filepath.exists():
            if filepath.is_dir():
                shutil.rmtree(filepath)
            else:
                filepath.unlink()


@pytest.fixture(autouse=True)
def reset_test_environment():
    """Automatically reset test environment before each test."""
    # This fixture runs before each test automatically
    # Add any global test environment setup/teardown here
    yield
    # Cleanup code runs after each test


@pytest.fixture
def capture_stdout(monkeypatch):
    """Capture stdout for testing print statements."""
    import io
    import sys
    
    captured_output = io.StringIO()
    monkeypatch.setattr(sys, 'stdout', captured_output)
    return captured_output


# Markers for different test types
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Skip tests that require Blender when not in Blender environment
def pytest_collection_modifyitems(config, items):
    """Skip tests that require Blender when not running in Blender."""
    try:
        import bpy
        has_blender = True
    except ImportError:
        has_blender = False
    
    if not has_blender:
        skip_blender = pytest.mark.skip(reason="requires Blender environment")
        for item in items:
            if "blender" in item.keywords or "bpy" in str(item.fspath):
                item.add_marker(skip_blender)