import tempfile
import unittest
from pathlib import Path

from core.downloads.archive import (
    classify_invalid_download_response,
    validate_zip_download,
)


class DownloadArchiveTests(unittest.TestCase):
    def test_classifies_certificate_html_response(self):
        self.assertEqual(
            classify_invalid_download_response("<html><title>Certificate Error</title>"),
            "a fonte retornou uma pagina HTML de erro de certificado/proxy",
        )

    def test_invalid_zip_error_redacts_signed_url_and_explains_html(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "download.zip"
            path.write_text("<!DOCTYPE html><title>Certificate Error</title>", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "erro de certificado/proxy") as ctx:
                validate_zip_download(
                    path,
                    "https://host/path/file.zip?X-Amz-Signature=secret",
                )

        self.assertIn("https://host/path/file.zip", str(ctx.exception))
        self.assertNotIn("secret", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
