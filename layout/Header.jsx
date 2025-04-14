import React from 'react'
import { Link } from 'react-router-dom'

export default function Header() {
  const isAuthenticated = localStorage.getItem('isAuthenticated')
  
  return (
    <header className="site-header">
      <div className="header-container">
        <div className="logo">
          <Link to="/">ShopEasy</Link>
        </div>
        
        <div className="search-bar">
          <input type="text" placeholder="Search products..." />
          <button>Search</button>
        </div>
        
        <nav className="user-nav">
          {isAuthenticated ? (
            <>
              <Link to="/profile">My Account</Link>
              <Link to="/wishlist">Wishlist</Link>
              <Link to="/cart">Cart</Link>
              <button>Logout</button>
            </>
          ) : (
            <>
              <Link to="/login">Login</Link>
              <Link to="/register">Register</Link>
            </>
          )}
        </nav>
      </div>
      
      <nav className="main-nav">
        <Link to="/products">All Products</Link>
        <Link to="/products?category=electronics">Electronics</Link>
        <Link to="/products?category=clothing">Clothing</Link>
        <Link to="/products?category=home">Home</Link>
        <Link to="/products?category=beauty">Beauty</Link>
        <Link to="/sale">Sale</Link>
      </nav>
    </header>
  )
}