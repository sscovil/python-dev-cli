import unittest

from src.python_dev_cli.settings import Settings

cast_to_bool_tests = [
    {"value": True, "expected": True},
    {"value": False, "expected": False},
    {"value": 1, "expected": True},
    {"value": 0, "expected": False},
    {"value": -1, "expected": True},
    {"value": "true", "expected": True},
    {"value": "false", "expected": False},
    {"value": "1", "expected": True},
    {"value": "0", "expected": False},
    {"value": "yes", "expected": True},
    {"value": "no", "expected": False},
    {"value": "", "expected": False},
    {"value": "any other string", "expected": True},
    {"value": [], "expected": False},
    {"value": {}, "expected": False},
    {"value": (), "expected": False},
    {"value": None, "expected": False},
]


class TestSettings(unittest.TestCase):
    def test_init(self):
        settings = Settings()
        self.assertTrue(settings.enable_templates)
        self.assertTrue(settings.parse_help)
        self.assertEqual(settings.include, [])
        self.assertEqual(settings.script_refs, "dev")

    def test_init_with_kwargs(self):
        settings = Settings(enable_templates=False, parse_help=False, include=["os"], script_refs="foo")
        self.assertFalse(settings.enable_templates)
        self.assertFalse(settings.parse_help)
        self.assertEqual(settings.include, ["os"])
        self.assertEqual(settings.script_refs, "foo")

    def test_from_config(self):
        config = {
            "tool": {
                "python-dev-cli": {
                    "settings": {
                        "enable_templates": False,
                        "parse_help": False,
                        "include": ["os"],
                        "script_refs": "foo",
                    }
                }
            }
        }
        settings = Settings.from_config(config)
        self.assertFalse(settings.enable_templates)
        self.assertFalse(settings.parse_help)
        self.assertEqual(settings.include, ["os"])
        self.assertEqual(settings.script_refs, "foo")

    def test_set_enable_templates(self):
        settings = Settings()
        for test in cast_to_bool_tests:
            with self.subTest(test=test):
                settings.enable_templates = test["value"]
                self.assertEqual(settings.enable_templates, test["expected"])

    def test_set_parse_help(self):
        settings = Settings()
        for test in cast_to_bool_tests:
            with self.subTest(test=test):
                settings.parse_help = test["value"]
                self.assertEqual(settings.parse_help, test["expected"])

    def test_set_include(self):
        settings = Settings()
        settings.include = ["os"]
        self.assertEqual(settings.include, ["os"])

    def test_set_script_refs(self):
        settings = Settings()
        settings.script_refs = "foo"
        self.assertEqual(settings.script_refs, "foo")


if __name__ == "__main__":
    unittest.main()
