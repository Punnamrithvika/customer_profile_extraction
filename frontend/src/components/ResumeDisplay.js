import React, { useEffect, useState } from "react";
import axios from "axios";

const ResumeDisplay = () => {
    const [resumes, setResumes] = useState([]);

    useEffect(() => {
        axios.get("/api/resumes")
            .then(response => setResumes(response.data))
            .catch(error => console.error("Error fetching resumes:", error));
    }, []);

    return (
        <div className="resume-display-scroll">
            <h3>Saved Resumes</h3>
            <table className="resume-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Mobile</th>
                    </tr>
                </thead>
                <tbody>
                    {resumes.map((resume, idx) => (
                        <tr key={idx}>
                            <td>{resume.name || "N/A"}</td>
                            <td>{resume.contact?.email || "N/A"}</td>
                            <td>{resume.contact?.phone || "N/A"}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default ResumeDisplay;
