"""
helper.py
=========

General-purpose geometry and utility helpers shared across the Document
Scanner pipeline: point ordering, distance calculations, the four-point
perspective transform, resizing helpers, and small aspect-ratio /
geometry utilities.

Kept dependency-light (OpenCV + NumPy only) and fully stateless so it can
be reused by detection, enhancement, and the main scanner pipeline
without introducing coupling between them.

Author: Senior Computer Vision Engineering Team
"""

from __future__ import annotations

import logging
from typing import Tuple

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class GeometryError(Exception):
    """Raised when a geometric operation receives invalid input."""


# --------------------------------------------------------------------------- #
# Point ordering
# --------------------------------------------------------------------------- #

def order_points(points: np.ndarray) -> np.ndarray:
    """
    Order four 2D points consistently as
    [top-left, top-right, bottom-right, bottom-left].

    This is essential because contour approximation returns points in an
    arbitrary order, and a stable ordering is required to build a correct
    perspective transform matrix.

    The method works by:
        1. Using the sum of (x + y) to find top-left (smallest sum) and
           bottom-right (largest sum).
        2. Using the difference (x - y) to find top-right (smallest
           difference) and bottom-left (largest difference).

    Args:
        points: Array of shape (4, 2) containing the four corner points.

    Returns:
        Array of shape (4, 2), dtype float32, ordered as
        [top-left, top-right, bottom-right, bottom-left].

    Raises:
        GeometryError: If ``points`` does not contain exactly four points.
    """
    points = np.asarray(points, dtype=np.float32).reshape(-1, 2)

    if points.shape[0] != 4:
        raise GeometryError(f"Expected exactly 4 points, got {points.shape[0]}.")

    ordered = np.zeros((4, 2), dtype=np.float32)

    point_sum = points.sum(axis=1)
    ordered[0] = points[np.argmin(point_sum)]  # top-left
    ordered[2] = points[np.argmax(point_sum)]  # bottom-right

    point_diff = np.diff(points, axis=1).flatten()
    ordered[1] = points[np.argmin(point_diff)]  # top-right
    ordered[3] = points[np.argmax(point_diff)]  # bottom-left

    return ordered


# --------------------------------------------------------------------------- #
# Distance calculations
# --------------------------------------------------------------------------- #

def euclidean_distance(point_a: np.ndarray, point_b: np.ndarray) -> float:
    """
    Compute the Euclidean distance between two 2D points.

    Args:
        point_a: First point as (x, y).
        point_b: Second point as (x, y).

    Returns:
        The straight-line distance between the two points.
    """
    point_a = np.asarray(point_a, dtype=np.float32)
    point_b = np.asarray(point_b, dtype=np.float32)
    return float(np.linalg.norm(point_a - point_b))


def compute_dimensions(ordered_points: np.ndarray) -> Tuple[int, int]:
    """
    Compute the target width and height for a warped document based on
    its four ordered corner points, by taking the maximum of the top and
    bottom edge lengths (width) and the maximum of the left and right
    edge lengths (height). This avoids stretching/squashing distortion.

    Args:
        ordered_points: Array of shape (4, 2) ordered as
            [top-left, top-right, bottom-right, bottom-left].

    Returns:
        Tuple of (width, height) in pixels, each at least 1.
    """
    (top_left, top_right, bottom_right, bottom_left) = ordered_points

    width_top = euclidean_distance(top_right, top_left)
    width_bottom = euclidean_distance(bottom_right, bottom_left)
    max_width = max(int(width_top), int(width_bottom), 1)

    height_left = euclidean_distance(bottom_left, top_left)
    height_right = euclidean_distance(bottom_right, top_right)
    max_height = max(int(height_left), int(height_right), 1)

    return max_width, max_height


# --------------------------------------------------------------------------- #
# Perspective transform
# --------------------------------------------------------------------------- #

def four_point_transform(image: np.ndarray, points: np.ndarray) -> np.ndarray:
    """
    Apply a perspective (bird's-eye / top-down) transform to an image
    given four corner points of the region to extract.

    Args:
        image: Source image (BGR or grayscale) to warp.
        points: Array of 4 points, in any order, describing the
            quadrilateral region to transform.

    Returns:
        The perspective-warped, top-down image cropped to the document
        boundaries.

    Raises:
        GeometryError: If the image is invalid or fewer/more than 4
            points are supplied.
    """
    if image is None or image.size == 0:
        raise GeometryError("Cannot warp an empty or None image.")

    ordered = order_points(points)
    (top_left, top_right, bottom_right, bottom_left) = ordered

    max_width, max_height = compute_dimensions(ordered)

    destination = np.array(
        [
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1],
        ],
        dtype=np.float32,
    )

    transform_matrix = cv2.getPerspectiveTransform(ordered, destination)
    warped = cv2.warpPerspective(image, transform_matrix, (max_width, max_height))

    return warped


