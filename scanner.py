"""
scanner.py
==========

Main orchestration pipeline for the CamScanner & Adobe Scan Pro Document Scanner.

Wires together preprocessing, edge/contour-based document detection,
perspective transformation, rotation, fine-tuning, enhancement, saving, and PDF generation.

Part of the Devsil Document Scanner project.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import List, Optional, Union

import cv2
import numpy as np

from utils.image_utils import (
    draw_contour_overlay,
    export_images_to_pdf,
    read_image_from_source,
    save_image as save_img_util,
)
from utils.processing_utils import (
    EnhancementPreset,
    adjust_color_temperature,
    apply_sharpness,
    enhance_document,
    find_document_corners,
    flip_image,
    four_point_transform,
    order_points,
    preprocess_image as preprocess_img_util,
    rotate_image,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


class ScannerError(Exception):
    """Top-level exception for unrecoverable scanning failures."""


@dataclass
class ScanResult:
    """Container for everything produced by a single scan run."""

    original: np.ndarray
    gray: np.ndarray
    blur: np.ndarray
    threshold: np.ndarray
    contour_overlay: np.ndarray
    warped: np.ndarray
    enhanced: np.ndarray
    saved_path: Optional[str] = None
    used_fallback: bool = False
    edges: Optional[np.ndarray] = None


class DocumentScanner:
    """
    High-level document scanner that automatically detects, corrects perspective,
    rotates, fine-tunes, and enhances documents to CamScanner & Adobe Scan quality.
    """

    def __init__(
        self,
        target_height: int = 800,
        enhancement_mode: Union[EnhancementPreset, str] = EnhancementPreset.MAGIC_COLOR,
        display: bool = False,
        output_dir: str = "dataset/output_images",
    ) -> None:
        self.target_height = target_height
        if isinstance(enhancement_mode, str):
            try:
                self.enhancement_mode = EnhancementPreset(enhancement_mode.lower())
            except ValueError:
                self.enhancement_mode = EnhancementPreset.MAGIC_COLOR
        else:
            self.enhancement_mode = enhancement_mode
        self.display = display
        self.output_dir = output_dir

    def scan(
        self,
        image_source: Union[str, np.ndarray, bytes],
        save_output: bool = True,
        enhancement_mode: Optional[Union[EnhancementPreset, str]] = None,
        manual_corners: Optional[np.ndarray] = None,
        rotation_angle: float = 0.0,
        flip_mode: Optional[str] = None,
        brightness: int = 0,
        contrast: float = 1.0,
        sharpness: float = 1.0,
        warmth: int = 0,
    ) -> ScanResult:
        """
        Run the full document scan pipeline with rotation, cropping, flipping, and fine-tuning.
        """
        mode = enhancement_mode or self.enhancement_mode
        if isinstance(mode, str):
            try:
                mode = EnhancementPreset(mode.lower())
            except ValueError:
                mode = EnhancementPreset.MAGIC_COLOR

        # 1. Load image
        try:
            original = read_image_from_source(image_source)
        except Exception as exc:
            logger.error("Failed to load image: %s", exc)
            raise ScannerError(f"Could not load image: {exc}") from exc

        # 2. Apply initial rotation / flip if requested before processing
        if rotation_angle != 0:
            original = rotate_image(original, rotation_angle)
        if flip_mode:
            original = flip_image(original, flip_mode)

        # 3. Preprocess
        prep = preprocess_img_util(original, target_height=self.target_height)

        # 4. Detect or apply manual corners
        used_fallback = False
        if manual_corners is not None and manual_corners.shape == (4, 2):
            corners = manual_corners
            ordered = True
        else:
            corners, used_fallback = find_document_corners(prep["edges"])
            ordered = False

        # 5. Contour overlay
        contour_overlay = draw_contour_overlay(prep["resized"], corners)

        # 6. Perspective Warp Transform
        full_res_corners = corners * prep["ratio"]
        warped = four_point_transform(original, full_res_corners, ordered=ordered)

        # 7. CamScanner Enhancement Filters + Fine Tuning Controls
        enhanced = enhance_document(
            warped,
            mode=mode,
            brightness=brightness,
            contrast=contrast,
            sharpness=sharpness,
            warmth=warmth,
        )

        # 8. Save output
        saved_path = None
        if save_output:
            if isinstance(image_source, str):
                base_name = os.path.basename(image_source)
            else:
                base_name = "scanned_doc.jpg"

            out_file = os.path.join(self.output_dir, f"scanned_{base_name}")
            try:
                saved_path = save_img_util(enhanced, out_file)
            except Exception as exc:
                logger.error("Failed to save scanned image: %s", exc)

        result = ScanResult(
            original=original,
            gray=prep["gray"],
            blur=prep["blur"],
            threshold=prep["threshold"],
            contour_overlay=contour_overlay,
            warped=warped,
            enhanced=enhanced,
            saved_path=saved_path,
            used_fallback=used_fallback,
            edges=prep["edges"],
        )

        if self.display:
            self._display_pipeline(result)

        return result

    def export_to_pdf(
        self,
        scan_results: List[ScanResult],
        output_pdf_path: str,
        page_format: str = "A4",
    ) -> str:
        """Export multiple scan results into a single multi-page PDF document."""
        images = [r.enhanced for r in scan_results]
        return export_images_to_pdf(images, output_pdf_path, page_format=page_format)

    @staticmethod
    def _display_pipeline(result: ScanResult) -> None:
        """OpenCV GUI windows display for local visual debugging."""
        windows = {
            "1 - Original": result.original,
            "2 - Gray": result.gray,
            "3 - Blur": result.blur,
            "4 - Threshold": result.threshold,
            "5 - Edges": result.edges,
            "6 - Detected Contour": result.contour_overlay,
            "7 - Warped Document": result.warped,
            "8 - Enhanced Scan": result.enhanced,
        }
        try:
            for name, img in windows.items():
                if img is not None:
                    cv2.imshow(name, img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        except Exception as exc:
            logger.warning("Display unavailable in this environment (%s). Skipping.", exc)
