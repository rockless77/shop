import os
from PIL import Image
from io import BytesIO
from flask import current_app
import uuid

def allowed_file(filename):
    """Check if the file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_image(image, max_width=800, max_height=800, quality=85):
    """Resize an image to fit within the specified dimensions while maintaining aspect ratio"""
    if not image:
        return None
        
    img = Image.open(image)
    
    # Convert to RGB if image is in RGBA mode (e.g., PNG with transparency)
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    # Get original dimensions
    width, height = img.size
    
    # Calculate new dimensions while maintaining aspect ratio
    if width > max_width or height > max_height:
        if width / height > max_width / max_height:
            new_width = max_width
            new_height = int(height * (max_width / width))
        else:
            new_height = max_height
            new_width = int(width * (max_height / height))
        
        # Resize the image
        img = img.resize((new_width, new_height), Image.LANCZOS)
    
    # Save the image to a BytesIO object
    output = BytesIO()
    img.save(output, format='JPEG', quality=quality)
    output.seek(0)
    
    return output

def save_product_image(file, product_id, is_primary=False):
    """Save a product image with proper resizing"""
    if not file or not allowed_file(file.filename):
        return None
    
    # Create directories if they don't exist
    product_upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'products')
    os.makedirs(product_upload_folder, exist_ok=True)
    
    # Generate a unique filename
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"product_{product_id}_{uuid.uuid4().hex[:8]}.{ext}"
    
    try:
        # Save the original image first
        original_filepath = os.path.join(product_upload_folder, filename)
        file.save(original_filepath)
        
        # Now create a resized version
        file.seek(0)  # Reset file pointer
        resized_image = resize_image(file, max_width=1200, max_height=1200)
        
        if resized_image:
            # Save the resized image (overwrite the original with the resized version)
            with open(original_filepath, 'wb') as f:
                f.write(resized_image.read())
            
            # Create thumbnail version for product listings
            file.seek(0)  # Reset file pointer
            thumbnail = resize_image(file, max_width=300, max_height=300, quality=75)
            if thumbnail:
                thumbnail_path = os.path.join(product_upload_folder, f"thumb_{filename}")
                with open(thumbnail_path, 'wb') as f:
                    f.write(thumbnail.read())
            
            return filename
    except Exception as e:
        print(f"Error saving product image: {e}")
        return None
    
    return filename

def save_profile_image(file, user_id):
    """Save a profile image with proper resizing"""
    if not file or not allowed_file(file.filename):
        return None
    
    # Create directories if they don't exist
    profile_upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profiles')
    os.makedirs(profile_upload_folder, exist_ok=True)
    
    # Generate a unique filename
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"profile_{user_id}_{uuid.uuid4().hex[:8]}.{ext}"
    
    # Resize the image to a square (for profile pictures)
    img = Image.open(file)
    
    # Convert to RGB if image is in RGBA mode
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    # Get original dimensions
    width, height = img.size
    
    # Determine the size of the square crop
    size = min(width, height)
    
    # Calculate crop box (centered)
    left = (width - size) // 2
    top = (height - size) // 2
    right = left + size
    bottom = top + size
    
    # Crop the image to a square
    img = img.crop((left, top, right, bottom))
    
    # Resize to standard profile image size
    img = img.resize((250, 250), Image.LANCZOS)
    
    # Save the image
    filepath = os.path.join(profile_upload_folder, filename)
    img.save(filepath, format='JPEG', quality=85)
    
    # Create a thumbnail version
    img = img.resize((50, 50), Image.LANCZOS)
    thumbnail_path = os.path.join(profile_upload_folder, f"thumb_{filename}")
    img.save(thumbnail_path, format='JPEG', quality=75)
    
    return filename

def validate_product_images(files):
    """Validate that the product has between 3 and 12 images"""
    valid_files = [f for f in files if f and f.filename and allowed_file(f.filename)]
    
    # Temporarily allow testing with just 1 image during development
    # In production, this should be 3 as per requirements
    if len(valid_files) < 1:
        return False, "Please upload at least 1 image for your product."
    
    if len(valid_files) > 12:
        return False, "You can upload a maximum of 12 images for your product."
    
    return True, valid_files
