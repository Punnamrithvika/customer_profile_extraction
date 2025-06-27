import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import ProfileUploader from './components/ProfileUploader';
import ProfileList from './components/ProfileList';
import { getProfiles } from './api/api';
import LoginPage from "./components/LoginPage";
import axios from "axios";
import { Route, Routes, useNavigate, Navigate } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
    const navigate = useNavigate();

    const [profiles, setProfiles] = useState([]);
    const [filteredProfiles, setFilteredProfiles] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [error, setError] = useState('');
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(null);

    const fetchProfiles = useCallback(async () => {
        try {
            setError('');
            const data = await getProfiles(searchTerm, token);
            setProfiles(data);
        } catch (err) {
            console.error("Failed to fetch profiles:", err);
            setError('Failed to fetch profiles. Please try again.');
        }
    }, [searchTerm, token]);

    useEffect(() => {
        const storedUser = localStorage.getItem("user");
        const storedToken = localStorage.getItem("token");
        if (storedUser && storedToken) {
            setUser(JSON.parse(storedUser));
            setToken(storedToken);
        }
    }, []);

    useEffect(() => {
        if (user) fetchProfiles();
    }, [fetchProfiles, user]);

    const handleUploadSuccess = () => {
        fetchProfiles();
    };

    const handleLogin = (userData) => {
        setUser(userData);
        setToken(userData.access_token);
        localStorage.setItem("user", JSON.stringify(userData));
        localStorage.setItem("token", userData.access_token);
        navigate("/home");
    };

    const handleLogout = () => {
        setUser(null);
        setToken(null);
        localStorage.removeItem("user");
        localStorage.removeItem("token");
        navigate("/login");
    };

    const handleSearch = ({ field, value }) => {
        if (!value) {
            setFilteredProfiles(profiles);
            return;
        }
        const val = value.toLowerCase();
        const filtered = profiles.filter(profile => {
            // Top-level fields
            if (["full_name", "email", "phone_number"].includes(field)) {
                return (profile[field] || "").toLowerCase().includes(val);
            }
            // Nested work_experience fields
            if (Array.isArray(profile.work_experience)) {
                return profile.work_experience.some(exp => {
                    // For skills_technologies (array of strings)
                    if (field === "skills_technologies") {
                        return Array.isArray(exp.skills_technologies) &&
                            exp.skills_technologies.some(skill =>
                                (skill || "").toLowerCase().includes(val)
                            );
                    }
                    // Other fields (string)
                    return (exp[field] || "").toLowerCase().includes(val);
                });
            }
            return false;
        });
        setFilteredProfiles(filtered);
    };

    // Show filtered or all profiles
    const profilesToShow = filteredProfiles.length > 0 || error ? filteredProfiles : profiles;

    const AddUserPage = () => {
        const [email, setEmail] = useState("");
        const [password, setPassword] = useState("");
        const [isAdmin, setIsAdmin] = useState(false);
        const [formError, setFormError] = useState("");
        const [formSuccess, setFormSuccess] = useState("");

        const handleSubmit = async (e) => {
            e.preventDefault();
            setFormError("");
            setFormSuccess("");
            try {
                const response = await axios.post(
                    "/api/users/",
                    { email, password, is_admin: isAdmin },
                    { headers: { Authorization: `Bearer ${token}` } }
                );
                setFormSuccess("User created successfully!");
                setEmail("");
                setPassword("");
                setIsAdmin(false);
            } catch (err) {
                setFormError(
                    err.response?.data?.detail || "Failed to create user."
                );
            }
        };

        return (
            <div className="login-page-center">
                <div className="login-container">
                    <h2>Add Admin/User</h2>
                    <form className="login-form" onSubmit={handleSubmit}>
                        <div>
                            <label>Email:</label>
                            <input
                                type="email"
                                value={email}
                                onChange={e => setEmail(e.target.value)}
                                required
                            />
                        </div>
                        <div>
                            <label>Password:</label>
                            <input
                                type="password"
                                value={password}
                                onChange={e => setPassword(e.target.value)}
                                required
                            />
                        </div>
                        <div>
                            <label>
                                <input
                                    type="checkbox"
                                    checked={isAdmin}
                                    onChange={e => setIsAdmin(e.target.checked)}
                                />
                                Is Admin
                            </label>
                        </div>
                        <button type="submit">Add User</button>
                        <button type="button" onClick={() => navigate(-1)} style={{ marginLeft: 8 }}>
                            Back
                        </button>
                        {formError && <div style={{ color: "red" }}>{formError}</div>}
                        {formSuccess && <div style={{ color: "green" }}>{formSuccess}</div>}
                    </form>
                </div>
            </div>
        );
    };

    useEffect(() => {
        const clearSession = () => {
            localStorage.removeItem("user");
            localStorage.removeItem("token");
        };
        window.addEventListener("unload", clearSession);
        return () => window.removeEventListener("unload", clearSession);
    }, []);

    return (
        <>
            <header className="App-header">
                <h1>Customer Profile Extractor</h1>
                {user && (
                    <div className="header-btn-group">
                        {user.is_admin && (
                            <button
                                className="header-users-btn"
                                onClick={() => navigate("/add-user")}
                            >
                                Add Users
                            </button>
                        )}
                        <button
                            className="header-users-btn"
                            onClick={handleLogout}
                        >
                            Logout
                        </button>
                    </div>
                )}
                
                {user && (
                    <span style={{ position: "absolute", right: 32, bottom: 8, fontSize: "1rem" }}>
                        Logged in as: {user.email} ({user.is_admin ? "Admin" : "User"})
                    </span>
                )}
                
            </header>
            <Routes>
                <Route
                    path="/login"
                    element={
                        !user
                            ? <LoginPage onLogin={handleLogin} />
                            : <Navigate to="/home" replace />
                    }
                />
                <Route
                    path="/home"
                    element={
                        <ProtectedRoute user={user}>
                            <main>
                                {user && user.is_admin && (
                                    <div className="upload-container">
                                        <ProfileUploader onUploadSuccess={handleUploadSuccess} token={token} />
                                    </div>
                                )}
                                <ProfileList
                                    profiles={profilesToShow}
                                    onSearch={handleSearch}
                                    error={error}
                                />
                            </main>
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/add-user"
                    element={
                        <ProtectedRoute user={user}>
                            <AddUserPage />
                        </ProtectedRoute>
                    }
                />
                {/* Redirect root to /login */}
                <Route path="/" element={<Navigate to="/login" replace />} />
            </Routes>
        </>
    );
}

export default App;
