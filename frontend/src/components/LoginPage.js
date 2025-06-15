import React, { useState } from "react";
import logo from "../assets/logo.png"; // Adjust path if needed
import "../App.css"; // Uses the styles from App.css

const LoginPage = ({ onLogin }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (!email || !password) {
      setError("Please fill in both fields.");
      return;
    }
    try {
      const res = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) {
        setError("Invalid credentials");
        return;
      }
      const data = await res.json();
      onLogin(data);
    } catch {
      setError("Login failed. Please try again.");
    }
  };

  // Wrap the login container
  return (
    <div className="login-page-center">
      <div className="login-container">
        <div className="login-logo">
          <img
            src={logo}
            alt="Pi-Square Logo"
            style={{
              maxWidth: 180,
              height: "auto",
              display: "block",
              margin: "0 auto 1.5rem auto",
            }}
          />
        </div>
        <h2>Login</h2>
        <form onSubmit={handleSubmit}>
          <label>Email:</label>
          <input
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <label>Password:</label>
          <input
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button type="submit">Login</button>
          {error && <p className="message error">{error}</p>}
        </form>
      </div>
    </div>
  );
};

export default LoginPage;