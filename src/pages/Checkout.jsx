import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Checkout() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    address: '',
    city: '',
    zipCode: '',
    country: '',
    phone: '',
    email: '',
    shippingMethod: 'standard',
    paymentMethod: 'creditCard',
    cardNumber: '',
    cardName: '',
    expiry: '',
    cvv: ''
  })
  const [errors, setErrors] = useState({})
  const [orderPlaced, setOrderPlaced] = useState(false)
  const [orderNumber, setOrderNumber] = useState('')

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const validate = () => {
    const newErrors = {}
    const requiredFields = [
      'firstName', 'lastName', 'address', 'city', 
      'zipCode', 'country', 'phone', 'email'
    ]
    
    requiredFields.forEach(field => {
      if (!formData[field]) newErrors[field] = 'This field is required'
    })

    if (formData.paymentMethod === 'creditCard') {
      if (!formData.cardNumber) newErrors.cardNumber = 'Card number is required'
      if (!formData.cardName) newErrors.cardName = 'Cardholder name is required'
      if (!formData.expiry) newErrors.expiry = 'Expiry date is required'
      if (!formData.cvv) newErrors.cvv = 'CVV is required'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (validate()) {
      // In a real app, you would process payment here
      const orderNum = 'ORD-' + Math.floor(Math.random() * 1000000)
      setOrderNumber(orderNum)
      setOrderPlaced(true)
      // Clear cart, etc.
    }
  }

  if (orderPlaced) {
    return (
      <div className="order-confirmation">
        <h2>Thank you for your order!</h2>
        <p>Your order number is: <strong>{orderNumber}</strong></p>
        <p>We've sent a confirmation email to {formData.email}</p>
        <p>Estimated delivery date: {new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toDateString()}</p>
        <button onClick={() => navigate('/')}>Continue Shopping</button>
        <button onClick={() => navigate('/order-tracking')}>Track Your Order</button>
      </div>
    )
  }

  return (
    <div className="checkout-page">
      <h1>Checkout</h1>
      <form onSubmit={handleSubmit}>
        <div className="checkout-sections">
          <section className="shipping-info">
            <h2>Shipping Information</h2>
            <div className="form-row">
              <div className="form-group">
                <label>First Name</label>
                <input 
                  type="text" 
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleChange}
                />
                {errors.firstName && <span className="error">{errors.firstName}</span>}
              </div>
              <div className="form-group">
                <label>Last Name</label>
                <input 
                  type="text" 
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleChange}
                />
                {errors.lastName && <span className="error">{errors.lastName}</span>}
              </div>
            </div>
            {/* More shipping fields... */}
          </section>

          <section className="shipping-method">
            <h2>Shipping Method</h2>
            <div className="radio-group">
              <label>
                <input 
                  type="radio" 
                  name="shippingMethod"
                  value="standard"
                  checked={formData.shippingMethod === 'standard'}
                  onChange={handleChange}
                />
                Standard Shipping (5-7 business days) - Free
              </label>
              <label>
                <input 
                  type="radio" 
                  name="shippingMethod"
                  value="express"
                  checked={formData.shippingMethod === 'express'}
                  onChange={handleChange}
                />
                Express Shipping (2-3 business days) - $9.99
              </label>
            </div>
          </section>

          <section className="payment-method">
            <h2>Payment Method</h2>
            <div className="radio-group">
              <label>
                <input 
                  type="radio" 
                  name="paymentMethod"
                  value="creditCard"
                  checked={formData.paymentMethod === 'creditCard'}
                  onChange={handleChange}
                />
                Credit Card
              </label>
              <label>
                <input 
                  type="radio" 
                  name="paymentMethod"
                  value="paypal"
                  checked={formData.paymentMethod === 'paypal'}
                  onChange={handleChange}
                />
                PayPal
              </label>
            </div>

            {formData.paymentMethod === 'creditCard' && (
              <div className="credit-card-form">
                <div className="form-group">
                  <label>Card Number</label>
                  <input 
                    type="text" 
                    name="cardNumber"
                    value={formData.cardNumber}
                    onChange={handleChange}
                    placeholder="1234 5678 9012 3456"
                  />
                  {errors.cardNumber && <span className="error">{errors.cardNumber}</span>}
                </div>
                <div className="form-group">
                  <label>Name on Card</label>
                  <input 
                    type="text" 
                    name="cardName"
                    value={formData.cardName}
                    onChange={handleChange}
                  />
                  {errors.cardName && <span className="error">{errors.cardName}</span>}
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label>Expiry Date</label>
                    <input 
                      type="text" 
                      name="expiry"
                      value={formData.expiry}
                      onChange={handleChange}
                      placeholder="MM/YY"
                    />
                    {errors.expiry && <span className="error">{errors.expiry}</span>}
                  </div>
                  <div className="form-group">
                    <label>CVV</label>
                    <input 
                      type="text" 
                      name="cvv"
                      value={formData.cvv}
                      onChange={handleChange}
                      placeholder="123"
                    />
                    {errors.cvv && <span className="error">{errors.cvv}</span>}
                  </div>
                </div>
              </div>
            )}
          </section>
        </div>

        <div className="order-summary">
          <h3>Order Summary</h3>
          {/* Display order summary */}
          <button type="submit" className="place-order-button">
            Place Order
          </button>
        </div>
      </form>
    </div>
  )
}