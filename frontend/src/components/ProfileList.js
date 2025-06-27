import React, { useState } from 'react';
import { exportToCsv } from '../utils/exportToCsv';

const SEARCH_FIELDS = [
    { value: 'full_name', label: 'Full Name' },
    { value: 'email', label: 'Email' },
    { value: 'phone_number', label: 'Phone Number' },
    { value: 'company_name', label: 'Company Name' },
    { value: 'customer_name', label: 'Customer Name' },
    { value: 'role', label: 'Role' },
    { value: 'duration', label: 'Duration' },
    { value: 'skills_technologies', label: 'Skills/Technologies' },
    { value: 'industry_domain', label: 'Industry/Domain' },
    { value: 'location', label: 'Location' },
];

const ProfileList = ({ profiles, onSearch, error }) => {
    const [inputValue, setInputValue] = useState("");
    const [searchField, setSearchField] = useState("full_name");

    const handleExport = () => {
        exportToCsv(profiles, "resume_export");
    };

    const handleSearch = () => {
        onSearch({ field: searchField, value: inputValue.trim() });
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    };

    return (
        <div className="list-container profile-list-scroll">
            <h2>Candidate Database</h2>
            <div className="search-bar" style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                <select
                    value={searchField}
                    onChange={e => setSearchField(e.target.value)}
                    style={{ height: "2.2rem", fontSize: "1rem" }}
                >
                    {SEARCH_FIELDS.map(opt => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                </select>
                <input
                    type="text"
                    placeholder={`Search by ${SEARCH_FIELDS.find(f => f.value === searchField).label.toLowerCase()}...`}
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    style={{ flex: 1 }}
                />
                <button onClick={handleSearch}>Search</button>
                <button onClick={handleExport} disabled={profiles.length === 0}>Export as CSV</button>
            </div>

            {error && <p className="message error">{error}</p>}

            {profiles.length > 0 ? (
                profiles.map((profile, idx) => (
                    <div key={`${profile.email || ''}_${profile.phone_number || ''}_${idx}`} className="profile-card">
                        <div className="profile-header">
                            <div>
                                <strong>Full Name:</strong> {profile.full_name || 'N/A'}
                            </div>
                            <div>
                                <strong>Email:</strong> {profile.email || 'N/A'}
                            </div>
                            <div>
                                <strong>Phone Number:</strong> {profile.phone_number || 'N/A'}
                            </div>
                        </div>
                        <div className="work-exp-section">
                            <h4>Work Experience:</h4>
                            <div className="work-exp-grid">
                                {Array.isArray(profile.work_experience) && profile.work_experience.length > 0 ? (
                                    profile.work_experience.map((exp, wid) => (
                                        <div key={wid} className="work-exp-card">
                                            <div className="work-exp-title">
                                                <strong>{exp.role || 'N/A'}</strong>
                                                {exp.company_name ? <> at <span>{exp.company_name}</span></> : null}
                                            </div>
                                            <div className="work-exp-details">
                                                <div><strong>Client/Customer:</strong> {exp.customer_name || 'N/A'}</div>
                                                <div><strong>Duration:</strong> {exp.duration || 'N/A'}</div>
                                                <div><strong>Industry/Domain:</strong> {exp.industry_domain || 'N/A'}</div>
                                                <div><strong>Location:</strong> {exp.location || 'N/A'}</div>
                                                <div>
                                                    <strong>Skills/Technologies:</strong>
                                                    <div className="skills-list">
                                                        {Array.isArray(exp.skills_technologies) && exp.skills_technologies.length > 0
                                                            ? exp.skills_technologies.map((skill, sid) => (
                                                                <span key={sid} className="skill-tag">{skill}</span>
                                                            ))
                                                            : <span className="skill-tag">N/A</span>
                                                        }
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    ))
                                ) : (
                                    <div>No work experience</div>
                                )}
                            </div>
                        </div>
                    </div>
                ))
            ) : (
                <div style={{ textAlign: "center", marginTop: "2rem" }}>No profiles found.</div>
            )}
        </div>
    );
};

export default ProfileList;
