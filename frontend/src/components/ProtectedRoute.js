import React from "react";
import { Navigate } from "react-router-dom";

const ProtectedRoute = ({ user, children }) => {
    if (!user || !user.access_token) {
        return <Navigate to="/login" replace />;
    }
    return children;
};

export default ProtectedRoute;