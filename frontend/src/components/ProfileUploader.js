import React, { useState } from 'react';
import { uploadProfile } from '../api/api';

const ProfileUploader = ({ onUploadSuccess, token }) => { // <-- Accept token
    const [file, setFile] = useState(null);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file) {
            setError('Please select a file to upload.');
            return;
        }

        setIsLoading(true);
        setMessage('');
        setError('');

        try {
            const uploadedProfile = await uploadProfile(file, token); // <-- Pass token
            setMessage(`Successfully uploaded profile for ${uploadedProfile.name}!`);
            onUploadSuccess(); // Notify parent component
        } catch (err) {
            const errorMessage = err.response?.data?.detail || 'An unexpected error occurred.';
            setError(`Upload failed: ${errorMessage}`);
            console.error(err);
        } finally {
            setIsLoading(false);
            setFile(null); // Reset file input
            e.target.reset();
        }
    };

    return (
        <div className="uploader-container">
            <h2>Upload Resume</h2>
            <p>Supported formats: PDF, DOCX</p>
            <form onSubmit={handleSubmit}>
                <input type="file" onChange={handleFileChange} accept=".pdf,.docx" disabled={isLoading} />
                <button type="submit" disabled={!file || isLoading}>
                    {isLoading ? 'Uploading...' : 'Upload & Process'}
                </button>
            </form>
            {message && <p className="message success">{message}</p>}
            {error && <p className="message error">{error}</p>}
        </div>
    );
};

export default ProfileUploader;
