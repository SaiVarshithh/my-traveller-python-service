import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@apollo/client';
import { GET_TRIP } from '../../graphql/queries';
import { REGENERATE_ITINERARY, UPDATE_TRIP } from '../../graphql/mutations';
import { useAuth } from '../../context/AuthContext';
import DayItinerary from './DayItinerary';
import './TripDetail.css';

const TripDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { token } = useAuth();
    const [activeDay, setActiveDay] = useState(1);

    const { data, loading, error, refetch } = useQuery(GET_TRIP, {
        variables: { token, tripId: parseInt(id) },
        skip: !token || !id,
    });

    const [regenerateItinerary, { loading: regenerating }] = useMutation(REGENERATE_ITINERARY);
    const [updateTrip] = useMutation(UPDATE_TRIP);

    const trip = data?.trip;

    const handleRegenerateItinerary = async () => {
        if (!window.confirm('Regenerate itinerary? This will replace your current plan.')) return;

        try {
            await regenerateItinerary({
                variables: { token, tripId: parseInt(id) }
            });
            refetch();
        } catch (err) {
            console.error('Failed to regenerate:', err);
            alert('Failed to regenerate itinerary');
        }
    };

    const handleStatusChange = async (newStatus) => {
        try {
            await updateTrip({
                variables: {
                    token,
                    tripId: parseInt(id),
                    input: { status: newStatus }
                }
            });
            refetch();
        } catch (err) {
            console.error('Failed to update status:', err);
        }
    };

    if (loading) {
        return (
            <div className="trip-detail-container">
                <div className="loading-state">
                    <div className="loading-spinner"></div>
                    <h3>Loading trip details...</h3>
                </div>
            </div>
        );
    }

    if (error || !trip) {
        return (
            <div className="trip-detail-container">
                <div className="error-state">
                    <span className="error-icon">⚠️</span>
                    <h3>Trip not found</h3>
                    <p>{error?.message || 'This trip does not exist or you do not have access to it.'}</p>
                    <button onClick={() => navigate('/trips')} className="back-btn">
                        ← Back to Trips
                    </button>
                </div>
            </div>
        );
    }

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            month: 'long',
            day: 'numeric',
            year: 'numeric'
        });
    };

    const getDuration = () => {
        const start = new Date(trip.startDate);
        const end = new Date(trip.endDate);
        const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1;
        return days;
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

    return (
        <div className="trip-detail-container fade-in">
            <button onClick={() => navigate('/trips')} className="back-button">
                ← Back to Trips
            </button>

            <div className="trip-header slide-up">
                <div className="trip-header-content">
                    <div className="trip-title-section">
                        <h1>{trip.destination}</h1>
                        <div className="trip-meta-info">
                            <span className="meta-item">
                                <span className="meta-icon">📅</span>
                                {formatDate(trip.startDate)} - {formatDate(trip.endDate)}
                            </span>
                            <span className="meta-item">
                                <span className="meta-icon">⏱️</span>
                                {getDuration()} days
                            </span>
                            <span className="meta-item">
                                <span className="meta-icon">💰</span>
                                {trip.budgetLevel}
                            </span>
                        </div>
                    </div>

                    <div
                        className="trip-status-badge-large"
                        style={{ background: getStatusColor(trip.status) }}
                    >
                        {trip.status}
                    </div>
                </div>

                {trip.notes && (
                    <div className="trip-notes-section">
                        <p>{trip.notes}</p>
                    </div>
                )}

                <div className="trip-actions">
                    <select
                        value={trip.status}
                        onChange={(e) => handleStatusChange(e.target.value)}
                        className="status-select"
                    >
                        <option value="PLANNING">Planning</option>
                        <option value="CONFIRMED">Confirmed</option>
                        <option value="ONGOING">Ongoing</option>
                        <option value="COMPLETED">Completed</option>
                        <option value="CANCELLED">Cancelled</option>
                    </select>

                    <button
                        onClick={handleRegenerateItinerary}
                        disabled={regenerating}
                        className="action-button regenerate-btn"
                    >
                        {regenerating ? '🔄 Regenerating...' : '🔄 Regenerate Itinerary'}
                    </button>
                </div>
            </div>

            <div className="itinerary-section">
                <div className="section-header">
                    <h2>Daily Itinerary</h2>
                    <p>{trip.itineraries?.length || 0} days planned</p>
                </div>

                {trip.itineraries && trip.itineraries.length > 0 ? (
                    <>
                        <div className="day-tabs">
                            {trip.itineraries.map((itinerary) => (
                                <button
                                    key={itinerary.id}
                                    className={`day-tab ${activeDay === itinerary.dayNumber ? 'active' : ''}`}
                                    onClick={() => setActiveDay(itinerary.dayNumber)}
                                >
                                    <span className="day-label">Day {itinerary.dayNumber}</span>
                                    <span className="day-date">
                                        {new Date(itinerary.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                                    </span>
                                </button>
                            ))}
                        </div>

                        <div className="itinerary-content">
                            {trip.itineraries
                                .filter(itin => itin.dayNumber === activeDay)
                                .map(itinerary => (
                                    <DayItinerary
                                        key={itinerary.id}
                                        itinerary={itinerary}
                                        onUpdate={refetch}
                                    />
                                ))}
                        </div>
                    </>
                ) : (
                    <div className="empty-itinerary">
                        <span className="empty-icon">📅</span>
                        <h3>No itinerary yet</h3>
                        <p>Click "Regenerate Itinerary" to create a plan for this trip</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default TripDetail;
