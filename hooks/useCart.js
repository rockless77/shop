import { useCart } from '../context/CartContext';

export const useCartActions = () => {
  const cart = useCart();
  
  const addToCart = (product, quantity = 1, size) => {
    cart.addItem({
      id: product.id,
      name: product.name,
      price: product.price,
      image: product.images[0],
      quantity,
      size,
    });
  };

  const removeFromCart = (productId, size) => {
    cart.removeItem(productId, size);
  };

  const updateCartItemQuantity = (productId, newQuantity, size) => {
    if (newQuantity < 1) {
      removeFromCart(productId, size);
      return;
    }
    cart.updateQuantity(productId, newQuantity, size);
  };

  return {
    ...cart,
    addToCart,
    removeFromCart,
    updateCartItemQuantity,
  };
};