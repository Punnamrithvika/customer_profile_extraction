import React, { useState } from 'react';
import { uploadProfiles } from '../api/api';

const ProfileUploader = ({ onUploadSuccess, token }) => {
    const [files, setFiles] = useState([]);
    const [messages, setMessages] = useState([]);
    const [errors, setErrors] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    const handleFileChange = (e) => {
        setFiles(Array.from(e.target.files)); // Convert FileList to array
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (files.length === 0) {
            setErrors(['Please select one or more resume files to upload.']);
            return;
        }

        setIsLoading(true);
        setMessages([]);
        setErrors([]);

        try {
            console.log("Uploading files:", files);
            console.log("Token being sent:", token);
            const result = await uploadProfiles(files, token); // Send all files at once
            console.log("Upload result:", result);
            setMessages(result.results.map(r => `✅ ${r.filename} uploaded successfully.`));
            setErrors(result.errors.map(e => `❌ ${e}`));
            if (onUploadSuccess) onUploadSuccess();
        } catch (err) {
            console.error("Upload error:", err);
            const errorMessage = err.response?.data?.detail || 'An error occurred.';
            setErrors([`❌ Upload failed: ${errorMessage}`]);
            setMessages([]);
        } finally {
            setIsLoading(false);
            setFiles([]);
            e.target.reset();
        }
    };

    return (
        <div className="uploader-container">
            <h2>Upload Resumes</h2>
            <p>Supported formats: PDF, DOCX</p>
            <form onSubmit={handleSubmit}>
                <input
                    type="file"
                    multiple
                    onChange={handleFileChange}
                    accept=".pdf,.docx,.doc"
                    disabled={isLoading}
                />
                <button type="submit" disabled={files.length === 0 || isLoading}>
                    {isLoading ? 'Uploading...' : 'Upload All'}
                </button>
            </form>

            {messages.length > 0 && (
                <div className="message success">
                    {messages.map((msg, i) => <p key={i}>{msg}</p>)}
                </div>
            )}

            {errors.length > 0 && (
                <div className="message error">
                    {errors.map((err, i) => <p key={i}>{err}</p>)}
                </div>
            )}
        </div>
    );
};

export default ProfileUploader;
