import exifread

def extract_exif(image_path):
    """Extract EXIF metadata from an image file"""
    try:
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f)
        return {tag: str(value) for tag, value in tags.items()}
    except Exception as e:
        return {"Error": str(e)}
