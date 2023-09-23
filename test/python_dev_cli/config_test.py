import unittest
from pathlib import Path
from unittest.mock import patch

from src.python_dev_cli.config import get_pyproject_toml, get_project_root

project_root = Path(__file__).parent.parent.parent


class TestConfig(unittest.TestCase):
    def test_get_project_root(self):
        self.assertEqual(get_project_root(), project_root)

    @patch("src.python_dev_cli.config.tomllib.load", autospec=True)
    def test_get_pyproject_toml(self, mock_load):
        expected = {"foo": "bar"}
        mock_load.return_value = expected
        actual = get_pyproject_toml()
        self.assertEqual(actual, expected)
        mock_load.assert_called_once()


if __name__ == "__main__":
    unittest.main()
