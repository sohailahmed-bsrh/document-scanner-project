"""
save.py
=======

Output persistence utilities for the Professional AI Document Scanner.

Responsible for creating the output directory tree, generating unique,
timestamped filenames, and writing scanned images to disk with proper
error handling.

Author: Senior Computer Vision Engineering Team
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class SaveError(Exception):
    """Raised when a scanned image cannot be saved to disk."""


DEFAULT_OUTPUT_DIR = os.path.join("dataset", "output_images")


def ensure_output_directory(output_dir: str = DEFAULT_OUTPUT_DIR) -> str:
    """
    Ensure the output directory exists, creating it (and any missing
    parent directories) if necessary.

    Args:
        output_dir: Path to the desired output directory.

    Returns:
        The (now guaranteed to exist) absolute path to the directory.

    Raises:
        SaveError: If the directory cannot be created (e.g. permissions).
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as exc:
        raise SaveError(f"Failed to create output directory '{output_dir}': {exc}") from exc

    return os.path.abspath(output_dir)


def generate_filename(
    source_name: Optional[str] = None,
    suffix: str = "scanned",
    extension: str = ".jpg",
) -> str:
    """
    Generate a unique, descriptive filename for a scanned output image,
    combining the original source filename (if provided), a suffix, and
    a millisecond-precision timestamp to guarantee uniqueness across
    repeated runs.

    Args:
        source_name: Original input filename or path (basename is used;
            extension is stripped). If None, a generic "document" base
            name is used.
        suffix: Descriptive suffix inserted before the timestamp.
        extension: File extension to use for the output (with leading dot).

    Returns:
        A filename string, e.g. "receipt_scanned_20260804_153245123.jpg".
    """
    if source_name:
        base_name = os.path.splitext(os.path.basename(source_name))[0]
    else:
        base_name = "document"

    # Sanitize base name to avoid filesystem-unfriendly characters.
    safe_base = "".join(c for c in base_name if c.isalnum() or c in ("-", "_")) or "document"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")[:-3]

    if not extension.startswith("."):
        extension = f".{extension}"

    return f"{safe_base}_{suffix}_{timestamp}{extension}"


def save_image(
    image: np.ndarray,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    source_name: Optional[str] = None,
    suffix: str = "scanned",
    extension: str = ".jpg",
    jpeg_quality: int = 95,
) -> str:
    """
    Save a scanned image to the output directory with an automatically
    generated, unique filename.

    Args:
        image: The final image (BGR or grayscale) to persist.
        output_dir: Directory to save into; created if it does not exist.
        source_name: Original input filename, used to derive the output
            filename.
        suffix: Descriptive suffix for the generated filename.
        extension: Output file extension (".jpg", ".png", etc.).
        jpeg_quality: JPEG compression quality (0-100), ignored for
            non-JPEG extensions.

    Returns:
        The absolute path to the saved image file.

    Raises:
        SaveError: If the image is invalid or writing to disk fails.
    """
    if image is None or not isinstance(image, np.ndarray) or image.size == 0:
        raise SaveError("Cannot save an empty or invalid image.")

    directory = ensure_output_directory(output_dir)
    filename = generate_filename(source_name=source_name, suffix=suffix, extension=extension)
    full_path = os.path.join(directory, filename)

    write_params = []
    normalized_extension = extension.lower()
    if normalized_extension in (".jpg", ".jpeg"):
        write_params = [cv2.IMWRITE_JPEG_QUALITY, int(jpeg_quality)]
    elif normalized_extension == ".png":
        write_params = [cv2.IMWRITE_PNG_COMPRESSION, 3]

    success = cv2.imwrite(full_path, image, write_params)

    if not success:
        raise SaveError(f"OpenCV failed to write the image to '{full_path}'.")

    logger.info("Scanned image saved to: %s", full_path)
    return full_path
