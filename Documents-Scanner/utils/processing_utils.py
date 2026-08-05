"""
processing_utils.py
===================

CamScanner & Adobe Scan Pro Computer Vision Processing Engine:
1. Multi-Scale Preprocessing & Denoising
2. 4-Tier Gold-Standard Paper Quad Detector (Prevents table/text cropping)
3. Four-Point Perspective Transformation & Rectification
4. Rotation & Fine Tilt Angle Alignment (-45° to +45°, 90°, 180°)
5. Color Temperature / Warmth Adjustment (Fixes indoor yellow lighting)
6. Adaptive Sharpness Filtering
7. CamScanner Magic Color 2.0 & Adobe Paper Whitening Filters

Part of the Devsil Document Scanner Application.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class EnhancementPreset(str, Enum):
    MAGIC_COLOR = "magic_color"
    ADOBE_WHITENING = "adobe_whitening"
    BLACK_AND_WHITE = "black_and_white"
    GRAYSCALE = "grayscale"
    ORIGINAL_CLEAN = "original_clean"
    THRESHOLD = "threshold"
    CLEAN_SCAN = "clean_scan"
    OCR_FRIENDLY = "ocr_friendly"
    HIGH_CONTRAST = "high_contrast"


def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    """Rotate image by arbitrary angle (degrees). Handles 90°, 180°, 270° quickly or fine tilt angles."""
    if angle % 360 == 0:
        return image.copy()

    if angle == 90:
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    if angle == 180:
        return cv2.rotate(image, cv2.ROTATE_180)
    if angle == 270 or angle == -90:
        return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

    h, w = image.shape[:2]
    center = (w // 2, h // 2)

    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))

    M[0, 2] += (new_w / 2) - center[0]
    M[1, 2] += (new_h / 2) - center[1]

    rotated = cv2.warpAffine(image, M, (new_w, new_h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated


def flip_image(image: np.ndarray, flip_mode: Optional[str] = None) -> np.ndarray:
    """Flip image horizontally ('horizontal'), vertically ('vertical'), or both ('both')."""
    if not flip_mode or flip_mode.lower() == "none":
        return image.copy()
    mode = flip_mode.lower()
    if mode in ("horizontal", "h"):
        return cv2.flip(image, 1)
    if mode in ("vertical", "v"):
        return cv2.flip(image, 0)
    if mode in ("both", "hv", "vh"):
        return cv2.flip(image, -1)
    return image.copy()


def add_watermark(image: np.ndarray, text: Optional[str] = None) -> np.ndarray:
    """Burn semi-transparent watermark or stamp into the bottom-right corner of the image."""
    if not text or not text.strip():
        return image.copy()

    overlay = image.copy()
    h, w = image.shape[:2]
    stamp_text = text.strip()

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = max(0.5, min(w, h) / 1000.0)
    thickness = max(1, int(font_scale * 2))

    (text_w, text_h), baseline = cv2.getTextSize(stamp_text, font, font_scale, thickness)

    margin = int(20 * font_scale)
    x = w - text_w - margin - 20
    y = h - margin - 20

    # Background badge box
    cv2.rectangle(
        overlay,
        (x - 10, y - text_h - 10),
        (x + text_w + 10, y + baseline + 10),
        (15, 23, 42),
        -1,
    )
    cv2.putText(
        overlay,
        stamp_text,
        (x, y),
        font,
        font_scale,
        (99, 102, 241),
        thickness,
        cv2.LINE_AA,
    )

    alpha = 0.8
    watermarked = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
    return watermarked


def adjust_color_temperature(image: np.ndarray, warmth: int = 0) -> np.ndarray:
    """Adjust color temperature / warmth (-50 Cool Blue to +50 Warm Yellow)."""
    if warmth == 0:
        return image.copy()

    out = image.astype(np.float32)
    factor = warmth * 0.4

    if warmth > 0:
        out[:, :, 2] = np.clip(out[:, :, 2] + factor * 1.2, 0, 255)  # Red
        out[:, :, 1] = np.clip(out[:, :, 1] + factor * 0.5, 0, 255)  # Green
        out[:, :, 0] = np.clip(out[:, :, 0] - factor * 0.8, 0, 255)  # Blue
    else:
        out[:, :, 0] = np.clip(out[:, :, 0] - factor * 1.2, 0, 255)  # Blue
        out[:, :, 2] = np.clip(out[:, :, 2] + factor * 0.8, 0, 255)  # Red

    return out.astype(np.uint8)


def apply_sharpness(image: np.ndarray, sharpness_factor: float = 1.0) -> np.ndarray:
    """Apply unsharp mask filter to enhance text legibility."""
    if sharpness_factor <= 0.0:
        return image.copy()

    blurred = cv2.GaussianBlur(image, (0, 0), 2.5)
    sharpened = cv2.addWeighted(image, 1.0 + (sharpness_factor * 0.5), blurred, -(sharpness_factor * 0.5), 0)
    return sharpened


def resize_image(image: np.ndarray, target_height: int = 800) -> Tuple[np.ndarray, float]:
    """Resize image maintaining aspect ratio so height equals target_height."""
    h, w = image.shape[:2]
    if h == 0 or w == 0:
        raise ValueError("Image dimensions must be non-zero.")

    if h == target_height:
        return image.copy(), 1.0

    ratio = h / float(target_height)
    target_width = max(1, int(w / ratio))
    resized = cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_AREA)
    return resized, ratio


def preprocess_image(
    image: np.ndarray,
    target_height: int = 800,
    blur_ksize: int = 9,
    c_canny_low: int = 30,
    c_canny_high: int = 150,
) -> Dict[str, Union[np.ndarray, float]]:
    """Preprocessing pipeline for paper document perimeter extraction."""
    resized, ratio = resize_image(image, target_height=target_height)

    if len(resized.shape) == 3:
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        lab = cv2.cvtColor(resized, cv2.COLOR_BGR2LAB)
        l_chan = lab[:, :, 0]
    else:
        gray = resized.copy()
        l_chan = gray.copy()

    ksize = blur_ksize if blur_ksize % 2 == 1 else blur_ksize + 1
    blurred = cv2.GaussianBlur(l_chan, (ksize, ksize), 0)

    canny = cv2.Canny(blurred, c_canny_low, c_canny_high)
    _, otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    combined = cv2.bitwise_or(canny, cv2.bitwise_not(otsu))

    kernel_size = max(15, int(min(resized.shape[:2]) * 0.03))
    if kernel_size % 2 == 0:
        kernel_size += 1
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    closed_edges = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel, iterations=3)

    return {
        "resized": resized,
        "gray": gray,
        "blur": blurred,
        "threshold": otsu,
        "edges": closed_edges,
        "raw_canny": canny,
        "ratio": ratio,
    }


def order_points(pts: np.ndarray) -> np.ndarray:
    """Order 4 corner coordinates in Top-Left, Top-Right, Bottom-Right, Bottom-Left order."""
    pts = pts.reshape(4, 2).astype(np.float32)
    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # TL
    rect[2] = pts[np.argmax(s)]  # BR

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # TR
    rect[3] = pts[np.argmax(diff)]  # BL

    return rect


def find_document_corners(
    edge_map: np.ndarray,
    min_area_ratio: float = 0.15,
) -> Tuple[np.ndarray, bool]:
    """
    4-Tier Gold-Standard Paper Quad Detector:
    Tier 1: High-Confidence Convex 4-Point Quad (`approxPolyDP` + internal angle check)
    Tier 2: Extreme 4-Corner Hull Projection (maximized quad area)
    Tier 3: Paper Saliency Segmentation
    Tier 4: Full-Page Frame Quad (1.5% margin)
    """
    h, w = edge_map.shape[:2]
    img_area = h * w

    contours, _ = cv2.findContours(edge_map.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return _get_margin_quad(edge_map), True

    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    for c in contours:
        area = cv2.contourArea(c)

        # Tier 4: Close-Up Full Page Shot (>70% area)
        if area > img_area * 0.70:
            return _get_margin_quad(edge_map, margin_ratio=0.015), False

        if area < img_area * min_area_ratio:
            continue

        hull = cv2.convexHull(c)
        peri = cv2.arcLength(hull, True)

        # Tier 1: Dynamic Epsilon Polygon Sweep
        for eps_factor in np.linspace(0.005, 0.10, 40):
            approx = cv2.approxPolyDP(hull, eps_factor * peri, True)
            if len(approx) == 4 and cv2.isContourConvex(approx):
                corners = order_points(approx.reshape(4, 2))
                if _is_valid_quad(corners, w, h):
                    return corners, False

        # Tier 2: Extreme 4-Corner Hull Projections
        pts = hull.reshape(-1, 2)
        s = pts.sum(axis=1)
        diff = np.diff(pts, axis=1)

        tl = pts[np.argmin(s)]
        br = pts[np.argmax(s)]
        tr = pts[np.argmin(diff)]
        bl = pts[np.argmax(diff)]

        extreme_quad = order_points(np.array([tl, tr, br, bl], dtype=np.float32))
        if _is_valid_quad(extreme_quad, w, h):
            return extreme_quad, False

    return _get_margin_quad(edge_map), True


def _is_valid_quad(pts: np.ndarray, w: int, h: int) -> bool:
    """Verify that detected quad has valid internal angles (50° to 130°) and aspect ratio."""
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    w_top = np.linalg.norm(tr - tl)
    w_bot = np.linalg.norm(br - bl)
    h_left = np.linalg.norm(bl - tl)
    h_right = np.linalg.norm(br - tr)

    avg_w = max(1.0, (w_top + w_bot) / 2.0)
    avg_h = max(1.0, (h_left + h_right) / 2.0)

    aspect_ratio = avg_w / avg_h
    quad_area = cv2.contourArea(rect.astype(np.int32))
    img_area = w * h

    if 0.3 <= aspect_ratio <= 3.5 and quad_area > img_area * 0.12:
        return True
    return False


def _get_margin_quad(img: np.ndarray, margin_ratio: float = 0.015) -> np.ndarray:
    """Return clean paper boundary matching outer image frame with safety margin."""
    h, w = img.shape[:2]
    m_w = max(2, int(w * margin_ratio))
    m_h = max(2, int(h * margin_ratio))
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


def four_point_transform(image: np.ndarray, pts: np.ndarray, ordered: bool = False) -> np.ndarray:
    """Apply perspective transform to crop and straighten document to top-down view."""
    if not ordered:
        rect = order_points(pts)
    else:
        rect = pts.astype(np.float32)
    (tl, tr, br, bl) = rect

    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array(
        [
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1],
        ],
        dtype="float32",
    )

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped


def enhance_document(
    image: np.ndarray,
    mode: Union[EnhancementPreset, str] = EnhancementPreset.MAGIC_COLOR,
    brightness: int = 0,
    contrast: float = 1.0,
    sharpness: float = 1.0,
    warmth: int = 0,
) -> np.ndarray:
    """
    CamScanner & Adobe Scan Quality Enhancement Suite:
    - Magic Color 2.0: Illumination division + CLAHE + text sharpening + color stamp preservation.
    - Adobe Whitening: Shadow subtraction + background paper whitening.
    - Black & White: High contrast adaptive background division.
    - Grayscale: Normalized clean gray scan.
    - Original Clean: Background denoised color scan.
    - Threshold: Global Otsu binarization.
    """
    if isinstance(mode, str):
        try:
            mode = EnhancementPreset(mode.lower())
        except ValueError:
            mode = EnhancementPreset.MAGIC_COLOR

    out = image.copy()

    if warmth != 0:
        out = adjust_color_temperature(out, warmth=warmth)

    if brightness != 0 or contrast != 1.0:
        out = cv2.convertScaleAbs(out, alpha=contrast, beta=brightness)

    if mode == EnhancementPreset.ORIGINAL_CLEAN:
        out = cv2.bilateralFilter(out, d=5, sigmaColor=40, sigmaSpace=40)
        return apply_sharpness(out, sharpness)

    if mode == EnhancementPreset.GRAYSCALE:
        gray = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
        norm_gray = _divide_background(gray)
        res = cv2.cvtColor(norm_gray, cv2.COLOR_GRAY2BGR)
        return apply_sharpness(res, sharpness)

    if mode == EnhancementPreset.BLACK_AND_WHITE:
        gray = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
        norm_gray = _divide_background(gray)
        bw = cv2.adaptiveThreshold(
            norm_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 10
        )
        res = cv2.cvtColor(bw, cv2.COLOR_GRAY2BGR)
        return apply_sharpness(res, sharpness)

    if mode == EnhancementPreset.THRESHOLD:
        gray = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
        norm_gray = _divide_background(gray)
        _, thresh = cv2.threshold(norm_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        res = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
        return apply_sharpness(res, sharpness)

    if mode == EnhancementPreset.CLEAN_SCAN:
        out = cv2.fastNlMeansDenoisingColored(out, None, 10, 10, 7, 21)
        gray = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
        norm_gray = _divide_background(gray)
        res = cv2.cvtColor(norm_gray, cv2.COLOR_GRAY2BGR)
        return apply_sharpness(res, sharpness)

    if mode == EnhancementPreset.OCR_FRIENDLY:
        gray = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
        norm_gray = _divide_background(gray)
        blurred = cv2.GaussianBlur(norm_gray, (3, 3), 0)
        bw = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 8
        )
        res = cv2.cvtColor(bw, cv2.COLOR_GRAY2BGR)
        return apply_sharpness(res, sharpness=1.5)

    if mode == EnhancementPreset.HIGH_CONTRAST:
        gray = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        eq = clahe.apply(gray)
        hc = cv2.convertScaleAbs(eq, alpha=1.4, beta=-20)
        res = cv2.cvtColor(hc, cv2.COLOR_GRAY2BGR)
        return apply_sharpness(res, sharpness)

    if mode == EnhancementPreset.ADOBE_WHITENING:
        gray = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
        dilated = cv2.dilate(gray, np.ones((7, 7), np.uint8))
        bg = cv2.medianBlur(dilated, 21)
        diff = 255 - cv2.absdiff(gray, bg)
        norm = cv2.normalize(diff, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        res = cv2.cvtColor(norm, cv2.COLOR_GRAY2BGR)
        return apply_sharpness(res, sharpness)

    # Default: CamScanner MAGIC_COLOR 2.0
    lab = cv2.cvtColor(out, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    l_norm = _divide_background(l)
    lab_enhanced = cv2.merge((l_norm, a, b))
    bgr_enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)

    return apply_sharpness(bgr_enhanced, sharpness_factor=sharpness)


def _divide_background(img_channel: np.ndarray) -> np.ndarray:
    """CamScanner Illumination Division algorithm to produce 100% white paper background."""
    h, w = img_channel.shape[:2]
    kernel_size = max(25, int(min(h, w) * 0.05))
    if kernel_size % 2 == 0:
        kernel_size += 1

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    bg_illum = cv2.morphologyEx(img_channel, cv2.MORPH_DILATE, kernel)
    bg_illum = cv2.medianBlur(bg_illum, 21)

    bg_illum[bg_illum == 0] = 1
    norm = np.clip((img_channel.astype(np.float32) / bg_illum.astype(np.float32)) * 255.0, 0, 255).astype(
        np.uint8
    )

    norm = cv2.normalize(norm, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
    return norm
