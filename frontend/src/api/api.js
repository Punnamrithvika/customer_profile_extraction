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

// ✅ Modified: Upload multiple profiles (folder of resumes)
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
    console.log("Headers being sent:", headers);

    try {
        const response = await apiClient.post('/upload-multiple', formData, { headers });
        console.log("API response:", response);
        return response.data;
    } catch (err) {
        console.error("API error:", err);
        throw err;
    }
};

// ✅ Unchanged: Get all parsed profiles with optional search
export const getProfiles = async (search = '') => {
    const params = new URLSearchParams();
    if (search) {
        params.append('search', search);
    }
    const response = await apiClient.get(`/?${params.toString()}`);
    return response.data;
};

// ✅ Unchanged: Export CSV of profiles
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
