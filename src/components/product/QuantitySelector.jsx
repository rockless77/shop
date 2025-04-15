import React, { useState, useEffect } from 'react';

const QuantitySelector = ({ 
  initialQuantity = 1, 
  maxQuantity = 10,
  onQuantityChange,
  disabled = false
}) => {
  const [quantity, setQuantity] = useState(initialQuantity);

  useEffect(() => {
    onQuantityChange(quantity);
  }, [quantity, onQuantityChange]);

  const handleDecrement = () => {
    setQuantity(prev => Math.max(1, prev - 1));
  };

  const handleIncrement = () => {
    setQuantity(prev => Math.min(maxQuantity, prev + 1));
  };

  return (
    <div className="quantity-selector">
      <h3 className="text-sm font-medium mb-2">Quantity:</h3>
      <div className="flex items-center border border-gray-200 rounded-md w-fit">
        <button
          onClick={handleDecrement}
          disabled={quantity <= 1 || disabled}
          className={`px-3 py-1 text-lg ${
            quantity <= 1 || disabled ? 'text-gray-300 cursor-not-allowed' : 'hover:bg-gray-50'
          }`}
        >
          -
        </button>
        <span className="px-4 py-1 border-x border-gray-200 text-center min-w-[40px]">
          {quantity}
        </span>
        <button
          onClick={handleIncrement}
          disabled={quantity >= maxQuantity || disabled}
          className={`px-3 py-1 text-lg ${
            quantity >= maxQuantity || disabled ? 'text-gray-300 cursor-not-allowed' : 'hover:bg-gray-50'
          }`}
        >
          +
        </button>
      </div>
    </div>
  );
};

export default QuantitySelector;