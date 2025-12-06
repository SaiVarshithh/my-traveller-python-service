import React from 'react';
import ActivityCard from './ActivityCard';
import './DayItinerary.css';

const DayItinerary = ({ itinerary, onUpdate }) => {
    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            weekday: 'long',
            month: 'long',
            day: 'numeric'
        });
    };

    const getTotalDuration = () => {
        const totalMinutes = itinerary.activities.reduce((sum, activity) => {
            return sum + activity.durationMinutes + activity.transportDurationMinutes;
        }, 0);

        const hours = Math.floor(totalMinutes / 60);
        const minutes = totalMinutes % 60;
        return `${hours}h ${minutes}m`;
    };

    return (
        <div className="day-itinerary fade-in">
            <div className="day-header">
                <div className="day-info">
                    <h3>Day {itinerary.dayNumber}</h3>
                    <p className="day-date">{formatDate(itinerary.date)}</p>
                    {itinerary.theme && (
                        <span className="day-theme">
                            <span className="theme-icon">🎯</span>
                            {itinerary.theme}
                        </span>
                    )}
                </div>
                <div className="day-stats">
                    <div className="stat-item">
                        <span className="stat-icon">📍</span>
                        <span>{itinerary.activities.length} stops</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-icon">⏱️</span>
                        <span>{getTotalDuration()}</span>
                    </div>
                </div>
            </div>

            {itinerary.notes && (
                <div className="day-notes">
                    <p>{itinerary.notes}</p>
                </div>
            )}

            <div className="activities-timeline">
                {itinerary.activities.map((activity, index) => (
                    <ActivityCard
                        key={activity.id}
                        activity={activity}
                        index={index}
                        isLast={index === itinerary.activities.length - 1}
                        onUpdate={onUpdate}
                    />
                ))}
            </div>
        </div>
    );
};

export default DayItinerary;