def scale_points(points: np.ndarray, ratio: float) -> np.ndarray:
    """
    Scale a set of points by a given ratio. Used to map corner points
    detected on a resized (downscaled) image back to the coordinate
    space of the original full-resolution image.

    Args:
        points: Array of shape (N, 2) points to scale.
        ratio: Scale factor (typically original_height / resized_height).

    Returns:
        Scaled points, same shape as input, dtype float32.
    """
    points = np.asarray(points, dtype=np.float32).reshape(-1, 2)
    return points * float(ratio)


# --------------------------------------------------------------------------- #
# Resize helpers
# --------------------------------------------------------------------------- #

def resize_keep_aspect(
    image: np.ndarray,
    width: int = None,
    height: int = None,
    interpolation: int = cv2.INTER_AREA,
) -> np.ndarray:
    """
    Resize an image to a target width or height while preserving aspect
    ratio. If both are provided, width takes precedence. If neither is
    provided, the original image is returned unchanged.

    Args:
        image: Source image.
        width: Desired width in pixels.
        height: Desired height in pixels.
        interpolation: OpenCV interpolation flag.

    Returns:
        The resized image.

    Raises:
        GeometryError: If the image is invalid.
    """
    if image is None or image.size == 0:
        raise GeometryError("Cannot resize an empty or None image.")

    if width is None and height is None:
        return image.copy()

    original_height, original_width = image.shape[:2]

    if width is not None:
        ratio = width / float(original_width)
        target_size = (width, int(original_height * ratio))
    else:
        ratio = height / float(original_height)
        target_size = (int(original_width * ratio), height)

    return cv2.resize(image, target_size, interpolation=interpolation)


# --------------------------------------------------------------------------- #
# Aspect ratio / geometry utilities
# --------------------------------------------------------------------------- #

def contour_area_ratio(contour: np.ndarray, image_shape: Tuple[int, int]) -> float:
    """
    Compute what fraction of the total image area a contour occupies.

    Args:
        contour: Contour points array.
        image_shape: (height, width) of the reference image.

    Returns:
        Ratio in [0, 1] representing contour_area / image_area.
    """
    image_area = float(image_shape[0] * image_shape[1])
    if image_area <= 0:
        return 0.0
    return float(cv2.contourArea(contour)) / image_area


def aspect_ratio_of_points(points: np.ndarray) -> float:
    """
    Compute the aspect ratio (width / height) implied by four ordered
    corner points. Useful for sanity-checking that a detected
    quadrilateral resembles a plausible document (not an extreme sliver).

    Args:
        points: Array of shape (4, 2), any order.

    Returns:
        Width-to-height ratio as a positive float. Returns a large
        sentinel value if height is degenerate (near zero).
    """
    ordered = order_points(points)
    width, height = compute_dimensions(ordered)
    if height == 0:
        return float("inf")
    return width / float(height)


def is_convex_quadrilateral(points: np.ndarray) -> bool:
    """
    Check whether four points form a convex quadrilateral, which real
    document boundaries always are (documents don't have concave
    corners).

    Args:
        points: Array of shape (4, 2) or (4, 1, 2).

    Returns:
        True if the polygon is convex, False otherwise.
    """
    reshaped = np.asarray(points, dtype=np.float32).reshape(-1, 1, 2)
    return bool(cv2.isContourConvex(reshaped.astype(np.int32)))


def midpoint(point_a: np.ndarray, point_b: np.ndarray) -> Tuple[float, float]:
    """
    Compute the midpoint between two 2D points.

    Args:
        point_a: First point (x, y).
        point_b: Second point (x, y).

    Returns:
        Tuple (x, y) representing the midpoint.
    """
    point_a = np.asarray(point_a, dtype=np.float32)
    point_b = np.asarray(point_b, dtype=np.float32)
    mid = (point_a + point_b) / 2.0
    return float(mid[0]), float(mid[1])
