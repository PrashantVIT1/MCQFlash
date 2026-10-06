/**
 * Compress an image by resizing and converting to JPEG
 * @param {File} file - The original image file
 * @param {number} maxSize - Maximum width/height in pixels (default: 1280)
 * @param {number} quality - JPEG quality 0-1 (default: 0.80)
 * @returns {Promise<Blob>} - Compressed image as Blob
 */
export async function compressImage(file, maxSize = 1280, quality = 0.80) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    img.onload = () => {
      // Calculate new dimensions while preserving aspect ratio
      let width = img.width;
      let height = img.height;

      // Only resize if larger than maxSize
      if (width > maxSize || height > maxSize) {
        if (width > height) {
          height = (height * maxSize) / width;
          width = maxSize;
        } else {
          width = (width * maxSize) / height;
          height = maxSize;
        }
      }

      // Set canvas dimensions
      canvas.width = Math.round(width);
      canvas.height = Math.round(height);

      // Draw image to canvas
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

      // Convert to JPEG blob
      canvas.toBlob(
        (blob) => {
          if (blob) {
            resolve(blob);
          } else {
            reject(new Error('Failed to compress image'));
          }
        },
        'image/jpeg',
        quality
      );
    };

    img.onerror = () => {
      reject(new Error('Failed to load image'));
    };

    // Load image from file
    const reader = new FileReader();
    reader.onload = (e) => {
      img.src = e.target.result;
    };
    reader.onerror = () => {
      reject(new Error('Failed to read file'));
    };
    reader.readAsDataURL(file);
  });
}
