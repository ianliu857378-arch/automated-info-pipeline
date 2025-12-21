import os
import requests
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor

class ImageProcessor:
    def __init__(self, input_dir="data/raw_images", output_dir="data/processed_images"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        # Ensure directories exist
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def download_image(self, url, filename):
        """Downloads a single image from a URL."""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                image_path = os.path.join(self.input_dir, filename)
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                print(f"⬇️ Downloaded: {filename}")
                return image_path
            else:
                print(f"❌ Failed to download {url}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Error downloading {url}: {e}")
        return None

    def batch_download(self, urls):
        """Downloads multiple images in parallel using threads."""
        print(f"🚀 Starting batch download for {len(urls)} images...")
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Create filenames based on index
            futures = [
                executor.submit(self.download_image, url, f"image_{i+1}.jpg")
                for i, url in enumerate(urls)
            ]
            for future in futures:
                future.result() # Wait for completion

    def process_images(self, target_size=(600, 800), format="JPEG"):
        """
        Batch processes images in the input directory:
        1. Resizes/Crops to target_size (e.g., ID card standard).
        2. Converts to standard format (e.g., JPEG).
        3. Optimizes for file size.
        """
        print(f"⚙️ Processing images from {self.input_dir}...")
        
        processed_count = 0
        for filename in os.listdir(self.input_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                img_path = os.path.join(self.input_dir, filename)
                try:
                    with Image.open(img_path) as img:
                        # Convert to RGB (in case of RGBA PNGs) check for transparency
                        if img.mode in ('RGBA', 'P'):
                            img = img.convert('RGB')
                        
                        # Resize (Thumbnail / Aspect Ratio Preserved)
                        img.thumbnail(target_size)
                        
                        # Create new filename
                        new_filename = os.path.splitext(filename)[0] + ".jpg"
                        output_path = os.path.join(self.output_dir, new_filename)
                        
                        # Save
                        img.save(output_path, format=format, quality=85, optimize=True)
                        processed_count += 1
                        print(f"✅ Processed: {new_filename}")
                        
                except Exception as e:
                    print(f"❌ Error processing {filename}: {e}")
        
        print(f"🎉 Batch processing complete. {processed_count} images saved to {self.output_dir}.")

if __name__ == "__main__":
    # Example Usage
    processor = ImageProcessor()
    
    # Mock URLs for demonstration
    mock_urls = [
        "https://via.placeholder.com/1200x1600.png?text=Photo+1",
        "https://via.placeholder.com/800x800.png?text=Photo+2",
        "https://via.placeholder.com/1024x768.png?text=Photo+3"
    ]
    
    # 1. Download
    processor.batch_download(mock_urls)
    
    # 2. Process
    processor.process_images(target_size=(300, 400))
