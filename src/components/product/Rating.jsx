import React from 'react';
import { FaStar, FaStarHalfAlt, FaRegStar } from 'react-icons/fa';

const Rating = ({ value, text, color = '#f8e825' }) => {
  return (
    <div className="rating">
      <div className="flex items-center">
        {[1, 2, 3, 4, 5].map((index) => {
          if (value >= index) {
            return <FaStar key={index} style={{ color }} />;
          } else if (value >= index - 0.5) {
            return <FaStarHalfAlt key={index} style={{ color }} />;
          } else {
            return <FaRegStar key={index} style={{ color }} />;
          }
        })}
        {text && <span className="ml-2 text-sm">{text}</span>}
      </div>
    </div>
  );
};

export default Rating;