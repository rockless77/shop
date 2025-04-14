import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getProductById, addToCart, addToWishlist } from '../data/products'
import { useCart } from '../contexts/CartContext'
import { useAuth } from '../contexts/AuthContext'
import ImageGallery from '../components/product/ImageGallery'
import SizeSelector from '../components/product/SizeSelector'
import QuantitySelector from '../components/product/QuantitySelector'
import Rating from '../components/product/Rating'







export default function ProductDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { addItemToCart } = useCart()
  const { isAuthenticated } = useAuth()
  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedSize, setSelectedSize] = useState('')
  const [quantity, setQuantity] = useState(1)
  const [selectedImage, setSelectedImage] = useState(0)
  const [isAddingToCart, setIsAddingToCart] = useState(false)
  const [isAddingToWishlist, setIsAddingToWishlist] = useState(false)

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const productData = await getProductById(id)
        if (!productData) {
          throw new Error('Product not found')
        }
        setProduct(productData)
        // Set default size if available
        if (productData.sizes && productData.sizes.length > 0) {
          setSelectedSize(productData.sizes[0])
        }
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchProduct()
  }, [id])

  const handleAddToCart = async () => {
    if (!selectedSize && product.sizes && product.sizes.length > 0) {
      setError('Please select a size')
      return
    }

    setIsAddingToCart(true)
    try {
      await addToCart({
        productId: product.id,
        size: selectedSize,
        quantity,
        price: product.price
      })
      addItemToCart({
        id: product.id,
        name: product.name,
        price: product.price,
        image: product.images[0],
        size: selectedSize,
        quantity
      })
      navigate('/cart')
    } catch (err) {
      setError(err.message)
    } finally {
      setIsAddingToCart(false)
    }
  }

  const handleAddToWishlist = async () => {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: `/product/${id}` } })
      return
    }

    setIsAddingToWishlist(true)
    try {
      await addToWishlist(product.id)
      // Show success message or update UI
    } catch (err) {
      setError(err.message)
    } finally {
      setIsAddingToWishlist(false)
    }
  }

  if (loading) return <div className="loading">Loading product details...</div>
  if (error) return <div className="error">Error: {error}</div>
  if (!product) return <div className="not-found">Product not found</div>

  return (
    <div className="product-detail-container">
      <div className="product-images-section">
        <ImageGallery 
          images={product.images}
          selectedIndex={selectedImage}
          onSelect={setSelectedImage}
        />
      </div>

      <div className="product-info-section">
        <h1 className="product-title">{product.name}</h1>
        
        <div className="product-meta">
          <Rating value={product.rating} reviews={product.reviewCount} />
          <span className="product-sku">SKU: {product.sku}</span>
          <span className={`product-stock ${product.stock > 0 ? 'in-stock' : 'out-of-stock'}`}>
            {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
          </span>
        </div>

        <div className="product-price">
          {product.discountedPrice ? (
            <>
              <span className="current-price">${product.discountedPrice}</span>
              <span className="original-price">${product.price}</span>
              <span className="discount-percentage">
                {Math.round((1 - product.discountedPrice / product.price) * 100)}% OFF
              </span>
            </>
          ) : (
            <span className="current-price">${product.price}</span>
          )}
        </div>

        <div className="product-description">
          <h3>Description</h3>
          <p>{product.description}</p>
        </div>

        {product.sizes && product.sizes.length > 0 && (
          <div className="product-size">
            <h3>Size</h3>
            <SizeSelector 
              sizes={product.sizes}
              selectedSize={selectedSize}
              onSelect={setSelectedSize}
            />
          </div>
        )}

        <div className="product-quantity">
          <h3>Quantity</h3>
          <QuantitySelector 
            quantity={quantity}
            maxQuantity={product.stock}
            onChange={setQuantity}
          />
        </div>

        <div className="product-actions">
          <button 
            className="add-to-cart-btn"
            onClick={handleAddToCart}
            disabled={isAddingToCart || product.stock <= 0}
          >
            {isAddingToCart ? 'Adding...' : 'Add to Cart'}
          </button>
          
          <button 
            className="add-to-wishlist-btn"
            onClick={handleAddToWishlist}
            disabled={isAddingToWishlist}
          >
            {isAddingToWishlist ? 'Adding...' : 'Add to Wishlist'}
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        <div className="product-details">
          <h3>Details</h3>
          <ul>
            {product.details && Object.entries(product.details).map(([key, value]) => (
              <li key={key}>
                <strong>{key}:</strong> {value}
              </li>
            ))}
          </ul>
        </div>

        <div className="product-shipping">
          <h3>Shipping & Returns</h3>
          <p>Free standard shipping on all orders. Returns accepted within 30 days.</p>
        </div>
      </div>
    </div>
  )
}
<Rating 
  value={product.rating} 
  text={`${product.numReviews} reviews`} 
  color="#ffd700"
/>


