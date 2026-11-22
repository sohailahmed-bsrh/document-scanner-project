import axios from 'axios';
import {
  CornerDetectionResult,
  Point,
  ScanHistoryRecord,
  ScanParameters,
  ScanProcessResult,
} from '../types/scanner';

const API_BASE_URL = '/api';

export const api = {
  healthCheck: async () => {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data;
  },

  detectCorners: async (file: File): Promise<CornerDetectionResult> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await axios.post<CornerDetectionResult>(
      `${API_BASE_URL}/scan/detect`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    );
    return response.data;
  },

  processScan: async (
    file: File,
    corners: Point[] | null,
    params: ScanParameters
  ): Promise<ScanProcessResult> => {
    const formData = new FormData();
    formData.append('file', file);
    if (corners) {
      formData.append('corners', JSON.stringify(corners));
    }
    formData.append('rotation_angle', params.rotation_angle.toString());
    formData.append('flip_mode', params.flip_mode);
    formData.append('enhancement_mode', params.enhancement_mode);
    formData.append('brightness', params.brightness.toString());
    formData.append('contrast', params.contrast.toString());
    formData.append('sharpness', params.sharpness.toString());
    formData.append('warmth', params.warmth.toString());
    if (params.custom_name) {
      formData.append('custom_name', params.custom_name);
    }

    const response = await axios.post<ScanProcessResult>(
      `${API_BASE_URL}/scan/process`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    );
    return response.data;
  },

  getHistory: async (): Promise<ScanHistoryRecord[]> => {
    const response = await axios.get<ScanHistoryRecord[]>(`${API_BASE_URL}/scans/history`);
    return response.data;
  },

  deleteHistoryItem: async (filename: string): Promise<void> => {
    await axios.delete(`${API_BASE_URL}/scans/history/${filename}`);
  },

  exportPdf: async (
    filenames: string[],
    outputName: string = 'scanned_document.pdf',
    pageFormat: string = 'A4'
  ): Promise<{ pdf_filename: string; download_url: string; page_count: number }> => {
    const response = await axios.post(`${API_BASE_URL}/export/pdf`, {
      filenames,
      output_name: outputName,
      page_format: pageFormat,
    });
    return response.data;
  },

  getSampleImages: async (): Promise<{ samples: string[] }> => {
    const response = await axios.get(`${API_BASE_URL}/samples`);
    return response.data;
  },
};
