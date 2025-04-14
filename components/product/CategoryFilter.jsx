import React from 'react';

const CategoryFilter = ({ 
  categories, 
  selectedCategory, 
  onSelect,
  className = ''
}) => {
  return (
    <div className={`category-filter ${className}`}>
      <h3 className="text-sm font-medium mb-2">Filter by Category:</h3>
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => onSelect('all')}
          className={`px-4 py-2 border rounded-md text-sm ${
            selectedCategory === 'all'
              ? 'bg-black text-white border-black'
              : 'hover:bg-gray-50 border-gray-200'
          }`}
        >
          All
        </button>
        {categories.map((category) => (
          <button
            key={category}
            onClick={() => onSelect(category)}
            className={`px-4 py-2 border rounded-md text-sm ${
              selectedCategory === category
                ? 'bg-black text-white border-black'
                : 'hover:bg-gray-50 border-gray-200'
            }`}
          >
            {category.charAt(0).toUpperCase() + category.slice(1)}
          </button>
        ))}
      </div>
    </div>
  );
};

export default CategoryFilter;