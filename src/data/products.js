// Exporting all products
export const allProducts = [
  // Product data here
];

// Exporting a featured products list
export const featuredProducts = [
  // Featured products here
];

// Function to get a product by ID
export const getProductById = (id) => {
  return allProducts.find(product => product.id === id);
};

// Function to add a product to the cart
export const addToCart = (productId) => {
  // Cart logic here
};

// Function to add a product to the wishlist
export const addToWishlist = (productId) => {
  // Wishlist logic here
};
