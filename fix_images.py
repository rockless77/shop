import os
import sys
from app import app, db, Product, ProductImage

def diagnose_images():
    """Diagnose and fix image display issues"""
    with app.app_context():
        print("Diagnosing image display issues...")
        
        # Check if there are any products in the database
        products = Product.query.all()
        print(f"Found {len(products)} products in the database.")
        
        # Check if there are any product images in the database
        images = ProductImage.query.all()
        print(f"Found {len(images)} product images in the database.")
        
        # Check if the upload folder exists
        upload_folder = app.config['UPLOAD_FOLDER']
        print(f"Upload folder: {upload_folder}")
        
        if not os.path.exists(upload_folder):
            print(f"ERROR: Upload folder does not exist: {upload_folder}")
            os.makedirs(upload_folder, exist_ok=True)
            print(f"Created upload folder: {upload_folder}")
        
        # Check if the products folder exists
        products_folder = os.path.join(upload_folder, 'products')
        print(f"Products folder: {products_folder}")
        
        if not os.path.exists(products_folder):
            print(f"ERROR: Products folder does not exist: {products_folder}")
            os.makedirs(products_folder, exist_ok=True)
            print(f"Created products folder: {products_folder}")
        
        # List files in the products folder
        product_files = os.listdir(products_folder) if os.path.exists(products_folder) else []
        print(f"Found {len(product_files)} files in the products folder.")
        
        # Check if the image files referenced in the database actually exist
        for image in images:
            image_path = os.path.join(products_folder, image.filename)
            if not os.path.exists(image_path):
                print(f"ERROR: Image file does not exist: {image_path}")
            else:
                print(f"Image file exists: {image.filename}")
        
        # Create a sample image if needed
        if not product_files:
            print("No product images found. Creating a sample image...")
            sample_image_path = os.path.join(products_folder, "sample_product.svg")
            with open(sample_image_path, 'w') as f:
                f.write('''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
  <rect width="800" height="600" fill="#4dabf7"/>
  <text x="400" y="300" font-family="Arial" font-size="48" font-weight="bold" text-anchor="middle" fill="white">Sample Product</text>
</svg>''')
            print(f"Created sample image: {sample_image_path}")
        
        # Update the database to use the sample image if needed
        if not images and products:
            print("No product images in database. Adding sample image to products...")
            for product in products:
                image = ProductImage(
                    filename="sample_product.svg",
                    product_id=product.id,
                    is_primary=True
                )
                db.session.add(image)
            db.session.commit()
            print(f"Added sample image to {len(products)} products.")

if __name__ == "__main__":
    diagnose_images()
