import React from 'react';

const SizeSelector = ({ sizes, selectedSize, onSelect, availableSizes = [] }) => {
  // If availableSizes is provided, filter sizes to only show available ones
  const displaySizes = availableSizes.length > 0 
    ? sizes.filter(size => availableSizes.includes(size))
    : sizes;

  return (
    <div className="size-selector">
      <h3 className="text-sm font-medium mb-2">Size:</h3>
      <div className="flex flex-wrap gap-2">
        {displaySizes.map((size) => (
          <button
            key={size}
            onClick={() => onSelect(size)}
            className={`px-4 py-2 border rounded-md text-sm ${
              selectedSize === size
                ? 'bg-black text-white border-black'
                : 'hover:bg-gray-50 border-gray-200'
            } ${
              availableSizes.length > 0 && !availableSizes.includes(size)
                ? 'opacity-50 cursor-not-allowed'
                : ''
            }`}
            disabled={availableSizes.length > 0 && !availableSizes.includes(size)}
          >
            {size}
          </button>
        ))}
      </div>
    </div>
  );
};

export default SizeSelector;