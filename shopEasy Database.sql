CREATE TABLE users (
    id CHAR(36) PRIMARY KEY,  -- UUID stored as a CHAR(36) (a 36-character string)
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('buyer', 'seller', 'admin') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE products (
    id CHAR(36) PRIMARY KEY,  -- UUID stored as CHAR(36)
    seller_id CHAR(36),  -- Foreign Key referencing Users
    name VARCHAR(255) NOT NULL,
    description TEXT,  -- Text type for product description
    price DECIMAL(10, 2) NOT NULL,  -- Decimal type for price (10 digits in total, 2 after the decimal point)
    stock INT NOT NULL,  -- Inventory count (integer)
    size_options TEXT,  -- Available sizes, could store as JSON or comma-separated values
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Timestamp when the product was added
    FOREIGN KEY (seller_id) REFERENCES users(id)  -- Foreign key constraint linking to Users table
);
CREATE TABLE orders (
    id CHAR(36) PRIMARY KEY,  -- UUID stored as CHAR(36) for order ID
    buyer_id CHAR(36),  -- Foreign Key referencing Users (the buyer)
    total_price DECIMAL(10, 2) NOT NULL,  -- Total cost of the order
    status VARCHAR(50) NOT NULL,  -- Order status (e.g., 'pending', 'confirmed', 'shipped')
    shipping_method VARCHAR(255) NOT NULL,  -- Delivery method (courier, postal service, etc.)
    estimated_delivery DATE NOT NULL,  -- Estimated delivery date for the order
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Order creation date
    FOREIGN KEY (buyer_id) REFERENCES users(id)  -- Foreign key constraint linking to Users table
);
CREATE TABLE order_items (
    id CHAR(36) PRIMARY KEY,  -- UUID stored as CHAR(36) for order item ID
    order_id CHAR(36),  -- Foreign Key referencing Orders table
    product_id CHAR(36),  -- Foreign Key referencing Products table
    quantity INT NOT NULL,  -- Quantity of the product ordered
    price_at_time DECIMAL(10, 2) NOT NULL,  -- Price of the product at the time the order was placed
    FOREIGN KEY (order_id) REFERENCES orders(id),  -- Foreign key linking to Orders table
    FOREIGN KEY (product_id) REFERENCES products(id)  -- Foreign key linking to Products table
);
CREATE TABLE wishlist (
    id CHAR(36) PRIMARY KEY,  -- UUID stored as CHAR(36) for wishlist ID
    user_id CHAR(36),  -- Foreign Key referencing Users table (the user who added the product)
    product_id CHAR(36),  -- Foreign Key referencing Products table (the product added to the wishlist)
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Timestamp when the product was added to the wishlist
    FOREIGN KEY (user_id) REFERENCES users(id),  -- Foreign key constraint linking to Users table
    FOREIGN KEY (product_id) REFERENCES products(id)  -- Foreign key constraint linking to Products table
);

