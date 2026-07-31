import tempfile
import unittest
from pathlib import Path

from scanner import find_json_files


class TestScanner(unittest.TestCase):

    def test_recursive_scan(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)

            (root / "a.json").write_text("{}")
            (root / "b.txt").write_text("")
            (root / "sub").mkdir()
            (root / "sub" / "c.json").write_text("{}")

            result = find_json_files(root)

            self.assertEqual(len(result), 2)
            self.assertTrue(any(f.name == "a.json" for f in result))
            self.assertTrue(any(f.name == "c.json" for f in result))


if __name__ == "__main__":
    unittest.main()
