
import React, { useState } from 'react';

const ImageGallery = ({ images }) => {
  const [selectedImage, setSelectedImage] = useState(0);

  return (
    <div className="image-gallery">
      <div className="main-image">
        <img 
          src={images[selectedImage]} 
          alt={`Product view ${selectedImage + 1}`}
          className="w-full h-auto rounded-lg"
        />
      </div>
      <div className="thumbnail-grid mt-4 grid grid-cols-4 gap-2">
        {images.map((image, index) => (
          <button
            key={index}
            onClick={() => setSelectedImage(index)}
            className={`thumbnail ${index === selectedImage ? 'ring-2 ring-blue-500' : ''}`}
          >
            <img 
              src={image} 
              alt={`Thumbnail ${index + 1}`}
              className="w-full h-full object-cover rounded"
            />
          </button>
        ))}
      </div>
    </div>
  );
};

export default ImageGallery;