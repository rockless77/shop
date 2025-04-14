import React, { useState } from 'react';
import SearchBar from '../components/product/SearchBar';  // Import SearchBar component
import CategoryFilter from '../components/product/CategoryFilter';  // Import CategoryFilter component
// import ProductCard from '../components/product/ProductCard'; // Assuming you have a ProductCard component
import { allProducts } from '../data/products';  // Import all products data

export default function Products() {
  const [searchTerm, setSearchTerm] = useState('');  // Manage search term state
  const [selectedCategory, setSelectedCategory] = useState('all');  // Manage selected category state

  // Filter products based on search term and selected category
  const filteredProducts = allProducts.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || product.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="products-page">
      {/* Filters Section */}
      <div className="filters">
        <SearchBar 
          onSearch={setSearchTerm} 
          className="mb-6"  // Optional: Add any custom styling classes
        />
        <CategoryFilter 
          categories={['all', 'electronics', 'clothing', 'home', 'beauty']} 
          selected={selectedCategory} 
          onSelect={setSelectedCategory}
        />
      </div>

      {/* Product List Section */}
      <div className="product-list">
        {filteredProducts.length > 0 ? (
          filteredProducts.map(product => (
            <ProductCard key={product.id} product={product} />
          ))
        ) : (
          <p>No products found matching your criteria.</p>
        )}
      </div>
    </div>
  );
}
