#!/usr/bin/env python3
"""
app.py
======

CamScanner & Adobe Scan Pro Studio - FastAPI Backend API Server.

Provides RESTful endpoints for:
- Auto document boundary & corner detection
- Manual corner cropping, perspective transform, rotation, flip & fine-tuning
- CamScanner & Adobe Scan enhancement filters (Magic Color, B&W, Clean Scan, OCR, etc.)
- Multi-page PDF generation & download
- Scan history management and sample dataset serving

Part of the Devsil Document Scanner Application.
"""

from __future__ import annotations

import base64
import json
import logging
import os
import time
import uuid
from typing import List, Optional, Union

import cv2
import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from scanner import DocumentScanner, ScannerError
from utils.image_utils import (
    bgr_to_pil,
    bgr_to_rgb,
    draw_contour_overlay,
    export_images_to_pdf,
    read_image_from_source,
    save_image,
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
    preprocess_image,
    rotate_image,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Basirah Document Scanner API",
    description="Production-grade API comparable to CamScanner, Adobe Scan, and Microsoft Lens.",
    version="2.0.0",
)

# Enable CORS for React Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = os.path.join("dataset", "output_images")
INPUT_DIR = os.path.join("dataset", "input_images")
HISTORY_FILE = os.path.join("dataset", "history.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(INPUT_DIR, exist_ok=True)

scanner_engine = DocumentScanner(output_dir=OUTPUT_DIR)


def load_history() -> List[dict]:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            logger.error("Failed to read history log: %s", exc)
    return []


def save_history(records: List[dict]) -> None:
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)
    except Exception as exc:
        logger.error("Failed to save history log: %s", exc)


def mat_to_base64(mat: np.ndarray, ext: str = ".jpg") -> str:
    success, buffer = cv2.imencode(ext, mat)
    if not success:
        raise ValueError("Failed to encode image to buffer")
    return f"data:image/{ext.replace('.', '')};base64," + base64.b64encode(buffer).decode("utf-8")


@app.get("/")
def read_root():
    static_file = os.path.join("static", "index.html")
    if os.path.exists(static_file):
        return FileResponse(static_file, media_type="text/html")
    return {"message": "Basirah Document Scanner API is running."}


@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "app": "Basirah Document Scanner Studio",
        "version": "2.0.0",
        "timestamp": time.time(),
    }


@app.post("/api/scan/detect")
async def detect_corners(file: UploadFile = File(...)):
    """Auto-detect document boundaries & 4 corner points."""
    try:
        contents = await file.read()
        image = read_image_from_source(contents)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image file: {str(exc)}",
        )

    h, w = image.shape[:2]
    prep = preprocess_image(image, target_height=800)
    auto_corners, is_fallback = find_document_corners(prep["edges"])
    overlay = draw_contour_overlay(prep["resized"], auto_corners)

    # Scale corners back to original image dimensions
    ratio = prep["ratio"]
    scaled_corners = (auto_corners * ratio).tolist()

    return {
        "width": w,
        "height": h,
        "preview_width": prep["resized"].shape[1],
        "preview_height": prep["resized"].shape[0],
        "corners": scaled_corners,
        "corners_preview": auto_corners.tolist(),
        "is_fallback": is_fallback,
        "overlay_base64": mat_to_base64(overlay),
    }


