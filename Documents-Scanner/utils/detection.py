"""
detection.py
============

Document boundary and corner detection algorithms.

Uses classical computer vision techniques:
- Multi-scale LAB Lightness & Edge Saliency Maps
- Morphological Closing & Contour Hull Approximation
- CamScanner Multi-Strategy Paper Quadrilateral Detector

Part of the Devsil Document Scanner Application.
"""

from __future__ import annotations

import logging
from typing import List, Tuple

import cv2
import numpy as np

from utils.processing_utils import find_document_corners, order_points

logger = logging.getLogger(__name__)


class DocumentNotFoundError(Exception):
    """Raised when no valid document boundary could be identified."""


def detect_edges(image: np.ndarray, low_thresh: int = 30, high_thresh: int = 150) -> np.ndarray:
    """Compute Canny edge map with Gaussian blurring."""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    blurred = cv2.GaussianBlur(gray, (9, 9), 0)
    return cv2.Canny(blurred, low_thresh, high_thresh)


def combine_edge_sources(edges: np.ndarray, threshold: np.ndarray) -> np.ndarray:
    """Combine Canny edge map with threshold map using bitwise OR and morphological closing."""
    if edges.shape != threshold.shape:
        threshold = cv2.resize(threshold, (edges.shape[1], edges.shape[0]))
    combined = cv2.bitwise_or(edges, cv2.bitwise_not(threshold))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 21))
    return cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel, iterations=3)


def detect_document_contour(
    blur: np.ndarray,
    threshold: np.ndarray,
    image_size: Tuple[int, int],
) -> np.ndarray:
    """
    Detect the 4 corner points of the outer document boundary.
    """
    edges = detect_edges(blur)
    combined = combine_edge_sources(edges, threshold)
    corners, is_fallback = find_document_corners(combined)
    return corners


def get_full_frame_fallback(image_size: Tuple[int, int], margin: float = 0.02) -> np.ndarray:
    """Return fallback document rectangle matching full frame with safety margin."""
    h, w = image_size
    m_w = int(w * margin)
    m_h = int(h * margin)
    pts = np.array(
        [
            [m_w, m_h],
            [w - m_w, m_h],
            [w - m_w, h - m_h],
            [m_w, h - m_h],
        ],
        dtype=np.float32,
    )
    return order_points(pts)
