import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from metasense.toolchain.config_check import load_config, run_checks


class EngineTests(unittest.TestCase):
    def test_load_config_reads_valid_json(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text(json.dumps({"project_name": "MetaSense", "environment": "test"}), encoding="utf-8")
            self.assertEqual(load_config(path)["project_name"], "MetaSense")

    def test_missing_config_raises_clear_error(self):
        with TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "Configuration file not found"):
                load_config(Path(tmp) / "missing.json")

    def test_invalid_json_raises_clear_error(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            path.write_text("{not json", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Invalid JSON"):
                load_config(path)

    def test_report_has_summary_and_status(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            config_path = root / "config.json"
            config_path.write_text(json.dumps({
                "project_name": "MetaSense",
                "environment": "test",
                "directories_to_check": ["src"],
                "optional_directories": []
            }), encoding="utf-8")
            report = run_checks(config_path, root)
            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["summary"]["failed"], 0)
            self.assertGreater(report["summary"]["total_checks"], 0)


if __name__ == "__main__":
    unittest.main()
