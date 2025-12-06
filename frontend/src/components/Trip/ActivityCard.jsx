import React, { useState } from 'react';
import { useMutation } from '@apollo/client';
import { REMOVE_ACTIVITY } from '../../graphql/mutations';
import { useAuth } from '../../context/AuthContext';
import './ActivityCard.css';

const ActivityCard = ({ activity, index, isLast, onUpdate }) => {
    const { token } = useAuth();
    const [expanded, setExpanded] = useState(false);
    const [removeActivity, { loading: removing }] = useMutation(REMOVE_ACTIVITY);

    const handleRemove = async () => {
        if (!window.confirm(`Remove "${activity.place.name}" from itinerary?`)) return;

        try {
            await removeActivity({
                variables: { token, activityId: activity.id }
            });
            onUpdate();
        } catch (err) {
            console.error('Failed to remove activity:', err);
            alert('Failed to remove activity');
        }
    };

    const getTransportIcon = (mode) => {
        const icons = {
            WALK: '🚶',
            DRIVE: '🚗',
            TRANSIT: '🚇',
            BIKE: '🚴',
            TAXI: '🚕',
            NONE: ''
        };
        return icons[mode] || '';
    };

    const getCategoryIcon = (category) => {
        const icons = {
            ATTRACTION: '🏛️',
            RESTAURANT: '🍽️',
            HOTEL: '🏨',
            MUSEUM: '🖼️',
            PARK: '🌳',
            SHOPPING: '🛍️',
            ENTERTAINMENT: '🎭',
            HISTORICAL: '🏰',
            RELIGIOUS: '⛪',
            NIGHTLIFE: '🌃',
            CAFE: '☕',
            OTHER: '📍'
        };
        return icons[category] || '📍';
    };

    const formatTime = (timeString) => {
        const [hours, minutes] = timeString.split(':');
        const hour = parseInt(hours);
        const ampm = hour >= 12 ? 'PM' : 'AM';
        const displayHour = hour % 12 || 12;
        return `${displayHour}:${minutes} ${ampm}`;
    };

    const formatDuration = (minutes) => {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        if (hours === 0) return `${mins}m`;
        if (mins === 0) return `${hours}h`;
        return `${hours}h ${mins}m`;
    };

    return (
        <div className={`activity-card scale-in ${expanded ? 'expanded' : ''}`} style={{ animationDelay: `${index * 0.1}s` }}>
            {activity.transportMode !== 'NONE' && activity.transportDurationMinutes > 0 && (
                <div className="transport-indicator">
                    <div className="transport-line"></div>
                    <div className="transport-info">
                        <span className="transport-icon">{getTransportIcon(activity.transportMode)}</span>
                        <span className="transport-duration">{formatDuration(activity.transportDurationMinutes)}</span>
                    </div>
                </div>
            )}

            <div className="activity-content" onClick={() => setExpanded(!expanded)}>
                <div className="activity-header">
                    <div className="activity-time">
                        <span className="time-value">{formatTime(activity.startTime)}</span>
                        <span className="duration-badge">{formatDuration(activity.durationMinutes)}</span>
                    </div>

                    <div className="activity-main">
                        <div className="activity-title">
                            <span className="category-icon">{getCategoryIcon(activity.place.category)}</span>
                            <h4>{activity.place.name}</h4>
                            {activity.isCustom && (
                                <span className="custom-badge">Custom</span>
                            )}
                        </div>

                        <div className="activity-meta">
                            <span className="meta-item">
                                <span className="meta-icon">📍</span>
                                {activity.place.address || 'Address not available'}
                            </span>
                            {activity.place.rating && (
                                <span className="meta-item">
                                    <span className="meta-icon">⭐</span>
                                    {activity.place.rating.toFixed(1)}
                                </span>
                            )}
                            {activity.place.priceLevel && (
                                <span className="meta-item">
                                    <span className="meta-icon">💰</span>
                                    {'$'.repeat(activity.place.priceLevel)}
                                </span>
                            )}
                        </div>
                    </div>

                    <button
                        className="expand-btn"
                        onClick={(e) => {
                            e.stopPropagation();
                            setExpanded(!expanded);
                        }}
                    >
                        {expanded ? '▲' : '▼'}
                    </button>
                </div>

                {expanded && (
                    <div className="activity-details">
                        {activity.notes && (
                            <div className="activity-notes">
                                <strong>Notes:</strong> {activity.notes}
                            </div>
                        )}

                        <div className="activity-actions">
                            {activity.place.phoneNumber && (
                                <a href={`tel:${activity.place.phoneNumber}`} className="action-link">
                                    📞 Call
                                </a>
                            )}
                            {activity.place.website && (
                                <a href={activity.place.website} target="_blank" rel="noopener noreferrer" className="action-link">
                                    🌐 Website
                                </a>
                            )}
                            <a
                                href={`https://www.google.com/maps/search/?api=1&query=${activity.place.latitude},${activity.place.longitude}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="action-link"
                            >
                                🗺️ View on Map
                            </a>
                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    handleRemove();
                                }}
                                disabled={removing}
                                className="remove-activity-btn"
                            >
                                {removing ? 'Removing...' : '🗑️ Remove'}
                            </button>
                        </div>
                    </div>
                )}
            </div>

            {!isLast && <div className="activity-connector"></div>}
        </div>
    );
};

export default ActivityCard;
