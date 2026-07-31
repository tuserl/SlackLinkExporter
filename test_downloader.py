import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from downloader import (
    download_all_in_directory,
    download_file,
    download_urls_from_file,
    get_filename_from_url,
)


class TestDownloader(unittest.TestCase):

    def test_get_filename_from_url(self):
        url = "https://files.slack.com/files-pri/T123-F456/sample_image.png?t=123"
        filename = get_filename_from_url(url)
        self.assertEqual(filename, "sample_image.png")

    def test_get_filename_fallback_and_sanitize(self):
        url = "https://example.com/"
        filename = get_filename_from_url(url)
        self.assertTrue(filename.startswith("file_"))

        url_unsafe = "https://example.com/bad:file?.jpg"
        filename_unsafe = get_filename_from_url(url_unsafe)
        self.assertNotIn(":", filename_unsafe)
        self.assertNotIn("?", filename_unsafe)


    @patch("urllib.request.urlopen")
    def test_download_file(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b"fake image bytes"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        with tempfile.TemporaryDirectory() as d:
            output_dir = Path(d)
            url = "https://a.com/photo.jpg"

            result = download_file(url, output_dir, token="test_token")

            self.assertIsNotNone(result)
            self.assertEqual(result.name, "photo.jpg")
            self.assertTrue(result.exists())
            self.assertEqual(result.read_bytes(), b"fake image bytes")

            # Verify Request headers
            req = mock_urlopen.call_args[0][0]
            self.assertEqual(req.headers.get("Authorization"), "Bearer test_token")

    @patch("urllib.request.urlopen")
    def test_skip_html_response(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.headers.get.return_value = "text/html; charset=utf-8"
        mock_response.read.return_value = b"<!DOCTYPE html><html><body>Sign In</body></html>"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        with tempfile.TemporaryDirectory() as d:
            output_dir = Path(d)
            url = "https://a.com/page.jpg"

            result = download_file(url, output_dir)
            self.assertIsNone(result)
            self.assertFalse((output_dir / "page.jpg").exists())


    @patch("downloader.download_file")
    def test_download_urls_from_file(self, mock_download_file):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            output_file = root / "output.txt"
            output_file.write_text("https://a.com/1.jpg\nhttps://a.com/2.jpg\n")

            mock_download_file.side_effect = [
                root / "1.jpg",
                root / "2.jpg",
            ]

            results = download_urls_from_file(output_file, token="tok")

            self.assertEqual(len(results), 2)
            self.assertEqual(mock_download_file.call_count, 2)

    @patch("downloader.download_urls_from_file")
    def test_download_all_in_directory(self, mock_download_urls):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sub1 = root / "sub1"
            sub2 = root / "sub2"
            sub1.mkdir()
            sub2.mkdir()

            (root / "output.txt").write_text("https://a.com/root.jpg")
            (sub1 / "output.txt").write_text("https://a.com/sub1.jpg")
            (sub2 / "output.txt").write_text("https://a.com/sub2.jpg")

            mock_download_urls.side_effect = lambda f, token=None: [f.parent / "file.jpg"]

            results = download_all_in_directory(root)

            self.assertEqual(len(results), 2)
            self.assertIn(sub1.resolve(), [p.resolve() for p in results.keys()])
            self.assertIn(sub2.resolve(), [p.resolve() for p in results.keys()])


if __name__ == "__main__":
    unittest.main()
