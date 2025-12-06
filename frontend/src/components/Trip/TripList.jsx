import React, { useState } from 'react';
import { useQuery } from '@apollo/client';
import { GET_MY_TRIPS } from '../../graphql/queries';
import { useAuth } from '../../context/AuthContext';
import TripCard from './TripCard';
import CreateTripModal from './CreateTripModal';
import './TripList.css';

const TripList = () => {
    const { token } = useAuth();
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [filter, setFilter] = useState('all'); // all, planning, confirmed, ongoing, completed

    const { data, loading, error, refetch } = useQuery(GET_MY_TRIPS, {
        variables: { token },
        skip: !token,
    });

    const trips = data?.myTrips || [];

    const filteredTrips = trips.filter(trip => {
        if (filter === 'all') return true;
        return trip.status.toLowerCase() === filter;
    });

    const stats = {
        total: trips.length,
        planning: trips.filter(t => t.status === 'PLANNING').length,
        confirmed: trips.filter(t => t.status === 'CONFIRMED').length,
        ongoing: trips.filter(t => t.status === 'ONGOING').length,
        completed: trips.filter(t => t.status === 'COMPLETED').length,
    };

    if (loading) {
        return (
            <div className="trip-list-container">
                <div className="loading-skeleton">
                    <div className="skeleton-header"></div>
                    <div className="skeleton-grid">
                        {[1, 2, 3].map(i => (
                            <div key={i} className="skeleton-card"></div>
                        ))}
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="trip-list-container">
                <div className="error-message">
                    <span className="error-icon">⚠️</span>
                    <h3>Failed to load trips</h3>
                    <p>{error.message}</p>
                    <button onClick={() => refetch()} className="retry-btn">
                        Try Again
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="trip-list-container fade-in">
            <div className="trip-list-header slide-up">
                <div>
                    <h1>My Trips</h1>
                    <p>Plan, manage, and explore your adventures</p>
                </div>
                <button
                    className="create-trip-btn pulse"
                    onClick={() => setShowCreateModal(true)}
                >
                    <span className="btn-icon">✈️</span>
                    Create New Trip
                </button>
            </div>

            <div className="trip-stats scale-in">
                <div className="stat-item" onClick={() => setFilter('all')}>
                    <span className="stat-value">{stats.total}</span>
                    <span className="stat-label">Total Trips</span>
                </div>
                <div className="stat-item" onClick={() => setFilter('planning')}>
                    <span className="stat-value">{stats.planning}</span>
                    <span className="stat-label">Planning</span>
                </div>
                <div className="stat-item" onClick={() => setFilter('confirmed')}>
                    <span className="stat-value">{stats.confirmed}</span>
                    <span className="stat-label">Confirmed</span>
                </div>
                <div className="stat-item" onClick={() => setFilter('ongoing')}>
                    <span className="stat-value">{stats.ongoing}</span>
                    <span className="stat-label">Ongoing</span>
                </div>
                <div className="stat-item" onClick={() => setFilter('completed')}>
                    <span className="stat-value">{stats.completed}</span>
                    <span className="stat-label">Completed</span>
                </div>
            </div>

            <div className="filter-tabs">
                {['all', 'planning', 'confirmed', 'ongoing', 'completed'].map(status => (
                    <button
                        key={status}
                        className={`filter-tab ${filter === status ? 'active' : ''}`}
                        onClick={() => setFilter(status)}
                    >
                        {status.charAt(0).toUpperCase() + status.slice(1)}
                    </button>
                ))}
            </div>

            {filteredTrips.length === 0 ? (
                <div className="empty-state slide-up">
                    <div className="empty-icon">🗺️</div>
                    <h2>No trips {filter !== 'all' ? `in ${filter} status` : 'yet'}</h2>
                    <p>Start planning your next adventure!</p>
                    <button
                        className="create-trip-btn-secondary"
                        onClick={() => setShowCreateModal(true)}
                    >
                        Create Your First Trip
                    </button>
                </div>
            ) : (
                <div className="trips-grid">
                    {filteredTrips.map((trip, index) => (
                        <TripCard
                            key={trip.id}
                            trip={trip}
                            index={index}
                            onUpdate={refetch}
                        />
                    ))}
                </div>
            )}

            {showCreateModal && (
                <CreateTripModal
                    onClose={() => setShowCreateModal(false)}
                    onSuccess={() => {
                        setShowCreateModal(false);
                        refetch();
                    }}
                />
            )}
        </div>
    );
};

export default TripList;
