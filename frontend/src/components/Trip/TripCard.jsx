import React, { useState } from 'react';
import { useMutation } from '@apollo/client';
import { DELETE_TRIP } from '../../graphql/mutations';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import './TripCard.css';

const TripCard = ({ trip, index, onUpdate }) => {
    const { token } = useAuth();
    const navigate = useNavigate();
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [deleteTrip, { loading: deleting }] = useMutation(DELETE_TRIP);

    const handleDelete = async () => {
        try {
            await deleteTrip({
                variables: { token, tripId: trip.id }
            });
            onUpdate();
        } catch (error) {
            console.error('Delete failed:', error);
            alert('Failed to delete trip');
        }
    };

    const getStatusColor = (status) => {
        const colors = {
            PLANNING: '#667eea',
            CONFIRMED: '#4facfe',
            ONGOING: '#f093fb',
            COMPLETED: '#43e97b',
            CANCELLED: '#f5576c'
        };
        return colors[status] || '#667eea';
    };

    const getBudgetIcon = (level) => {
        const icons = {
            BUDGET: '💰',
            MODERATE: '💰💰',
            LUXURY: '💰💰💰'
        };
        return icons[level] || '💰';
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    };

    const getDuration = () => {
        const start = new Date(trip.startDate);
        const end = new Date(trip.endDate);
        const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1;
        return `${days} day${days > 1 ? 's' : ''}`;
    };

    return (
        <div
            className="trip-card scale-in"
            style={{ animationDelay: `${index * 0.1}s` }}
        >
            <div className="trip-card-image">
                <div className="trip-image-placeholder">
                    <span className="trip-emoji">🌍</span>
                </div>
                <div
                    className="trip-status-badge"
                    style={{ background: getStatusColor(trip.status) }}
                >
                    {trip.status}
                </div>
            </div>

            <div className="trip-card-content">
                <h3 className="trip-destination">{trip.destination}</h3>

                <div className="trip-dates">
                    <span className="date-icon">📅</span>
                    <span>{formatDate(trip.startDate)} - {formatDate(trip.endDate)}</span>
                </div>

                <div className="trip-meta">
                    <div className="trip-duration">
                        <span className="meta-icon">⏱️</span>
                        <span>{getDuration()}</span>
                    </div>
                    <div className="trip-budget">
                        <span className="meta-icon">{getBudgetIcon(trip.budgetLevel)}</span>
                        <span>{trip.budgetLevel}</span>
                    </div>
                </div>

                {trip.notes && (
                    <p className="trip-notes">{trip.notes}</p>
                )}

                <div className="trip-card-actions">
                    <button
                        className="action-btn view-btn"
                        onClick={() => navigate(`/trip/${trip.id}`)}
                    >
                        <span>View Details</span>
                        <span className="btn-arrow">→</span>
                    </button>
                    <button
                        className="action-btn delete-btn"
                        onClick={() => setShowDeleteConfirm(true)}
                        disabled={deleting}
                    >
                        🗑️
                    </button>
                </div>
            </div>

            {showDeleteConfirm && (
                <div className="delete-confirm-overlay" onClick={() => setShowDeleteConfirm(false)}>
                    <div className="delete-confirm-modal" onClick={(e) => e.stopPropagation()}>
                        <h3>Delete Trip?</h3>
                        <p>Are you sure you want to delete "{trip.destination}"? This action cannot be undone.</p>
                        <div className="confirm-actions">
                            <button
                                className="cancel-btn"
                                onClick={() => setShowDeleteConfirm(false)}
                            >
                                Cancel
                            </button>
                            <button
                                className="confirm-delete-btn"
                                onClick={handleDelete}
                                disabled={deleting}
                            >
                                {deleting ? 'Deleting...' : 'Delete'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TripCard;
