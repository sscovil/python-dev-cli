import unittest
from argparse import ArgumentParser, Namespace
from unittest.mock import MagicMock, patch

from src.python_dev_cli.scripts import Scripts
from src.python_dev_cli.cli import build_arg_parser, dev_cli


class TestBuildArgParser(unittest.TestCase):
    def test_build_arg_parser(self):
        config = {
            "tool": {
                "python-dev-cli": {"settings": {"enable_templates": False, "include": ["os"], "script_refs": "foo"}}
            }
        }
        scripts = Scripts.from_config(config)
        scripts["test_key"] = "test_value"
        scripts.get_script_command = MagicMock(return_value="test_command")
        arg_parser = build_arg_parser(scripts)
        self.assertIsInstance(arg_parser, ArgumentParser)
        self.assertEqual(arg_parser.prog, "dev")
        self.assertEqual(arg_parser.parse_args(["test_key"]).script, "test_key")


@patch("src.python_dev_cli.cli.Scripts.from_config")
@patch("src.python_dev_cli.cli.build_arg_parser")
@patch("src.python_dev_cli.cli.sys")
class TestDevCli(unittest.TestCase):
    def test_dev_cli(self, mock_sys, mock_build_arg_parser, mock_from_config):
        mock_sys.argv = ["dev", "test_key"]
        scripts = mock_from_config()
        scripts.run_script = MagicMock()
        mock_build_arg_parser.return_value = MagicMock(parse_args=MagicMock(return_value=Namespace(script="test_key")))
        dev_cli()
        scripts.run_script.assert_called_once_with("test_key")

    def test_dev_cli_no_script(self, mock_sys, mock_build_arg_parser, mock_from_config):
        mock_sys.argv = ["dev"]
        scripts = mock_from_config()
        scripts.run_script = MagicMock()
        mock_build_arg_parser.return_value = MagicMock(
            parse_args=MagicMock(return_value=Namespace(script=None)),
            print_help=MagicMock(),
        )
        dev_cli()
        scripts.run_script.assert_not_called()
        mock_build_arg_parser.return_value.print_help.assert_called_once()


if __name__ == "__main__":
    unittest.main()
