import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
from s3_manager import S3FileManager, format_size

class S3FileManagerTests(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.manager = S3FileManager("test-bucket", client=self.client)

    def test_upload_uses_filename_by_default(self):
        with tempfile.NamedTemporaryFile() as file:
            result = self.manager.upload_file(file.name)
        self.client.upload_file.assert_called_once_with(file.name, "test-bucket", Path(file.name).name)
        self.assertEqual(result, Path(file.name).name)

    def test_upload_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            self.manager.upload_file("does-not-exist.txt")

    def test_list_objects_collects_pages(self):
        paginator = Mock()
        paginator.paginate.return_value = [{"Contents": [{"Key": "a"}]}, {"Contents": [{"Key": "b"}]}]
        self.client.get_paginator.return_value = paginator
        self.assertEqual([x["Key"] for x in self.manager.list_objects()], ["a", "b"])

    def test_presigned_url(self):
        self.client.generate_presigned_url.return_value = "https://example.test/file"
        self.assertEqual(self.manager.generate_download_url("file.txt", 120), "https://example.test/file")
        self.client.generate_presigned_url.assert_called_once_with(
            "get_object", Params={"Bucket": "test-bucket", "Key": "file.txt"}, ExpiresIn=120
        )

    def test_invalid_expiry(self):
        with self.assertRaises(ValueError):
            self.manager.generate_download_url("file.txt", 700000)

    def test_delete(self):
        self.manager.delete_object("file.txt")
        self.client.delete_object.assert_called_once_with(Bucket="test-bucket", Key="file.txt")

    def test_format_size(self):
        self.assertEqual(format_size(1024), "1.0 KB")
        self.assertEqual(format_size(0), "0.0 B")

if __name__ == "__main__":
    unittest.main()
