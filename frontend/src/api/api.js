import axios from 'axios';
import { saveAs } from 'file-saver';

// Use environment variable for the API URL, fallback to localhost
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Use relative path for Docker/Nginx proxying
const apiClient = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Upload multiple profiles (folder of resumes)
export const uploadProfiles = async (files, token) => {
    const formData = new FormData();
    files.forEach(file => {
        formData.append('files', file);
    });

    const headers = {
        'Content-Type': 'multipart/form-data',
    };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await apiClient.post('/upload-multiple', formData, { headers });
    return response.data;
};

// Get all parsed profiles with optional search
export const getProfiles = async (search = '') => {
    const params = new URLSearchParams();
    if (search) {
        params.append('search', search);
    }
    const response = await apiClient.get(`/?${params.toString()}`);
    return response.data;
};

// Export CSV of profiles
export const exportProfiles = async (search = '') => {
    const params = new URLSearchParams();
    if (search) {
        params.append('search', search);
    }
    const response = await apiClient.get(`/export-csv?${params.toString()}`, {
        responseType: 'blob',
    });
    saveAs(response.data, 'profiles.csv');
};
