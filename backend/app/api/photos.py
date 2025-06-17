from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlmodel import Session, select
from app.core.database import get_session
from app.models import Photo, PhotoCreate, PhotoResponse, Report
import os
import shutil
from typing import Optional
import uuid
from PIL import Image
from io import BytesIO
from pathlib import Path

router = APIRouter()

# Set up upload directories
UPLOAD_DIR = Path("uploads/photos")
THUMBNAIL_DIR = Path("uploads/thumbnails")

# Create directories if they don't exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)

def create_thumbnail(image_data: bytes, max_size: tuple = (200, 200)) -> bytes:
    """Create a thumbnail from image data"""
    img = Image.open(BytesIO(image_data))
    img.thumbnail(max_size)
    output = BytesIO()
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    img.save(output, format='JPEG')
    output.seek(0)
    return output.getvalue()

@router.get("/", response_model=list[PhotoResponse])
def get_photos(session: Session = Depends(get_session)):
    """Get all photos"""
    statement = select(Photo)
    results = session.exec(statement)
    photos = results.all()
    return photos

@router.get("/{photo_id}", response_model=PhotoResponse)
def get_photo(photo_id: int, session: Session = Depends(get_session)):
    """Get a specific photo by ID"""
    statement = select(Photo).where(Photo.id == photo_id)
    result = session.exec(statement)
    photo = result.first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return photo

@router.post("/", response_model=PhotoResponse)
async def create_photo(
    report_id: int = Form(...),
    image: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """Upload a new photo for a report"""
    # Verify file is an image
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read the file
    image_data = await image.read()
    
    # Generate a unique filename
    file_extension = image.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    
    # Create thumbnail
    thumbnail_data = create_thumbnail(image_data)
    thumbnail_filename = f"thumbnail_{unique_filename}"
    
    # Save full image
    full_image_path = UPLOAD_DIR / unique_filename
    with open(full_image_path, "wb") as f:
        f.write(image_data)
    
    # Save thumbnail
    thumbnail_path = THUMBNAIL_DIR / thumbnail_filename
    with open(thumbnail_path, "wb") as f:
        f.write(thumbnail_data)
    
    # Verify report exists
    report_statement = select(Report).where(Report.id == report_id)
    report_result = session.exec(report_statement)
    report = report_result.first()
    if not report:
        # Delete saved files if report doesn't exist
        os.remove(full_image_path)
        os.remove(thumbnail_path)
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Create photo record
    db_photo = Photo(
        path=str(full_image_path),
        thumbnail=str(thumbnail_path),
        report_id=report_id
    )
    session.add(db_photo)
    session.commit()
    session.refresh(db_photo)
    return db_photo

@router.delete("/{photo_id}")
def delete_photo(photo_id: int, session: Session = Depends(get_session)):
    """Delete a photo by ID"""
    statement = select(Photo).where(Photo.id == photo_id)
    result = session.exec(statement)
    photo = result.first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    # Delete the files
    try:
        if os.path.exists(photo.path):
            os.remove(photo.path)
        if os.path.exists(photo.thumbnail):
            os.remove(photo.thumbnail)
    except Exception as e:
        # Log the error but continue with deletion
        print(f"Error deleting files: {e}")
    
    # Delete the database record
    session.delete(photo)
    session.commit()
    return {"message": "Photo deleted"} 