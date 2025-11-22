import React from 'react';
import './Navbar.css';

const Navbar = ({ user, onLogout }) => {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-logo">
          <span className="logo-icon">🌍</span>
          <span className="logo-text">MyTraveller</span>
        </div>
        
        {user && (
          <div className="navbar-user">
            <div className="user-info">
              <span className="user-greeting">Hello, {user.username}!</span>
              <span className="user-email">{user.email}</span>
            </div>
            <button onClick={onLogout} className="btn-logout">
              Logout
            </button>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
