"""
enhancement.py
==============

Post-warp image enhancement for the Professional AI Document Scanner.

Once the document has been perspective-corrected, this module offers a
set of enhancement "modes" analogous to the filters found in apps like
Adobe Scan / CamScanner (original, black & white, magic color, high
contrast, etc.), plus a library of individual, composable operations
(sharpening, denoising, brightness/contrast correction) that the modes
are built from.

Author: Senior Computer Vision Engineering Team
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Callable, Dict

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class EnhancementError(Exception):
    """Raised when an enhancement operation receives invalid input."""


def _validate(image: np.ndarray) -> None:
    """Raise :class:`EnhancementError` if the image is missing or empty."""
    if image is None or not isinstance(image, np.ndarray) or image.size == 0:
        raise EnhancementError("Cannot enhance an empty or invalid image.")


# --------------------------------------------------------------------------- #
# Enhancement modes enum
# --------------------------------------------------------------------------- #

class EnhancementMode(str, Enum):
    """Supported final-scan enhancement modes."""

    ORIGINAL = "original"
    BLACK_AND_WHITE = "black_and_white"
    MAGIC_COLOR = "magic_color"
    HIGH_CONTRAST = "high_contrast"
    ADAPTIVE_THRESHOLD = "adaptive_threshold"
    NOISE_REDUCTION = "noise_reduction"
    SHARPEN = "sharpen"
    BRIGHTNESS_CORRECTION = "brightness_correction"
    CONTRAST_ENHANCEMENT = "contrast_enhancement"


# --------------------------------------------------------------------------- #
# Individual enhancement operations
# --------------------------------------------------------------------------- #

def sharpen_image(image: np.ndarray, strength: float = 1.0) -> np.ndarray:
    """
    Sharpen an image using an unsharp-mask style kernel, which improves
    legibility of printed and handwritten text after warping.

    Args:
        image: Input BGR or grayscale image.
        strength: Multiplier controlling sharpening intensity (1.0 = default).

    Returns:
        Sharpened image, same shape/dtype as input.
    """
    _validate(image)
    base_kernel = np.array(
        [[0, -1, 0], [-1, 5, -1], [0, -1, 0]],
        dtype=np.float32,
    )
    # Blend toward identity as strength decreases, and amplify as it increases.
    identity = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]], dtype=np.float32)
    kernel = identity + (base_kernel - identity) * strength
    return cv2.filter2D(image, -1, kernel)


def reduce_noise_color(image: np.ndarray, strength: int = 10) -> np.ndarray:
    """
    Apply Non-Local Means denoising suited for color (BGR) images,
    smoothing sensor noise while preserving text edges.

    Args:
        image: Input BGR image.
        strength: Filter strength for luminance channel.

    Returns:
        Denoised BGR image.
    """
    _validate(image)
    if image.ndim == 2:
        return cv2.fastNlMeansDenoising(image, None, strength, 7, 21)
    return cv2.fastNlMeansDenoisingColored(image, None, strength, strength, 7, 21)


def correct_brightness(image: np.ndarray, target_mean: float = 180.0) -> np.ndarray:
    """
    Shift image brightness so its mean intensity approaches
    ``target_mean``, brightening dim scans or toning down overexposed ones.

    Args:
        image: Input BGR or grayscale image.
        target_mean: Desired mean pixel intensity (0-255).

    Returns:
        Brightness-adjusted image.
    """
    _validate(image)
    gray = image if image.ndim == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    current_mean = float(np.mean(gray))

    if current_mean <= 1e-6:
        return image.copy()

    shift = target_mean - current_mean
    corrected = image.astype(np.float32) + shift
    return np.clip(corrected, 0, 255).astype(np.uint8)


def enhance_contrast(image: np.ndarray, alpha: float = 1.25, beta: float = 0.0) -> np.ndarray:
    """
    Linearly enhance contrast via ``output = alpha * input + beta``.

    Args:
        image: Input BGR or grayscale image.
        alpha: Contrast gain (>1 increases contrast).
        beta: Brightness offset added after scaling.

    Returns:
        Contrast-enhanced image.
    """
    _validate(image)
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)


def apply_clahe(image: np.ndarray, clip_limit: float = 2.5, tile_grid_size: tuple = (8, 8)) -> np.ndarray:
    """
    Apply Contrast Limited Adaptive Histogram Equalization for locally
    adaptive contrast improvement, ideal for scans with uneven lighting
    or faded print.

    Args:
        image: Input BGR or grayscale image.
        clip_limit: Contrast limiting threshold.
        tile_grid_size: Grid size for local equalization tiles.

    Returns:
        Contrast-enhanced image, same channel layout as input.
    """
    _validate(image)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)

    if image.ndim == 2:
        return clahe.apply(image)

    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    l_channel = clahe.apply(l_channel)
    merged = cv2.merge((l_channel, a_channel, b_channel))
    return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)


def to_black_and_white_scan(image: np.ndarray, block_size: int = 21, constant: int = 10) -> np.ndarray:
    """
    Convert a warped document into a clean, high-contrast black & white
    scan using adaptive Gaussian thresholding -- the classic "scanned
    document" look, robust to shadows and uneven lighting.

    Args:
        image: Input BGR or grayscale image.
        block_size: Neighborhood size for adaptive thresholding (odd, > 1).
        constant: Constant subtracted from the local mean.

    Returns:
        Single-channel binary (black & white) scan image.
    """
    _validate(image)
    gray = image if image.ndim == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    if block_size % 2 == 0:
        block_size += 1
    block_size = max(block_size, 3)

    binary = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        block_size,
        constant,
    )
    return binary


def to_magic_color_scan(image: np.ndarray) -> np.ndarray:
    """
    Produce a "magic color" style scan: boosts saturation and contrast
    while brightening the background, similar to CamScanner's "Magic
    Color" filter, which keeps color content but makes the page look
    clean and vivid.

    Args:
        image: Input BGR image.

    Returns:
        Enhanced BGR image.
    """
    _validate(image)
    working = image if image.ndim == 3 else cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    hsv = cv2.cvtColor(working, cv2.COLOR_BGR2HSV).astype(np.float32)
    hue, saturation, value = cv2.split(hsv)
    saturation = np.clip(saturation * 1.3, 0, 255)
    value = np.clip(value * 1.08, 0, 255)
    hsv_boosted = cv2.merge((hue, saturation, value)).astype(np.uint8)
    boosted = cv2.cvtColor(hsv_boosted, cv2.COLOR_HSV2BGR)

    contrasted = enhance_contrast(boosted, alpha=1.15, beta=10)
    return apply_clahe(contrasted, clip_limit=2.0)


def to_high_contrast_scan(image: np.ndarray) -> np.ndarray:
    """
    Produce a bold, high-contrast grayscale scan suited for faded prints
    or low-ink documents.

    Args:
        image: Input BGR or grayscale image.

    Returns:
        Single-channel high-contrast grayscale image.
    """
    _validate(image)
    gray = image if image.ndim == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    equalized = apply_clahe(gray, clip_limit=3.0)
    return enhance_contrast(equalized, alpha=1.4, beta=-20)


# --------------------------------------------------------------------------- #
# Mode dispatch
# --------------------------------------------------------------------------- #

def _mode_original(image: np.ndarray) -> np.ndarray:
    """Return a lightly cleaned version of the color scan (denoise + sharpen)."""
    denoised = reduce_noise_color(image, strength=7)
    return sharpen_image(denoised, strength=0.6)


def _mode_noise_reduction(image: np.ndarray) -> np.ndarray:
    return reduce_noise_color(image, strength=12)


_MODE_DISPATCH: Dict[EnhancementMode, Callable[[np.ndarray], np.ndarray]] = {
    EnhancementMode.ORIGINAL: _mode_original,
    EnhancementMode.BLACK_AND_WHITE: to_black_and_white_scan,
    EnhancementMode.MAGIC_COLOR: to_magic_color_scan,
    EnhancementMode.HIGH_CONTRAST: to_high_contrast_scan,
    EnhancementMode.ADAPTIVE_THRESHOLD: to_black_and_white_scan,
    EnhancementMode.NOISE_REDUCTION: _mode_noise_reduction,
    EnhancementMode.SHARPEN: sharpen_image,
    EnhancementMode.BRIGHTNESS_CORRECTION: correct_brightness,
    EnhancementMode.CONTRAST_ENHANCEMENT: enhance_contrast,
}


def enhance_document(
    image: np.ndarray,
    mode: EnhancementMode = EnhancementMode.MAGIC_COLOR,
) -> np.ndarray:
    """
    Apply the requested enhancement mode to a perspective-warped document
    image, producing the final scan-ready output.

    Args:
        image: Perspective-warped BGR document image.
        mode: Which enhancement mode to apply. Defaults to
            ``EnhancementMode.MAGIC_COLOR``, which gives a clean,
            vivid, print-like result suitable for most documents.

    Returns:
        The enhanced image (may be single-channel for modes that produce
        grayscale/binary output).

    Raises:
        EnhancementError: If the image is invalid or the mode is unknown.
    """
    _validate(image)

    handler = _MODE_DISPATCH.get(mode)
    if handler is None:
        raise EnhancementError(f"Unknown enhancement mode: '{mode}'.")

    logger.info("Applying enhancement mode: %s", mode.value)
    return handler(image)
