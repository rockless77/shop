import * as React from 'react';
import { createContext, useContext, useState } from 'react';

const WishlistContext = createContext({
  wishlist: [] as number[], // Array of product IDs
  toggleWishlist: (id: number) => {},
});

export const WishlistProvider = ({ children }: { children: React.ReactNode }) => {
  const [wishlist, setWishlist] = useState<number[]>([]);

  const toggleWishlist = (id: number) => {
    setWishlist(
      wishlist.includes(id)
        ? wishlist.filter(item => item !== id)
        : [...wishlist, id]
    );
  };

  return (
    <WishlistContext.Provider value={{ wishlist, toggleWishlist }}>
      {children}
    </WishlistContext.Provider>
  );
};

export const useWishlist = () => useContext(WishlistContext);
