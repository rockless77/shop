import React from "react";

import { featuredProducts } from "../data/products";

export default function Home() {
  return (
    <div className="home">
      <div className="product-grid">
        {featuredProducts.map(product => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </div>
  );
}