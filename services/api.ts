export const fetchProducts = async () => {
    const response = await fetch('https://fakestoreapi.com/products');
    return await response.json();
  };
  
  export const checkout = async (cartItems: any[]) => {
    const response = await fetch('/api/checkout', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ items: cartItems }),
    });
    return await response.json();
  };