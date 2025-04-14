import React from 'react'

export default function OrderTracking() {
  const orderDetails = {
    number: '#586789963',
    products: [
      { name: 'Product name', quantity: 1 },
      { name: 'Product name', quantity: 1 },
      { name: 'Product name', quantity: 1 }
    ],
    delivery: {
      name: 'Nikita Afonchenko',
      phone: '(453) 632-8404',
      address: 'Lubin 20-63, Poland'
    },
    payment: {
      method: 'VISA',
      details: 'VISA ****84'
    },
    tracking: [
      {
        date: '04 Mar',
        status: 'Packed',
        description: 'Consectetur ainet in excepteur moilit velit temper parisur fugiat culpe sit temper'
      },
      {
        date: '05 Mar',
        status: 'At the transit center',
        description: 'Exercitation voluptate elusmod qui irure dolore parisur'
      },
      {
        date: '06 Mar',
        status: 'Being delivered',
        description: 'Nula exercitation sit excepteur veniam ad irure et is voluptate'
      },
      {
        date: '07 Mar',
        status: 'Deliver to you',
        description: 'Fugiat aliqua et aute consequat quis sa adipisicing'
      }
    ]
  }

  return (
    <div className="order-tracking">
      <h1>Order tracking</h1>
      <p className="order-number">Order number {orderDetails.number}</p>
      
      <div className="order-sections">
        <section className="products">
          <h2>Product</h2>
          <ul>
            {orderDetails.products.map((product, index) => (
              <li key={index}>
                {product.name} Quantity: {product.quantity}
              </li>
            ))}
          </ul>
        </section>
        
        <section className="delivery">
          <h2>Delivery to</h2>
          <p>{orderDetails.delivery.name}</p>
          <p>{orderDetails.delivery.phone}</p>
          <p>{orderDetails.delivery.address}</p>
        </section>
        
        <section className="payment">
          <h2>Payment method</h2>
          <p><strong>{orderDetails.payment.method}</strong></p>
          <p>{orderDetails.payment.details}</p>
        </section>
      </div>
      
      <div className="tracking-timeline">
        <h2>Track your package</h2>
        {orderDetails.tracking.map((step, index) => (
          <div key={index} className="timeline-step">
            <div className="timeline-marker"></div>
            <div className="timeline-content">
              <h3>{step.date} {step.status}</h3>
              <p>{step.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}