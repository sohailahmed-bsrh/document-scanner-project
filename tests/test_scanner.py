import os
import unittest
import numpy as np
from scanner import DocumentScanner, ScanResult


class TestDocumentScanner(unittest.TestCase):
    def setUp(self):
        self.output_dir = "dataset/output_images"
        self.scanner = DocumentScanner(output_dir=self.output_dir)

    def test_scan_synthetic_image(self):
        # Create a synthetic image containing a tilted white sheet
        img = np.zeros((600, 600, 3), dtype=np.uint8)
        pts = np.array([[100, 150], [500, 100], [450, 500], [120, 480]], dtype=np.int32)
        import cv2

        cv2.fillPoly(img, [pts], (240, 240, 240))

        res = self.scanner.scan(img, save_output=False)
        self.assertIsInstance(res, ScanResult)
        self.assertIsNotNone(res.enhanced)
        self.assertEqual(len(res.enhanced.shape), 3)

    def test_scan_real_sample_image(self):
        sample_path = "dataset/input_images/mydoc1.jpg"
        if os.path.exists(sample_path):
            res = self.scanner.scan(sample_path, save_output=True)
            self.assertIsNotNone(res.saved_path)
            self.assertTrue(os.path.exists(res.saved_path))


if __name__ == "__main__":
    unittest.main()
