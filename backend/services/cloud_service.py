import cloudinary
import cloudinary.uploader
import cloudinary.api
from config.config import (
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
    CLOUDINARY_CLOUD_NAME,
)

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True
)

cloudinary_available = all([
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
])

def upload_file(file_path, resource_type="auto", public_id=None):
    """
    Upload a file to Cloudinary
    
    Args:
        file_path (str): Path to the file to upload
        resource_type (str): Type of resource (image, video, raw)
        public_id (str, optional): Public ID for the uploaded file
        
    Returns:
        dict: Upload result containing URL and other metadata, or None if failed
    """
    if not cloudinary_available:
        print("Cloudinary is not configured; skipping upload.")
        return None

    try:
        # Upload file to Cloudinary
        result = cloudinary.uploader.upload(
            file_path,
            resource_type=resource_type,
            public_id=public_id,
            use_filename=True,
            unique_filename=False
        )
        return result
    except Exception as e:
        print(f"Error uploading file to Cloudinary: {e}")
        return None

def get_file_url(public_id, resource_type="auto"):
    """
    Get the URL of a file in Cloudinary
    
    Args:
        public_id (str): Public ID of the file
        resource_type (str): Type of resource (image, video, raw)
        
    Returns:
        str: URL of the file
    """
    if not cloudinary_available:
        print("Cloudinary is not configured; cannot create URL.")
        return None

    try:
        url = cloudinary.utils.cloudinary_url(public_id, resource_type=resource_type)[0]
        return url
    except Exception as e:
        print(f"Error getting file URL from Cloudinary: {e}")
        return None
