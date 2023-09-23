import unittest
from unittest.mock import patch

from src.python_dev_cli.scripts import Scripts


@patch("src.python_dev_cli.settings.Settings", autospec=True)
class TestScripts(unittest.TestCase):
    def test_init(self, mock_settings):
        settings = mock_settings()
        scripts = Scripts(settings, foo="echo foo", bar="echo bar", baz=["foo", "bar"])
        self.assertEqual(scripts["foo"], "echo foo")
        self.assertEqual(scripts["bar"], "echo bar")
        self.assertEqual(scripts["baz"], ["foo", "bar"])

    def test_init_invalid_script(self, mock_settings):
        settings = mock_settings()
        with self.assertRaises(TypeError):
            Scripts(settings, foo=1)

    def test_setitem(self, mock_settings):
        settings = mock_settings()
        scripts = Scripts(settings)
        scripts["foo"] = "echo foo"
        self.assertEqual(scripts["foo"], "echo foo")

    def test_setitem_invalid_key(self, mock_settings):
        settings = mock_settings()
        scripts = Scripts(settings)
        with self.assertRaises(TypeError):
            scripts[1] = "echo foo"

    def test_setitem_invalid_value(self, mock_settings):
        settings = mock_settings()
        scripts = Scripts(settings)
        with self.assertRaises(TypeError):
            scripts["foo"] = 1

    def test_contains(self, mock_settings):
        settings = mock_settings()
        scripts = Scripts(settings)
        scripts["foo"] = "echo foo"
        self.assertIn("foo", scripts)
        self.assertNotIn("bar", scripts)

    def test_is_iterable(self, mock_settings):
        settings = mock_settings()
        scripts = Scripts(settings)
        scripts["foo"] = "echo foo"
        scripts["bar"] = "echo bar"
        self.assertEqual(list(scripts), ["foo", "bar"])

    def test_has_length(self, mock_settings):
        settings = mock_settings()
        scripts = Scripts(settings)
        scripts["foo"] = "echo foo"
        scripts["bar"] = "echo bar"
        self.assertEqual(len(scripts), 2)
        scripts["baz"] = ["foo", "bar"]
        self.assertEqual(len(scripts), 3)

    @patch("src.python_dev_cli.settings.Settings.from_config", autospec=True)
    def test_from_config(self, mock_settings_from_config, mock_settings):
        mock_settings_from_config.return_value = mock_settings()
        config = {"tool": {"python-dev-cli": {"scripts": {"foo": "echo foo", "bar": "echo bar"}}}}
        scripts = Scripts.from_config(config)
        mock_settings_from_config.assert_called_once_with(config)
        self.assertEqual(scripts["foo"], "echo foo")
        self.assertEqual(scripts["bar"], "echo bar")

    @patch("src.python_dev_cli.settings.Settings.from_config", autospec=True)
    def test_from_config_invalid_config(self, mock_settings_from_config, mock_settings):
        mock_settings_from_config.return_value = mock_settings()
        config = {"tool": {"python-dev-cli": {"scripts": {"foo": 1}}}}
        with self.assertRaises(TypeError):
            Scripts.from_config(config)

    @patch("uuid.uuid4", autospec=True)
    @patch("os.getenv", autospec=True)
    @patch("os.getcwd", autospec=True)
    def test_get_script_command(self, mock_getcwd, mock_getenv, mock_uuid, mock_settings):
        expected_cwd = "/path/to/current/working/directory"
        expected_home = "/home/user"
        expected_uuid = "12345678-1234-5678-1234-567812345678"
        mock_getcwd.return_value = expected_cwd
        mock_getenv.return_value = expected_home
        mock_uuid.return_value = expected_uuid
        settings = mock_settings()
        settings.include = ["os", "os:getenv", "uuid:uuid4 as uuid"]
        scripts = Scripts(settings)
        tests = [
            ("text", "echo foo", ["echo foo"]),
            ("python", "echo {{ 2 + 2 }}", ["echo 4"]),
            ("list", ["text", "python"], ["echo foo", "echo 4"]),
            ("getcwd", "echo {{ os.getcwd() }}", [f"echo {expected_cwd}"]),
            ("getenv", "echo {{ os.getenv('HOME') }}", [f"echo {expected_home}"]),
            ("uuid", "echo {{ uuid() }}", [f"echo {expected_uuid}"]),
        ]
        for key, value, expected in tests:
            with self.subTest(key=key, value=value, expected=expected):
                scripts[key] = value
                self.assertEqual(scripts.get_script_command(key), expected)

    def test_get_script_command_invalid_key(self, mock_settings):
        settings = mock_settings()
        scripts = Scripts(settings)
        with self.assertRaises(KeyError):
            scripts.get_script_command("foo")

    @patch("uuid.uuid4", autospec=True)
    @patch("os.getenv", autospec=True)
    @patch("os.getcwd", autospec=True)
    def test_run_script(self, mock_getcwd, mock_getenv, mock_uuid, mock_settings):
        expected_cwd = "/path/to/current/working/directory"
        expected_home = "/home/user"
        expected_uuid = "12345678-1234-5678-1234-567812345678"
        mock_getcwd.return_value = expected_cwd
        mock_getenv.return_value = expected_home
        mock_uuid.return_value = expected_uuid
        settings = mock_settings()
        settings.include = ["os", "os:getenv", "uuid:uuid4 as uuid"]
        scripts = Scripts(settings)
        tests = [
            ("text", "echo foo", ["foo"]),
            ("python", "echo {{ 2 + 2 }}", ["4"]),
            ("list", ["text", "python"], ["foo", "4"]),
            ("getcwd", "echo {{ os.getcwd() }}", [expected_cwd]),
            ("getenv", "echo {{ os.getenv('HOME') }}", [expected_home]),
            ("uuid", "echo {{ uuid() }}", [expected_uuid]),
        ]
        for key, value, expected in tests:
            with self.subTest(key=key, value=value, expected=expected):
                scripts[key] = value
                result = scripts.run_script(key, capture_output=True, check=False)
                for i, res in enumerate(result):
                    self.assertEqual(res.stdout.decode().strip(), expected[i])

    def test_run_script_invalid_key(self, mock_settings):
        settings = mock_settings()
        scripts = Scripts(settings)
        with self.assertRaises(KeyError):
            scripts.run_script("foo")


if __name__ == "__main__":
    unittest.main()
