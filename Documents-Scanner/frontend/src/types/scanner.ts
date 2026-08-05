export type Point = [number, number]; // [x, y]

export interface CornerDetectionResult {
  width: number;
  height: number;
  preview_width: number;
  preview_height: number;
  corners: Point[];
  corners_preview: Point[];
  is_fallback: boolean;
  overlay_base64: string;
}

export interface ScanProcessResult {
  scan_id: string;
  filename: string;
  enhanced_base64: string;
  original_base64: string;
  warped_base64: string;
  overlay_base64: string;
  used_fallback: boolean;
  width: number;
  height: number;
}

export interface ScanHistoryRecord {
  id: string;
  filename: string;
  original_name: string;
  timestamp: number;
  mode: string;
  width: number;
  height: number;
}

export type EnhancementMode =
  | 'magic_color'
  | 'adobe_whitening'
  | 'black_and_white'
  | 'grayscale'
  | 'original_clean'
  | 'threshold'
  | 'clean_scan'
  | 'ocr_friendly'
  | 'high_contrast';

export interface ScanParameters {
  rotation_angle: number;
  flip_mode: 'none' | 'horizontal' | 'vertical' | 'both';
  enhancement_mode: EnhancementMode;
  brightness: number;
  contrast: number;
  sharpness: number;
  warmth: number;
  custom_name?: string;
}
