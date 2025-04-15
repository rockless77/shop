import React from 'react';

const Support = () => {
  return (
    <div className="support-page">
      <h1>Customer Support</h1>
      <div className="support-options">
        <div className="support-card">
          <h2>📞 Contact Us</h2>
          <p>Phone: 1-800-SHOP-EASY</p>
          <p>Email: support@shopeasy.com</p>
        </div>
        <div className="support-card">
          <h2>❓ FAQs</h2>
          <ul>
            <li>How do I track my order?</li>
            <li>What's your return policy?</li>
            <li>Payment methods accepted</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Support;