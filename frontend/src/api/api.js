import axios from 'axios';
import { saveAs } from 'file-saver';

// Use environment variable for the API URL, with a fallback for local dev
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
    baseURL: `${API_URL}/api`,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const uploadProfile = async (file, token) => {
    const formData = new FormData();
    formData.append('file', file);

    const headers = {
        'Content-Type': 'multipart/form-data',
    };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await apiClient.post('/upload', formData, {
        headers,
    });
    return response.data;
};

export const getProfiles = async (search = '') => {
    const params = new URLSearchParams();
    if (search) {
        params.append('search', search);
    }
    const response = await apiClient.get(`/?${params.toString()}`);
    return response.data;
};

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
