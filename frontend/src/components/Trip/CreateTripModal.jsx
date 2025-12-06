import React, { useState } from 'react';
import { useMutation } from '@apollo/client';
import { CREATE_TRIP } from '../../graphql/mutations';
import { useAuth } from '../../context/AuthContext';
import './CreateTripModal.css';

const CreateTripModal = ({ onClose, onSuccess }) => {
    const { token } = useAuth();
    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState({
        destination: '',
        startDate: '',
        endDate: '',
        budgetLevel: 'MODERATE',
        notes: ''
    });

    const [createTrip, { loading, error }] = useMutation(CREATE_TRIP);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async () => {
        try {
            const result = await createTrip({
                variables: {
                    token,
                    input: {
                        destination: formData.destination,
                        startDate: formData.startDate,
                        endDate: formData.endDate,
                        budgetLevel: formData.budgetLevel,
                        notes: formData.notes || null
                    }
                }
            });

            if (result.data?.createTrip) {
                onSuccess(result.data.createTrip.trip);
            }
        } catch (err) {
            console.error('Failed to create trip:', err);
        }
    };

    const canProceed = () => {
        if (step === 1) return formData.destination.trim().length > 0;
        if (step === 2) return formData.startDate && formData.endDate;
        if (step === 3) return formData.budgetLevel;
        if (step === 4) return true; // Step 4 is optional notes, always allow
        return false;
    };

    const renderStep = () => {
        switch (step) {
            case 1:
                return (
                    <div className="modal-step fade-in">
                        <div className="step-icon">🌍</div>
                        <h2>Where do you want to go?</h2>
                        <p>Enter your dream destination</p>
                        <input
                            type="text"
                            name="destination"
                            value={formData.destination}
                            onChange={handleChange}
                            placeholder="e.g., Paris, France"
                            className="trip-input"
                            autoFocus
                        />
                        <div className="popular-destinations">
                            <p className="suggestions-label">Popular destinations:</p>
                            <div className="destination-chips">
                                {['Paris, France', 'Tokyo, Japan', 'New York, USA', 'Bali, Indonesia'].map(dest => (
                                    <button
                                        key={dest}
                                        className="destination-chip"
                                        onClick={() => setFormData({ ...formData, destination: dest })}
                                    >
                                        {dest}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                );

            case 2:
                return (
                    <div className="modal-step fade-in">
                        <div className="step-icon">📅</div>
                        <h2>When are you traveling?</h2>
                        <p>Select your travel dates</p>
                        <div className="date-inputs">
                            <div className="date-group">
                                <label>Start Date</label>
                                <input
                                    type="date"
                                    name="startDate"
                                    value={formData.startDate}
                                    onChange={handleChange}
                                    className="trip-input"
                                    min={new Date().toISOString().split('T')[0]}
                                />
                            </div>
                            <div className="date-group">
                                <label>End Date</label>
                                <input
                                    type="date"
                                    name="endDate"
                                    value={formData.endDate}
                                    onChange={handleChange}
                                    className="trip-input"
                                    min={formData.startDate || new Date().toISOString().split('T')[0]}
                                />
                            </div>
                        </div>
                        {formData.startDate && formData.endDate && (
                            <div className="duration-display">
                                <span className="duration-icon">⏱️</span>
                                <span>
                                    {Math.ceil((new Date(formData.endDate) - new Date(formData.startDate)) / (1000 * 60 * 60 * 24)) + 1} days
                                </span>
                            </div>
                        )}
                    </div>
                );

            case 3:
                return (
                    <div className="modal-step fade-in">
                        <div className="step-icon">💰</div>
                        <h2>What's your budget?</h2>
                        <p>Choose your preferred budget level</p>
                        <div className="budget-options">
                            {[
                                { value: 'BUDGET', label: 'Budget', icon: '💰', desc: 'Affordable options' },
                                { value: 'MODERATE', label: 'Moderate', icon: '💰💰', desc: 'Balanced experience' },
                                { value: 'LUXURY', label: 'Luxury', icon: '💰💰💰', desc: 'Premium choices' }
                            ].map(option => (
                                <button
                                    key={option.value}
                                    className={`budget-option ${formData.budgetLevel === option.value ? 'selected' : ''}`}
                                    onClick={() => setFormData({ ...formData, budgetLevel: option.value })}
                                >
                                    <div className="budget-icon">{option.icon}</div>
                                    <div className="budget-label">{option.label}</div>
                                    <div className="budget-desc">{option.desc}</div>
                                </button>
                            ))}
                        </div>
                    </div>
                );

            case 4:
                return (
                    <div className="modal-step fade-in">
                        <div className="step-icon">📝</div>
                        <h2>Any special notes?</h2>
                        <p>Add notes or preferences (optional)</p>
                        <textarea
                            name="notes"
                            value={formData.notes}
                            onChange={handleChange}
                            placeholder="e.g., Anniversary trip, prefer cultural activities..."
                            className="trip-textarea"
                            rows="4"
                        />
                        <div className="trip-summary">
                            <h3>Trip Summary</h3>
                            <div className="summary-item">
                                <span className="summary-label">Destination:</span>
                                <span className="summary-value">{formData.destination}</span>
                            </div>
                            <div className="summary-item">
                                <span className="summary-label">Dates:</span>
                                <span className="summary-value">
                                    {new Date(formData.startDate).toLocaleDateString()} - {new Date(formData.endDate).toLocaleDateString()}
                                </span>
                            </div>
                            <div className="summary-item">
                                <span className="summary-label">Budget:</span>
                                <span className="summary-value">{formData.budgetLevel}</span>
                            </div>
                        </div>
                    </div>
                );

            default:
                return null;
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-container" onClick={(e) => e.stopPropagation()}>
                <button className="modal-close" onClick={onClose}>✕</button>

                <div className="modal-progress">
                    {[1, 2, 3, 4].map(s => (
                        <div
                            key={s}
                            className={`progress-step ${s <= step ? 'active' : ''} ${s < step ? 'completed' : ''}`}
                        >
                            <div className="progress-dot">{s < step ? '✓' : s}</div>
                            {s < 4 && <div className="progress-line"></div>}
                        </div>
                    ))}
                </div>

                <div className="modal-body">
                    {loading ? (
                        <div className="loading-state">
                            <div className="loading-spinner"></div>
                            <h3>Creating your trip...</h3>
                            <p>Generating personalized itinerary with AI 🤖</p>
                        </div>
                    ) : (
                        renderStep()
                    )}
                </div>

                {error && (
                    <div className="error-banner">
                        <span className="error-icon">⚠️</span>
                        <span>{error.message}</span>
                    </div>
                )}

                <div className="modal-footer">
                    {step > 1 && !loading && (
                        <button
                            className="modal-btn secondary"
                            onClick={() => setStep(step - 1)}
                        >
                            ← Back
                        </button>
                    )}
                    <div style={{ flex: 1 }}></div>
                    {step < 4 ? (
                        <button
                            className="modal-btn primary"
                            onClick={() => setStep(step + 1)}
                            disabled={!canProceed()}
                        >
                            Next →
                        </button>
                    ) : (
                        <button
                            className="modal-btn primary create-btn"
                            onClick={handleSubmit}
                            disabled={loading || !canProceed()}
                        >
                            {loading ? 'Creating...' : '✨ Create Trip'}
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default CreateTripModal;
