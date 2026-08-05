import unittest
import numpy as np
from utils.processing_utils import (
    find_document_corners,
    four_point_transform,
    order_points,
)


class TestDetectionAndTransform(unittest.TestCase):
    def test_order_points(self):
        # Unordered points: BR, TL, TR, BL
        pts = np.array([[500, 500], [10, 10], [500, 10], [10, 500]], dtype=np.float32)
        ordered = order_points(pts)

        # Expected: TL (10,10), TR (500,10), BR (500,500), BL (10,500)
        np.testing.assert_array_almost_equal(ordered[0], [10, 10])
        np.testing.assert_array_almost_equal(ordered[1], [500, 10])
        np.testing.assert_array_almost_equal(ordered[2], [500, 500])
        np.testing.assert_array_almost_equal(ordered[3], [10, 500])

    def test_find_document_corners_synthetic(self):
        # Create binary edge image with a rectangle
        edge_map = np.zeros((400, 400), dtype=np.uint8)
        edge_map[50:350, 50:350] = 255
        corners, is_fallback = find_document_corners(edge_map)
        self.assertEqual(corners.shape, (4, 2))

    def test_four_point_transform(self):
        img = np.zeros((400, 400, 3), dtype=np.uint8)
        img[50:350, 50:350] = (255, 255, 255)
        pts = np.array([[50, 50], [350, 50], [350, 350], [50, 350]], dtype=np.float32)
        warped = four_point_transform(img, pts)
        self.assertGreater(warped.shape[0], 0)
        self.assertGreater(warped.shape[1], 0)


if __name__ == "__main__":
    unittest.main()
