import React from 'react'
import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-sections">
        <section className="customer-service">
          <h3>Customer Service</h3>
          <ul>
            <li><Link to="/support">Help Center</Link></li>
            <li><Link to="/returns">Returns</Link></li>
            <li><Link to="/shipping">Shipping</Link></li>
          </ul>
        </section>
        
        <section className="about">
          <h3>About</h3>
          <ul>
            <li><Link to="/about">About Us</Link></li>
            <li><Link to="/contact">Contact Us</Link></li>
            <li><Link to="/privacy">Privacy Policy</Link></li>
          </ul>
        </section>
        
        <section className="payment-methods">
          <h3>Payment Methods</h3>
          <div className="payment-icons">
            <span>VISA</span>
            <span>PayPal</span>
            {/* Add more payment icons */}
          </div>
        </section>
      </div>
      
      <div className="copyright">
        <p>© {new Date().getFullYear()} ShopEasy Inc. • Privacy • Terms • Sitemap</p>
      </div>
    </footer>
  )
}