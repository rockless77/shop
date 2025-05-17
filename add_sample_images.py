import os
import sys
from app import app, db, Product, ProductImage

def add_sample_images():
    """Add sample images to existing products in the database"""
    with app.app_context():
        # Get all products without images
        products = Product.query.all()
        
        if not products:
            print("No products found in the database.")
            return False
        
        count = 0
        for product in products:
            # Skip products that already have images
            if product.images:
                continue
                
            # Create a new product image
            image = ProductImage(
                filename="sample_product.svg",
                product_id=product.id,
                is_primary=True
            )
            
            db.session.add(image)
            count += 1
        
        if count > 0:
            db.session.commit()
            print(f"Success: Added sample images to {count} products.")
            return True
        else:
            print("No products without images found.")
            return False

if __name__ == "__main__":
    success = add_sample_images()
    sys.exit(0 if success else 1)
