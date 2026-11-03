import os
import tempfile
import unittest
from pathlib import Path

from llm_advisor.cli import _save_output, _slugify


class TestCliOutputSaving(unittest.TestCase):
    def test_slugify(self) -> None:
        self.assertEqual(_slugify("My Demo Name"), "my_demo_name")
        self.assertEqual(_slugify("  GDPR + SOC2 "), "gdpr_soc2")

    def test_save_output_uses_required_pattern(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            current = Path.cwd()
            try:
                os.chdir(td)
                path = _save_output("hello", name="incident advisor", compliance="strict")
                self.assertTrue(path.exists())
                self.assertEqual(path.suffix, ".ms")
                self.assertTrue(path.name.startswith("incident_advisor_strict_"))
                self.assertIn("_strict_", path.name)
            finally:
                os.chdir(current)


if __name__ == "__main__":
    unittest.main()
