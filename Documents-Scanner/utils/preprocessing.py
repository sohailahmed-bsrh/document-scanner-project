"""
preprocessing.py
=================

Image preprocessing utilities for the Professional AI Document Scanner.

This module is responsible for every operation that happens on the raw
input image *before* edge detection and contour analysis take place. It
covers image I/O, validation, geometric normalization (resizing), color
space conversion, denoising, thresholding, morphology and brightness /
contrast correction.

All functions are pure, stateless and side-effect free (they never mutate
the array passed in -- they always return a new array), which makes this
module safe to reuse across different pipelines (scanning, batch
processing, testing, etc).

Author: Senior Computer Vision Engineering Team
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import numpy as np


# --------------------------------------------------------------------------- #
# Exceptions
# --------------------------------------------------------------------------- #

class ImageValidationError(Exception):
    """Raised when an input image fails validation checks."""


class ImageReadError(Exception):
    """Raised when an image cannot be read from disk."""


# --------------------------------------------------------------------------- #
# Data containers
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class PreprocessResult:
    """
    Container holding the outputs of the preprocessing pipeline.

    Attributes:
        gray: Single-channel grayscale version of the resized image.
        blur: Denoised / blurred single-channel image used for edge
            detection.
        threshold: Binary thresholded image (document vs background).
        resized: The resized BGR image that all the above were derived
            from.
        resize_ratio: Ratio (original_height / resized_height) needed to
            scale detected coordinates back to the original image size.
    """

    gray: np.ndarray
    blur: np.ndarray
    threshold: np.ndarray
    resized: np.ndarray
    resize_ratio: float


# --------------------------------------------------------------------------- #
# Supported file extensions
# --------------------------------------------------------------------------- #

VALID_EXTENSIONS: Tuple[str, ...] = (
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tiff",
    ".tif",
    ".webp",
)

MIN_IMAGE_DIMENSION: int = 50  # pixels, below this the image is unusable


# --------------------------------------------------------------------------- #
# Image I/O and validation
# --------------------------------------------------------------------------- #

def validate_image_path(image_path: str) -> None:
    """
    Validate that the given path points to an existing, readable file with
    a supported image extension.

    Args:
        image_path: Path to the candidate image file.

    Raises:
        ImageValidationError: If the path does not exist, is not a file,
            or has an unsupported extension.
    """
    if not isinstance(image_path, str) or not image_path.strip():
        raise ImageValidationError("Image path must be a non-empty string.")

    if not os.path.exists(image_path):
        raise ImageValidationError(f"Image not found at path: '{image_path}'.")

    if not os.path.isfile(image_path):
        raise ImageValidationError(f"Path is not a file: '{image_path}'.")

    extension = os.path.splitext(image_path)[1].lower()
    if extension not in VALID_EXTENSIONS:
        raise ImageValidationError(
            f"Unsupported file extension '{extension}'. "
            f"Supported extensions are: {', '.join(VALID_EXTENSIONS)}."
        )

    if os.path.getsize(image_path) == 0:
        raise ImageValidationError(f"Image file is empty: '{image_path}'.")


def validate_image_array(image: Optional[np.ndarray]) -> None:
    """
    Validate that an in-memory image array is well formed and usable.

    Args:
        image: The image array to validate.

    Raises:
        ImageValidationError: If the image is None, empty, corrupted, or
            too small to be processed.
    """
    if image is None:
        raise ImageValidationError("Image is None. It may be corrupted or unreadable.")

    if not isinstance(image, np.ndarray):
        raise ImageValidationError("Image is not a valid NumPy array.")

    if image.size == 0:
        raise ImageValidationError("Image array is empty.")

    if image.ndim not in (2, 3):
        raise ImageValidationError(f"Unexpected image dimensionality: {image.ndim}.")

    height, width = image.shape[:2]
    if height < MIN_IMAGE_DIMENSION or width < MIN_IMAGE_DIMENSION:
        raise ImageValidationError(
            f"Image is too small ({width}x{height}). "
            f"Minimum required dimension is {MIN_IMAGE_DIMENSION}px."
        )


def read_image(image_path: str) -> np.ndarray:
    """
    Read an image from disk into a BGR NumPy array, with full validation.

    Args:
        image_path: Path to the image file on disk.

    Returns:
        The loaded image as a BGR NumPy array.

    Raises:
        ImageValidationError: If the path or resulting array fails
            validation.
        ImageReadError: If OpenCV fails to decode the file.
    """
    validate_image_path(image_path)

    image = cv2.imread(image_path, cv2.IMREAD_COLOR)

    if image is None:
        raise ImageReadError(
            f"Failed to decode image at '{image_path}'. "
            f"The file may be corrupted or in an unsupported format."
        )

    validate_image_array(image)
    return image


# --------------------------------------------------------------------------- #
# Geometric normalization
# --------------------------------------------------------------------------- #

def resize_image(
    image: np.ndarray,
    target_height: int = 800,
) -> Tuple[np.ndarray, float]:
    """
    Resize an image so its height matches ``target_height`` while
    preserving aspect ratio. Working on a smaller, normalized image
    dramatically speeds up contour detection and makes the algorithm's
    behavior consistent across wildly different input resolutions.

    Args:
        image: Source BGR or grayscale image.
        target_height: Desired height in pixels after resizing.

    Returns:
        A tuple of (resized_image, ratio) where ``ratio`` is the factor
        needed to scale coordinates found in the resized image back to
        the original image's coordinate space (original / resized).

    Raises:
        ImageValidationError: If the image is invalid.
    """
    validate_image_array(image)

    original_height = image.shape[0]
    ratio = original_height / float(target_height)

    if ratio <= 0:
        ratio = 1.0

    new_width = int(image.shape[1] / ratio)
    new_height = target_height

    interpolation = cv2.INTER_AREA if ratio > 1 else cv2.INTER_CUBIC
    resized = cv2.resize(image, (new_width, new_height), interpolation=interpolation)

    return resized, ratio


def resize_to_width(image: np.ndarray, target_width: int) -> np.ndarray:
    """
    Resize an image to a specific width, preserving aspect ratio.

    Args:
        image: Source image.
        target_width: Desired width in pixels.

    Returns:
        The resized image.
    """
    validate_image_array(image)
    ratio = target_width / float(image.shape[1])
    new_height = int(image.shape[0] * ratio)
    interpolation = cv2.INTER_AREA if ratio < 1 else cv2.INTER_CUBIC
    return cv2.resize(image, (target_width, new_height), interpolation=interpolation)


# --------------------------------------------------------------------------- #
# Color space conversions
# --------------------------------------------------------------------------- #

def to_grayscale(image: np.ndarray) -> np.ndarray:
    """
    Convert a BGR image to single-channel grayscale. If the image is
    already grayscale, it is returned unchanged (copied).

    Args:
        image: BGR or grayscale image.

    Returns:
        Single-channel grayscale image.
    """
    validate_image_array(image)

    if image.ndim == 2:
        return image.copy()

    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# --------------------------------------------------------------------------- #
# Blurring / denoising
# --------------------------------------------------------------------------- #

def apply_gaussian_blur(
    image: np.ndarray,
    kernel_size: Tuple[int, int] = (5, 5),
    sigma: float = 0,
) -> np.ndarray:
    """
    Apply Gaussian blur to smooth out high-frequency noise while
    preserving edges reasonably well.

    Args:
        image: Input single or multi-channel image.
        kernel_size: Size of the Gaussian kernel (must be odd values).
        sigma: Gaussian kernel standard deviation. 0 lets OpenCV compute
            it automatically from the kernel size.

    Returns:
        Blurred image.
    """
    validate_image_array(image)
    kernel_size = _ensure_odd_kernel(kernel_size)
    return cv2.GaussianBlur(image, kernel_size, sigma)


def apply_median_blur(image: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """
    Apply median blur, which is highly effective against salt-and-pepper
    noise while keeping edges sharp -- useful for noisy phone camera
    captures.

    Args:
        image: Input image.
        kernel_size: Aperture size, must be odd and greater than 1.

    Returns:
        Blurred image.
    """
    validate_image_array(image)
    if kernel_size % 2 == 0:
        kernel_size += 1
    kernel_size = max(kernel_size, 3)
    return cv2.medianBlur(image, kernel_size)


def apply_bilateral_filter(
    image: np.ndarray,
    diameter: int = 9,
    sigma_color: float = 75,
    sigma_space: float = 75,
) -> np.ndarray:
    """
    Apply a bilateral filter, which smooths flat regions while keeping
    edges crisp. This is the preferred denoising step before edge
    detection because it does not blur document boundaries.

    Args:
        image: Input image.
        diameter: Diameter of each pixel neighborhood.
        sigma_color: Filter sigma in the color space.
        sigma_space: Filter sigma in the coordinate space.

    Returns:
        Filtered image.
    """
    validate_image_array(image)
    return cv2.bilateralFilter(image, diameter, sigma_color, sigma_space)


def reduce_noise(image: np.ndarray, strength: int = 10) -> np.ndarray:
    """
    Apply Non-Local Means denoising for stronger noise reduction on
    grayscale images that are particularly noisy (e.g. low-light or
    high-ISO mobile captures).

    Args:
        image: Single-channel grayscale image.
        strength: Filter strength; higher values remove more noise but
            can also remove fine detail.

    Returns:
        Denoised grayscale image.
    """
    validate_image_array(image)
    gray = to_grayscale(image)
    return cv2.fastNlMeansDenoising(gray, None, strength, 7, 21)


def _ensure_odd_kernel(kernel_size: Tuple[int, int]) -> Tuple[int, int]:
    """Ensure both kernel dimensions are odd, as required by OpenCV."""
    width, height = kernel_size
    width = width if width % 2 == 1 else width + 1
    height = height if height % 2 == 1 else height + 1
    return max(width, 1), max(height, 1)


# --------------------------------------------------------------------------- #
# Thresholding
# --------------------------------------------------------------------------- #

def apply_adaptive_threshold(
    image: np.ndarray,
    block_size: int = 11,
    constant: int = 2,
) -> np.ndarray:
    """
    Apply adaptive (locally-computed) Gaussian thresholding. This is
    robust to uneven illumination and shadows across the document,
    which is common with hand-held mobile camera captures.

    Args:
        image: Single-channel grayscale image.
        block_size: Size of the pixel neighborhood used to compute the
            threshold (must be odd and > 1).
        constant: Constant subtracted from the computed mean/weighted mean.

    Returns:
        Binary thresholded image.
    """
    validate_image_array(image)
    gray = to_grayscale(image)

    if block_size % 2 == 0:
        block_size += 1
    block_size = max(block_size, 3)

    return cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        block_size,
        constant,
    )


def apply_otsu_threshold(image: np.ndarray) -> np.ndarray:
    """
    Apply Otsu's automatic global thresholding. Otsu determines the
    optimal threshold value that best separates foreground (document)
    from background based on the image histogram.

    Args:
        image: Single-channel grayscale image.

    Returns:
        Binary thresholded image.
    """
    validate_image_array(image)
    gray = to_grayscale(image)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh


# --------------------------------------------------------------------------- #
# Morphological operations
# --------------------------------------------------------------------------- #

def morphological_opening(
    image: np.ndarray,
    kernel_size: Tuple[int, int] = (5, 5),
    iterations: int = 1,
) -> np.ndarray:
    """
    Apply morphological opening (erosion followed by dilation) to remove
    small noise specks such as isolated bright pixels or fine text
    artifacts, without significantly altering the document's shape.

    Args:
        image: Input binary or grayscale image.
        kernel_size: Structuring element size.
        iterations: Number of times the operation is applied.

    Returns:
        Processed image.
    """
    validate_image_array(image)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=iterations)


def morphological_closing(
    image: np.ndarray,
    kernel_size: Tuple[int, int] = (5, 5),
    iterations: int = 1,
) -> np.ndarray:
    """
    Apply morphological closing (dilation followed by erosion) to seal
    small gaps in document edges caused by noise, shadows, or partial
    occlusion -- this helps produce a single continuous contour.

    Args:
        image: Input binary or grayscale image.
        kernel_size: Structuring element size.
        iterations: Number of times the operation is applied.

    Returns:
        Processed image.
    """
    validate_image_array(image)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
    return cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations=iterations)


# --------------------------------------------------------------------------- #
# Brightness / contrast normalization
# --------------------------------------------------------------------------- #

def normalize_image(image: np.ndarray) -> np.ndarray:
    """
    Normalize pixel intensities to span the full [0, 255] range. This
    counteracts globally under- or over-exposed captures.

    Args:
        image: Input image (grayscale or BGR).

    Returns:
        Normalized image with the same shape and dtype as the input.
    """
    validate_image_array(image)
    normalized = np.empty_like(image)
    cv2.normalize(image, normalized, 0, 255, cv2.NORM_MINMAX)
    return normalized


def normalize_brightness(image: np.ndarray, target_mean: float = 128.0) -> np.ndarray:
    """
    Shift image brightness so that its mean intensity approaches
    ``target_mean``. Useful for correcting consistently dark or bright
    captures before thresholding.

    Args:
        image: Input grayscale or BGR image.
        target_mean: Desired mean pixel intensity (0-255).

    Returns:
        Brightness-corrected image, same dtype as input.
    """
    validate_image_array(image)

    gray_for_mean = to_grayscale(image)
    current_mean = float(np.mean(gray_for_mean))

    if current_mean <= 1e-6:
        return image.copy()

    shift = target_mean - current_mean
    corrected = image.astype(np.float32) + shift
    corrected = np.clip(corrected, 0, 255).astype(np.uint8)
    return corrected


def improve_contrast(image: np.ndarray, clip_limit: float = 2.0, tile_grid_size: Tuple[int, int] = (8, 8)) -> np.ndarray:
    """
    Improve local contrast using CLAHE (Contrast Limited Adaptive
    Histogram Equalization). This enhances text and edge visibility in
    documents with faded print or uneven lighting without amplifying
    noise as much as global histogram equalization would.

    Args:
        image: Input grayscale or BGR image.
        clip_limit: Threshold for contrast limiting.
        tile_grid_size: Size of the grid for the histogram equalization.

    Returns:
        Contrast-enhanced image. If input was BGR, output remains BGR.
    """
    validate_image_array(image)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)

    if image.ndim == 2:
        return clahe.apply(image)

    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    l_channel = clahe.apply(l_channel)
    merged = cv2.merge((l_channel, a_channel, b_channel))
    return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)


# --------------------------------------------------------------------------- #
# High-level pipeline
# --------------------------------------------------------------------------- #

def preprocess_image(
    image: np.ndarray,
    target_height: int = 800,
    use_bilateral: bool = True,
) -> PreprocessResult:
    """
    Run the full preprocessing pipeline used by the scanner before edge
    detection: resize -> grayscale -> denoise -> edge-ready threshold.

    Args:
        image: Raw BGR input image (already read from disk).
        target_height: Height to normalize the image to before
            processing, for speed and consistency.
        use_bilateral: If True, use an edge-preserving bilateral filter
            for denoising; otherwise fall back to Gaussian blur.

    Returns:
        A :class:`PreprocessResult` bundling every intermediate image
        needed downstream, plus the resize ratio for coordinate mapping.

    Raises:
        ImageValidationError: If the input image is invalid.
    """
    validate_image_array(image)

    resized, ratio = resize_image(image, target_height=target_height)

    gray = to_grayscale(resized)
    gray = normalize_brightness(gray)
    gray = improve_contrast(gray, clip_limit=2.0)

    if use_bilateral:
        blurred = apply_bilateral_filter(gray, diameter=9, sigma_color=75, sigma_space=75)
    else:
        blurred = apply_gaussian_blur(gray, kernel_size=(5, 5))

    threshold = apply_otsu_threshold(blurred)
    threshold = morphological_closing(threshold, kernel_size=(5, 5), iterations=1)

    return PreprocessResult(
        gray=gray,
        blur=blurred,
        threshold=threshold,
        resized=resized,
        resize_ratio=ratio,
    )
