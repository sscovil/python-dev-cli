import unittest
from unittest.mock import patch, MagicMock

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

    def test_context(self, mock_settings):
        settings = mock_settings()
        key = settings.script_refs
        scripts = Scripts(settings)
        self.assertEqual(scripts._context, {str(key): {}})
        scripts["foo"] = "echo foo"
        self.assertEqual(scripts._context, {str(key): {"foo": "echo foo"}})
        settings.include = ["os"]
        self.assertTrue("os" in scripts._context.keys())

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
            {"key": "text", "value": "echo foo", "expected": ["echo foo"]},
            {"key": "python", "value": "echo {{ 2 + 2 }}", "expected": ["echo 4"]},
            {"key": "list", "value": ["text", "python"], "expected": ["echo foo", "echo 4"]},
            {"key": "getcwd", "value": "echo {{ os.getcwd() }}", "expected": [f"echo {expected_cwd}"]},
            {"key": "getenv", "value": "echo {{ os.getenv('HOME') }}", "expected": [f"echo {expected_home}"]},
            {"key": "uuid", "value": "echo {{ uuid() }}", "expected": [f"echo {expected_uuid}"]},
        ]
        for test in tests:
            with self.subTest(test=test):
                scripts[test["key"]] = test["value"]
                self.assertEqual(scripts.get_script_command(test["key"]), test["expected"])

    def test_get_script_command_invalid_key(self, mock_settings):
        settings = mock_settings()
        scripts = Scripts(settings)
        with self.assertRaises(KeyError):
            scripts.get_script_command("foo")

    def test_get_script_command_templates_disabled(self, mock_settings):
        settings = mock_settings()
        settings.enable_templates = False
        scripts = Scripts(settings)
        scripts["foo"] = "echo {{ 2 + 2 }}"
        self.assertEqual(scripts.get_script_command("foo"), ["echo {{ 2 + 2 }}"])

    def test_get_script_command_no_parse(self, mock_settings):
        settings = mock_settings()
        scripts = Scripts(settings)
        scripts["foo"] = "echo {{ 2 + 2 }}"
        self.assertEqual(scripts.get_script_command("foo", parse=False), ["echo {{ 2 + 2 }}"])

    @patch("uuid.uuid4", autospec=True)
    def test_get_script_command_call_count(self, mock_uuid, mock_settings):
        settings = mock_settings()
        settings.include = ["uuid:uuid4 as uuid"]
        scripts = Scripts(settings)
        scripts["uuid"] = "echo {{ uuid() }}"
        scripts["uuids"] = ["uuid", "uuid", "uuid"]
        mock_uuid.assert_not_called()
        tests = [
            {"script": "uuid", "expected_call_count": 1},
            {"script": "uuids", "expected_call_count": 3},
        ]
        for test in tests:
            with self.subTest(test=test):
                scripts.get_script_command(test["script"])
                self.assertEqual(mock_uuid.call_count, test["expected_call_count"])
                mock_uuid.reset_mock()

    def test_get_script_help(self, mock_settings):
        settings = mock_settings()
        scripts = Scripts(settings)
        scripts["foo"] = "echo {{ 2 + 2 }}"
        scripts.get_script_command = MagicMock()
        tests = [
            {"enable_templates": True, "parse_help": True, "expected": True},
            {"enable_templates": True, "parse_help": False, "expected": False},
            {"enable_templates": False, "parse_help": True, "expected": False},
            {"enable_templates": False, "parse_help": False, "expected": False},
        ]
        for test in tests:
            with self.subTest(test=test):
                settings.enable_templates = test["enable_templates"]
                settings.parse_help = test["parse_help"]
                scripts.get_script_help("foo")
                scripts.get_script_command.assert_called_once_with("foo", parse=test["expected"])
                scripts.get_script_command.reset_mock()

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
