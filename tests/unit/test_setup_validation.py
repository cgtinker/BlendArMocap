"""
Validation tests to ensure the testing infrastructure is properly set up.
"""
import json
from pathlib import Path
from unittest.mock import Mock

import pytest


class TestSetupValidation:
    """Validate that the testing infrastructure is correctly configured."""
    
    @pytest.mark.unit
    def test_pytest_is_importable(self):
        """Verify pytest can be imported."""
        import pytest
        assert pytest is not None
        assert hasattr(pytest, 'main')
    
    @pytest.mark.unit
    def test_coverage_is_configured(self):
        """Verify pytest-cov is available and configured."""
        import pytest_cov
        assert pytest_cov is not None
    
    @pytest.mark.unit
    def test_pytest_mock_is_available(self):
        """Verify pytest-mock is available."""
        import pytest_mock
        assert pytest_mock is not None
    
    @pytest.mark.unit
    def test_temp_dir_fixture_works(self, temp_dir):
        """Test that temp_dir fixture creates and cleans up properly."""
        assert temp_dir.exists()
        assert temp_dir.is_dir()
        
        # Create a test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        assert test_file.exists()
    
    @pytest.mark.unit
    def test_temp_file_fixture_works(self, temp_file):
        """Test that temp_file fixture creates a file with content."""
        assert temp_file.exists()
        assert temp_file.is_file()
        assert temp_file.read_text() == "test content"
    
    @pytest.mark.unit
    def test_mock_config_fixture_provides_config(self, mock_config):
        """Test that mock_config fixture provides expected structure."""
        assert isinstance(mock_config, dict)
        assert "debug" in mock_config
        assert "version" in mock_config
        assert "settings" in mock_config
        assert mock_config["settings"]["max_retries"] == 3
    
    @pytest.mark.unit
    def test_mock_json_file_fixture_creates_json(self, mock_json_file):
        """Test that mock_json_file fixture creates valid JSON file."""
        assert mock_json_file.exists()
        
        with open(mock_json_file, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, dict)
        assert "debug" in data
        assert data["debug"] is True
    
    @pytest.mark.unit
    def test_mock_logger_fixture_has_methods(self, mock_logger):
        """Test that mock_logger fixture provides logging methods."""
        assert isinstance(mock_logger, Mock)
        assert hasattr(mock_logger, 'debug')
        assert hasattr(mock_logger, 'info')
        assert hasattr(mock_logger, 'warning')
        assert hasattr(mock_logger, 'error')
        
        # Test that methods can be called
        mock_logger.info("test message")
        mock_logger.info.assert_called_once_with("test message")
    
    @pytest.mark.unit
    def test_project_structure_exists(self):
        """Verify the expected project structure is in place."""
        workspace = Path("/workspace")
        
        # Check main directories
        assert (workspace / "src").exists()
        assert (workspace / "tests").exists()
        assert (workspace / "tests" / "unit").exists()
        assert (workspace / "tests" / "integration").exists()
        
        # Check configuration files
        assert (workspace / "pyproject.toml").exists()
        assert (workspace / "requirements.txt").exists()
    
    @pytest.mark.unit
    def test_markers_are_registered(self, request):
        """Test that custom pytest markers are registered."""
        # Get list of registered markers from the pytest configuration
        config_markers = request.config.getini('markers')
        marker_names = [m.split(':')[0].strip() for m in config_markers]
        assert "unit" in marker_names
        assert "integration" in marker_names
        assert "slow" in marker_names
    
    @pytest.mark.unit
    @pytest.mark.parametrize("fixture_name", [
        "temp_dir",
        "temp_file",
        "mock_config",
        "mock_json_file",
        "mock_logger",
        "mock_blender_context",
        "mock_blender_operator",
        "sample_mediapipe_data",
        "mock_opencv_image",
        "cleanup_files",
        "capture_stdout",
    ])
    def test_fixture_is_available(self, request, fixture_name):
        """Test that all expected fixtures are available."""
        # Fixtures are available through the request.getfixturevalue method
        try:
            request.getfixturevalue(fixture_name)
            assert True
        except pytest.FixtureLookupError:
            pytest.fail(f"Fixture '{fixture_name}' is not available")
    
    @pytest.mark.unit
    def test_coverage_configuration_exists(self):
        """Verify coverage configuration is present in pyproject.toml."""
        pyproject_path = Path("/workspace/pyproject.toml")
        assert pyproject_path.exists()
        
        content = pyproject_path.read_text()
        assert "[tool.coverage.run]" in content
        assert "[tool.coverage.report]" in content
        assert "source = [\"src\"]" in content
        assert "fail_under = 0" in content
    
    @pytest.mark.unit
    def test_pytest_configuration_exists(self):
        """Verify pytest configuration is present in pyproject.toml."""
        pyproject_path = Path("/workspace/pyproject.toml")
        content = pyproject_path.read_text()
        
        assert "[tool.pytest.ini_options]" in content
        assert "testpaths = [\"tests\"]" in content
        assert "--cov=src" in content
        assert "--cov-fail-under=0" in content


class TestCommandValidation:
    """Validate that Poetry scripts are properly configured."""
    
    @pytest.mark.unit
    def test_poetry_scripts_configured(self):
        """Verify that 'poetry run test' and 'poetry run tests' are configured."""
        pyproject_path = Path("/workspace/pyproject.toml")
        content = pyproject_path.read_text()
        
        assert "[tool.poetry.scripts]" in content
        assert 'test = "pytest:main"' in content
        assert 'tests = "pytest:main"' in content


@pytest.mark.integration
class TestIntegrationSetup:
    """Integration tests for the testing setup."""
    
    def test_import_project_modules(self):
        """Test that project modules can be imported."""
        # This will only work after poetry install
        try:
            import src
            assert src is not None
        except ImportError:
            pytest.skip("Project not yet installed with Poetry")
    
    def test_blender_fixture_skip_works(self, mock_blender_context):
        """Test that Blender-related fixtures work but tests skip when not in Blender."""
        # This test should pass even outside Blender environment
        assert mock_blender_context is not None
        assert hasattr(mock_blender_context, 'scene')