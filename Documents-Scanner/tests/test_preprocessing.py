import unittest
import numpy as np
from utils.processing_utils import preprocess_image, resize_image


class TestPreprocessing(unittest.TestCase):
    def setUp(self):
        # Create a synthetic image (1000x800)
        self.image = np.zeros((1000, 800, 3), dtype=np.uint8)
        self.image[200:800, 100:700] = 255  # White rectangle on black canvas

    def test_resize_image(self):
        resized, ratio = resize_image(self.image, target_height=500)
        self.assertEqual(resized.shape[0], 500)
        self.assertEqual(resized.shape[1], 400)
        self.assertAlmostEqual(ratio, 2.0)

    def test_preprocess_pipeline(self):
        prep = preprocess_image(self.image, target_height=500)
        self.assertIn("resized", prep)
        self.assertIn("gray", prep)
        self.assertIn("blur", prep)
        self.assertIn("edges", prep)
        self.assertEqual(prep["resized"].shape[0], 500)
        self.assertEqual(len(prep["gray"].shape), 2)


if __name__ == "__main__":
    unittest.main()