@app.post("/api/scan/process")
async def process_scan(
    file: UploadFile = File(...),
    corners: Optional[str] = Form(None),  # JSON array string of 4 points [[x,y],...]
    rotation_angle: float = Form(0.0),
    flip_mode: Optional[str] = Form(None),
    enhancement_mode: str = Form("magic_color"),
    brightness: int = Form(0),
    contrast: float = Form(1.0),
    sharpness: float = Form(1.0),
    warmth: int = Form(0),
    save_to_history: bool = Form(True),
    custom_name: Optional[str] = Form(None),
):
    """Run full scan pipeline with perspective correction, cropping, rotation, flip, and enhancement."""
    try:
        contents = await file.read()
        image = read_image_from_source(contents)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image file: {str(exc)}",
        )

    parsed_corners = None
    if corners:
        try:
            pts = np.array(json.loads(corners), dtype=np.float32)
            if pts.shape == (4, 2):
                parsed_corners = pts
        except Exception as exc:
            logger.warning("Could not parse corners JSON (%s), auto-detecting.", exc)

    try:
        result = scanner_engine.scan(
            image_source=image,
            save_output=False,
            enhancement_mode=enhancement_mode,
            manual_corners=parsed_corners,
            rotation_angle=rotation_angle,
            flip_mode=flip_mode,
            brightness=brightness,
            contrast=contrast,
            sharpness=sharpness,
            warmth=warmth,
        )
    except ScannerError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    scan_id = str(uuid.uuid4())[:8]
    filename_base = custom_name.strip() if custom_name and custom_name.strip() else file.filename or "scan.jpg"
    if not filename_base.lower().endswith((".jpg", ".jpeg", ".png")):
        filename_base += ".jpg"

    saved_filename = f"{scan_id}_{filename_base}"
    saved_path = os.path.join(OUTPUT_DIR, saved_filename)
    save_image(result.enhanced, saved_path)

    # Save metadata into history log
    if save_to_history:
        history = load_history()
        history.insert(
            0,
            {
                "id": scan_id,
                "filename": saved_filename,
                "original_name": file.filename,
                "timestamp": time.time(),
                "mode": enhancement_mode,
                "width": result.enhanced.shape[1],
                "height": result.enhanced.shape[0],
            },
        )
        save_history(history)

    return {
        "scan_id": scan_id,
        "filename": saved_filename,
        "enhanced_base64": mat_to_base64(result.enhanced),
        "original_base64": mat_to_base64(result.original),
        "warped_base64": mat_to_base64(result.warped),
        "overlay_base64": mat_to_base64(result.contour_overlay),
        "used_fallback": result.used_fallback,
        "width": result.enhanced.shape[1],
        "height": result.enhanced.shape[0],
    }


class PDFExportRequest(BaseModel):
    filenames: List[str]
    output_name: Optional[str] = "scanned_document.pdf"
    page_format: str = Field(default="A4", description="A4, Letter, or Auto")


@app.post("/api/export/pdf")
async def export_pdf(payload: PDFExportRequest):
    """Combine saved scan images into a single multi-page PDF document."""
    if not payload.filenames:
        raise HTTPException(status_code=400, detail="No filenames provided.")

    images = []
    for fname in payload.filenames:
        path = os.path.join(OUTPUT_DIR, fname)
        if not os.path.exists(path):
            # Try input directory as fallback
            path = os.path.join(INPUT_DIR, fname)
        if os.path.exists(path):
            img = read_image_from_source(path)
            images.append(img)

    if not images:
        raise HTTPException(status_code=404, detail="None of the specified scan files were found.")

    out_name = payload.output_name if payload.output_name.endswith(".pdf") else f"{payload.output_name}.pdf"
    pdf_filename = f"export_{str(uuid.uuid4())[:6]}_{out_name}"
    pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)

    try:
        export_images_to_pdf(images, pdf_path, page_format=payload.page_format)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(exc)}")

    return {
        "pdf_filename": pdf_filename,
        "download_url": f"/api/scans/file/{pdf_filename}",
        "page_count": len(images),
    }


@app.get("/api/scans/history")
def get_history():
    """Retrieve saved scans history list."""
    history = load_history()
    valid_records = []
    for rec in history:
        fname = rec.get("filename")
        if fname and os.path.exists(os.path.join(OUTPUT_DIR, fname)):
            valid_records.append(rec)
    return valid_records


@app.delete("/api/scans/history/{filename}")
def delete_history_item(filename: str):
    """Delete scan from history and disk."""
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    history = load_history()
    updated = [r for r in history if r.get("filename") != filename]
    save_history(updated)
    return {"message": "Scan deleted successfully.", "filename": filename}


@app.get("/api/scans/file/{filename}")
def get_scan_file(filename: str):
    """Serve image or PDF file from output directory."""
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        path = os.path.join(INPUT_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    media_type = "image/jpeg"
    if filename.lower().endswith(".pdf"):
        media_type = "application/pdf"
    elif filename.lower().endswith(".png"):
        media_type = "image/png"

    return FileResponse(path, media_type=media_type, filename=filename)


@app.get("/api/samples")
def get_sample_images():
    """List available sample images from dataset/input_images."""
    files = []
    if os.path.exists(INPUT_DIR):
        for f in sorted(os.listdir(INPUT_DIR)):
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                files.append(f)
    return {"samples": files}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
