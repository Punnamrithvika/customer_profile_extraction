import React, { useState } from 'react';
import { exportProfiles } from '../api/api';

const ProfileList = ({ profiles, onSearch, error }) => {
    const [inputValue, setInputValue] = useState("");

    const handleExport = async () => {
        try {
            await exportProfiles(inputValue);
        } catch (err) {
            console.error('Failed to export profiles:', err);
            alert('Failed to export data.');
        }
    };

    // Call the search function when button is clicked
    const handleSearch = () => {
        // If input is empty, show all profiles
        onSearch(inputValue.trim());
    };

    // Optional: allow pressing Enter to trigger search
    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    };

    // Helper to format skills string into tags
    const renderSkills = (skills) => {
        if (!skills) return null;
        // Split by newlines and commas, trim, and filter out empty strings
        const skillList = skills
            .split(/\n|,/)
            .map(s => s.replace(/^•\s*/, '').trim())
            .filter(Boolean);
        return (
            <div className="skills">
                {skillList.map((skill, idx) => (
                    <span key={idx} className="skill-tag">{skill}</span>
                ))}
            </div>
        );
    };

    return (
        <div className="list-container profile-list-scroll">
            <h2>Candidate Database</h2>
            <div className="search-bar">
                <input
                    type="text"
                    placeholder="Search by name, email, or skill..."
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                />
                <button onClick={handleSearch}>Search</button>
                <button onClick={handleExport} disabled={profiles.length === 0}>Export as CSV</button>
            </div>

            {error && <p className="message error">{error}</p>}

            <div>
                <table className="profile-table">
                    <thead>
                        <tr>
                            <th>Name / Contact</th>
                            <th>Education</th>
                            <th>Experience</th>
                            <th>Skills</th>
                        </tr>
                    </thead>
                    <tbody>
                        {profiles.length > 0 ? (
                            profiles.map((profile) => (
                                <tr key={profile.id}>
                                    <td>
                                        <strong>{profile.name || 'N/A'}</strong>
                                        <div style={{ fontSize: "0.95em", marginTop: "0.3em" }}>
                                            <div><strong>Email:</strong> {profile.contact?.email || 'N/A'}</div>
                                            <div><strong>Phone:</strong> {profile.contact?.phone || 'N/A'}</div>
                                        </div>
                                    </td>
                                    <td>
                                        {Array.isArray(profile.education) && profile.education.length > 0 ? (
                                            <ul>
                                                {profile.education.map((edu, idx) => (
                                                    <li key={idx}>
                                                        <strong>{edu.institution}</strong><br />
                                                        {edu.degree}<br />
                                                        {edu.date}
                                                    </li>
                                                ))}
                                            </ul>
                                        ) : 'N/A'}
                                    </td>
                                    <td>
                                        {Array.isArray(profile.experience) && profile.experience.length > 0 ? (
                                            <ul>
                                                {profile.experience.map((exp, idx) => (
                                                    <li key={idx}>
                                                        <strong>{exp.customer}</strong> - {exp.role}<br />
                                                        {exp.project_dates}<br />
                                                        {exp.technology && exp.technology.length > 0 && (
                                                            <span>
                                                                <em>Tech:</em> {exp.technology.join(', ')}
                                                            </span>
                                                        )}
                                                    </li>
                                                ))}
                                            </ul>
                                        ) : 'N/A'}
                                    </td>
                                    <td>
                                        {renderSkills(profile.skills)}
                                    </td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan="4">No profiles found.</td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default ProfileList;
