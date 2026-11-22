"""
image_utils.py
==============

Utility functions for image I/O, format conversion, visualization overlays,
and PDF document export (with A4 / Letter page sizing support).

Part of the Devsil Document Scanner Application.
"""

from __future__ import annotations

import logging
import os
from typing import List, Optional, Tuple, Union

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


def read_image_from_source(source: Union[str, bytes, np.ndarray, Image.Image]) -> np.ndarray:
    """Load an image from various input sources into an OpenCV BGR numpy array."""
    if isinstance(source, np.ndarray):
        if source.size == 0:
            raise ValueError("Input image array is empty.")
        return source.copy()

    if isinstance(source, Image.Image):
        rgb = np.array(source.convert("RGB"))
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    if isinstance(source, bytes):
        nparr = np.frombuffer(source, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Could not decode image bytes.")
        return img

    if isinstance(source, str):
        if not os.path.exists(source):
            raise FileNotFoundError(f"Image file not found: {source}")
        img = cv2.imread(source)
        if img is None:
            raise ValueError(f"Could not read image file: {source}")
        return img

    raise TypeError(f"Unsupported image source type: {type(source)}")


def bgr_to_rgb(image: np.ndarray) -> np.ndarray:
    """Convert an OpenCV BGR image to RGB."""
    if len(image.shape) == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def bgr_to_pil(image: np.ndarray) -> Image.Image:
    """Convert an OpenCV BGR image to a PIL Image."""
    rgb = bgr_to_rgb(image)
    return Image.fromarray(rgb)


def draw_contour_overlay(
    image: np.ndarray,
    corners: np.ndarray,
    color: Tuple[int, int, int] = (0, 255, 0),
    thickness: int = 4,
    draw_dots: bool = True,
) -> np.ndarray:
    """Draw detected document bounding corners/contour on top of an image."""
    overlay = image.copy()
    if len(overlay.shape) == 2:
        overlay = cv2.cvtColor(overlay, cv2.COLOR_GRAY2BGR)

    pts = corners.reshape((-1, 1, 2)).astype(np.int32)
    cv2.polylines(overlay, [pts], isClosed=True, color=color, thickness=thickness)

    if draw_dots:
        corner_colors = [
            (0, 0, 255),    # Top-Left (Red)
            (0, 255, 255),  # Top-Right (Yellow)
            (255, 0, 0),    # Bottom-Right (Blue)
            (0, 255, 0),    # Bottom-Left (Green)
        ]
        for i, pt in enumerate(corners.reshape(4, 2)):
            x, y = int(pt[0]), int(pt[1])
            dot_color = corner_colors[i % len(corner_colors)]
            cv2.circle(overlay, (x, y), thickness * 3, dot_color, -1)
            cv2.circle(overlay, (x, y), thickness * 3 + 2, (255, 255, 255), 1)

    return overlay


def save_image(image: np.ndarray, output_path: str) -> str:
    """Save OpenCV image array to filesystem."""
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    success = cv2.imwrite(output_path, image)
    if not success:
        raise IOError(f"Failed to write image to {output_path}")

    return os.path.abspath(output_path)


def export_images_to_pdf(
    images: List[np.ndarray],
    output_pdf_path: str,
    page_format: str = "A4",
) -> str:
    """
    Combine scanned images into a single PDF document.
    Supports A4, Letter, or Auto page formats.
    """
    if not images:
        raise ValueError("No images provided for PDF export.")

    out_dir = os.path.dirname(output_pdf_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    pil_images = []
    for img in images:
        pil_img = bgr_to_pil(img).convert("RGB")

        if page_format.upper() == "A4":
            # A4 standard at 150 DPI: 1240 x 1754 px
            target_size = (1240, 1754)
            canvas = Image.new("RGB", target_size, (255, 255, 255))
            pil_img.thumbnail(target_size, Image.Resampling.LANCZOS)
            offset = ((target_size[0] - pil_img.width) // 2, (target_size[1] - pil_img.height) // 2)
            canvas.paste(pil_img, offset)
            pil_images.append(canvas)
        elif page_format.upper() == "LETTER":
            # Letter standard at 150 DPI: 1275 x 1650 px
            target_size = (1275, 1650)
            canvas = Image.new("RGB", target_size, (255, 255, 255))
            pil_img.thumbnail(target_size, Image.Resampling.LANCZOS)
            offset = ((target_size[0] - pil_img.width) // 2, (target_size[1] - pil_img.height) // 2)
            canvas.paste(pil_img, offset)
            pil_images.append(canvas)
        else:
            pil_images.append(pil_img)

    first_image = pil_images[0]
    rest_images = pil_images[1:] if len(pil_images) > 1 else []

    first_image.save(
        output_pdf_path,
        "PDF",
        resolution=150.0,
        save_all=True,
        append_images=rest_images,
    )

    return os.path.abspath(output_pdf_path)
