import React from 'react';
import { useAuth } from '../../context/AuthContext';
import './Dashboard.css';

const Dashboard = () => {
  const { user } = useAuth();

  const stats = [
    { icon: '🗺️', label: 'Trips Planned', value: '0', color: '#667eea' },
    { icon: '📍', label: 'Places Saved', value: '0', color: '#f093fb' },
    { icon: '✈️', label: 'Countries', value: '0', color: '#4facfe' },
    { icon: '⭐', label: 'Reviews', value: '0', color: '#f5576c' }
  ];

  const quickActions = [
    { icon: '🎯', title: 'Plan New Trip', desc: 'Start planning your next adventure' },
    { icon: '🔍', title: 'Explore', desc: 'Discover amazing destinations' },
    { icon: '💾', title: 'Saved Places', desc: 'View your favorite spots' },
    { icon: '⚙️', title: 'Settings', desc: 'Manage your preferences' }
  ];

  return (
    <div className="dashboard-container fade-in">
      <div className="dashboard-content">
        <div className="welcome-section slide-up">
          <div className="welcome-header">
            <div className="welcome-icon float">🌟</div>
            <div>
              <h1>Welcome back, {user?.username || 'Traveller'}!</h1>
              <p>Ready to plan your next adventure?</p>
            </div>
          </div>
          
          <div className="user-badge">
            <span className="badge-icon">👤</span>
            <div className="badge-info">
              <span className="badge-name">{user?.fullName || user?.username}</span>
              <span className="badge-email">{user?.email}</span>
            </div>
          </div>
        </div>

        <div className="stats-grid">
          {stats.map((stat, index) => (
            <div 
              key={index} 
              className="stat-card scale-in"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="stat-icon" style={{ background: stat.color }}>
                {stat.icon}
              </div>
              <div className="stat-content">
                <div className="stat-value">{stat.value}</div>
                <div className="stat-label">{stat.label}</div>
              </div>
            </div>
          ))}
        </div>

        <div className="actions-section">
          <h2>Quick Actions</h2>
          <div className="actions-grid">
            {quickActions.map((action, index) => (
              <div 
                key={index} 
                className="action-card scale-in"
                style={{ animationDelay: `${index * 0.1 + 0.4}s` }}
              >
                <div className="action-icon">{action.icon}</div>
                <h3>{action.title}</h3>
                <p>{action.desc}</p>
                <button className="action-btn">Get Started</button>
              </div>
            ))}
          </div>
        </div>

        <div className="info-banner slide-up">
          <div className="banner-icon">🎉</div>
          <div className="banner-content">
            <h3>Authentication Complete!</h3>
            <p>You've successfully logged in with GraphQL. Your travel planning features are coming soon!</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
