import unittest

from src.python_dev_cli.settings import Settings


class TestSettings(unittest.TestCase):
    def test_init(self):
        settings = Settings()
        self.assertTrue(settings.enable_templates)
        self.assertEqual(settings.include, [])
        self.assertEqual(settings.script_refs, "dev")

    def test_init_with_kwargs(self):
        settings = Settings(enable_templates=False, include=["os"], script_refs="foo")
        self.assertFalse(settings.enable_templates)
        self.assertEqual(settings.include, ["os"])
        self.assertEqual(settings.script_refs, "foo")

    def test_from_config(self):
        config = {
            "tool": {
                "python-dev-cli": {"settings": {"enable_templates": False, "include": ["os"], "script_refs": "foo"}}
            }
        }
        settings = Settings.from_config(config)
        self.assertFalse(settings.enable_templates)
        self.assertEqual(settings.include, ["os"])
        self.assertEqual(settings.script_refs, "foo")

    def test_set_enable_templates(self):
        settings = Settings()
        settings.enable_templates = False
        self.assertFalse(settings.enable_templates)

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
