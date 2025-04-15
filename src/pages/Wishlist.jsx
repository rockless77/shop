import React from 'react';
import { useCart } from '../contexts/CartContext';

const Wishlist = () => {
  const { state } = useCart(); // Or use a dedicated wishlist context

  return (
    <div className="wishlist-page">
      <h1>Your Wishlist</h1>
      {state.items.length > 0 ? (
        <div className="wishlist-items">
          {state.items.map(item => (
            <div key={item.id} className="wishlist-item">
              <img src={item.image} alt={item.name} />
              <h3>{item.name}</h3>
              <p>${item.price}</p>
            </div>
          ))}
        </div>
      ) : (
        <p>Your wishlist is empty</p>
      )}
    </div>
  );
};

export default Wishlist;