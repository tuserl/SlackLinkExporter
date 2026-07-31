import json
import tempfile
import unittest
from pathlib import Path

from extract_urls import extract_image_urls, export_urls


class TestExtractURLs(unittest.TestCase):

    def test_extract_unique_urls(self):
        data = {
            "files": [
                {
                    "url_private": "https://a.com/image1.jpg",
                    "url_private_download": "https://a.com/image1.jpg",
                },
                {
                    "url_private": "https://a.com/image2.jpg",
                },
            ]
        }

        with tempfile.TemporaryDirectory() as d:
            json_path = Path(d) / "test.json"

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f)

            urls = extract_image_urls(json_path)

            self.assertEqual(
                urls,
                {
                    "https://a.com/image1.jpg",
                    "https://a.com/image2.jpg",
                },
            )

    def test_export(self):
        data = {
            "files": [
                {
                    "url_private_download": "https://a.com/abc.jpg"
                }
            ]
        }


        with tempfile.TemporaryDirectory() as d:
            json_path = Path(d) / "sample.json"
            output = Path(d) / "output.txt"

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f)

            count = export_urls(json_path, output)

            self.assertEqual(count, 1)
            self.assertTrue(output.exists())
            self.assertIn("https://a.com/abc.jpg", output.read_text())

    def test_extract_directory_recursively(self):
        data1 = {"files": [{"url_private": "https://a.com/image1.jpg"}]}
        data2 = {"files": [{"url_private": "https://a.com/image2.jpg"}]}

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sub = root / "sub"
            sub.mkdir()

            (root / "1.json").write_text(json.dumps(data1))
            (sub / "2.json").write_text(json.dumps(data2))

            urls = extract_image_urls(root)
            self.assertEqual(urls, {"https://a.com/image1.jpg", "https://a.com/image2.jpg"})

            output = root / "output.txt"
            count = export_urls(root, output)
            self.assertEqual(count, 2)
            self.assertTrue(output.exists())

            # Check subfolder output.txt
            sub_output = sub / "output.txt"
            self.assertTrue(sub_output.exists())
            self.assertEqual(sub_output.read_text().strip(), "https://a.com/image2.jpg")



if __name__ == "__main__":
    unittest.main()

