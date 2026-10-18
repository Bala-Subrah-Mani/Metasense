import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from metasense.checks import check_directories, validate_config


class ValidateConfigTests(unittest.TestCase):
    def test_valid_config_has_no_errors(self):
        config = {
            "project_name": "MetaSense",
            "environment": "test",
            "directories_to_check": ["src"],
            "optional_directories": ["logs"],
            "strict_optional_directories": False,
        }
        self.assertEqual(validate_config(config), [])

    def test_non_object_is_rejected(self):
        self.assertIn("Configuration root must be a JSON object.", validate_config([]))

    def test_missing_project_name_is_rejected(self):
        errors = validate_config({"environment": "test"})
        self.assertTrue(any("project_name" in error for error in errors))


class DirectoryCheckTests(unittest.TestCase):
    def test_required_existing_directory_passes(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            config = {"directories_to_check": ["src"], "optional_directories": []}
            result = check_directories(root, config)
            self.assertEqual(result[0]["status"], "pass")

    def test_missing_required_directory_fails(self):
        with TemporaryDirectory() as tmp:
            config = {"directories_to_check": ["missing"], "optional_directories": []}
            result = check_directories(Path(tmp), config)
            self.assertEqual(result[0]["status"], "fail")

    def test_missing_optional_directory_warns_by_default(self):
        with TemporaryDirectory() as tmp:
            config = {"directories_to_check": [], "optional_directories": ["logs"]}
            result = check_directories(Path(tmp), config)
            self.assertEqual(result[0]["status"], "warn")

    def test_strict_optional_directory_fails(self):
        with TemporaryDirectory() as tmp:
            config = {"directories_to_check": [], "optional_directories": ["logs"]}
            result = check_directories(Path(tmp), config, strict=True)
            self.assertEqual(result[0]["status"], "fail")


if __name__ == "__main__":
    unittest.main()
