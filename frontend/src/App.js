import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import ProfileUploader from './components/ProfileUploader';
import ProfileList from './components/ProfileList';
import { getProfiles } from './api/api';
import ResumeDisplay from "./components/ResumeDisplay";
import LoginPage from "./components/LoginPage";

function App() {
    const [profiles, setProfiles] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [error, setError] = useState('');
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(null); // <-- Add this

    const fetchProfiles = useCallback(async () => {
        try {
            setError('');
            const data = await getProfiles(searchTerm, token); // Pass token if needed
            setProfiles(data);
        } catch (err) {
            console.error("Failed to fetch profiles:", err);
            setError('Failed to fetch profiles. Please try again.');
        }
    }, [searchTerm, token]);

    useEffect(() => {
        if (user) fetchProfiles();
    }, [fetchProfiles, user]);

    const handleUploadSuccess = () => {
        fetchProfiles();
    };

    const handleLogin = (userData) => {
        setUser(userData);
        setToken(userData.access_token); // <-- Save token
    };

    const handleSearch = async (searchTerm) => {
        try {
            const result = await getProfiles(searchTerm);
            setProfiles(result);
            setError("");
        } catch (err) {
            setError("Failed to fetch profiles.");
        }
    };

    if (!user) {
        return <LoginPage onLogin={handleLogin} />;
    }

    return (
        <div className="App">
            <header className="App-header">
                <h1>Customer Profile Extractor</h1>
                <span style={{float: "right"}}>Logged in as: {user.email} ({user.is_admin ? "Admin" : "User"})</span>
            </header>
            <main>
                {user.is_admin && (
                    <>
                        <ProfileUploader onUploadSuccess={handleUploadSuccess} token={token} /> {/* Pass token */}
                    </>
                )}
                <ProfileList
                    profiles={profiles}
                    onSearch={handleSearch}
                    error={error}
                />
            </main>
        </div>
    );
}

export default App;
