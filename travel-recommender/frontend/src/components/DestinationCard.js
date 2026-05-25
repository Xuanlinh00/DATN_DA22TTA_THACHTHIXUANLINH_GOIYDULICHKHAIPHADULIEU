import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FaStar, FaMapMarkerAlt, FaDollarSign } from 'react-icons/fa';
import './DestinationCard.css';

function DestinationCard({ destination }) {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/destinations/${encodeURIComponent(destination['Destination Name'])}`);
  };

  const getBudgetIcon = (category) => {
    const count = category === 'Budget' ? 1 : category === 'Moderate' ? 2 : category === 'Expensive' ? 3 : 4;
    return Array(count).fill('$').join('');
  };

  // Placeholder image if none available
  const imageUrl = destination.image || `https://source.unsplash.com/800x600/?${encodeURIComponent(destination['Destination Name'])},travel`;

  return (
    <div className="destination-card" onClick={handleClick}>
      <div className="card-image">
        <img 
          src={imageUrl} 
          alt={destination['Destination Name']}
          onError={(e) => {
            e.target.src = 'https://source.unsplash.com/800x600/?travel,destination';
          }}
        />
        <div className="card-badge">{destination.Type}</div>
      </div>

      <div className="card-content">
        <h3 className="card-title">{destination['Destination Name']}</h3>
        
        <div className="card-location">
          <FaMapMarkerAlt className="icon" />
          <span>{destination.Country}</span>
        </div>

        <div className="card-details">
          <div className="card-rating">
            <FaStar className="star-icon" />
            <span>{destination['Avg Rating']?.toFixed(1) || 'N/A'}</span>
          </div>

          <div className="card-budget">
            <FaDollarSign className="icon" />
            <span>{getBudgetIcon(destination.Cost_Category)}</span>
          </div>
        </div>

        <div className="card-season">
          <span className="season-label">Best Season:</span>
          <span className="season-value">{destination['Best Season']}</span>
        </div>
      </div>
    </div>
  );
}

export default DestinationCard;
