import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from core.security import get_current_user
from models.user import User

router = APIRouter(tags=["Object"])  # ✅ This must come BEFORE using @router decorators

STORAGE_PATH = "storage"

@router.post("/upload")
def upload_object(bucket_name: str, file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    bucket_path = os.path.join(STORAGE_PATH, current_user.username, bucket_name)
    
    if not os.path.exists(bucket_path):
        raise HTTPException(status_code=404, detail="Bucket does not exist")  

    file_location = os.path.join(bucket_path, file.filename)

    with open(file_location, "wb") as f:
        f.write(file.file.read())
    
    return {"msg": f"File '{file.filename}' uploaded to bucket '{bucket_name}'"}


# ✅ Here's the download route
@router.get("/download")
def download_object(bucket_name: str, file_name: str, current_user: User = Depends(get_current_user)):
    bucket_path = os.path.join(STORAGE_PATH, current_user.username, bucket_name)
    file_path = os.path.join(bucket_path, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path, filename=file_name, media_type='application/octet-stream')

@router.get("/list")
def list_objects(bucket_name: str, current_user: User = Depends(get_current_user)):
    bucket_path = os.path.join(STORAGE_PATH, current_user.username, bucket_name)

    if not os.path.exists(bucket_path):
        raise HTTPException(status_code=404, detail="Bucket not found")

    files = os.listdir(bucket_path)
    return {"bucket": bucket_name, "files": files}

@router.delete("/delete")
def delete_object(bucket_name: str, file_name: str, current_user: User = Depends(get_current_user)):
    bucket_path = os.path.join(STORAGE_PATH, current_user.username, bucket_name)
    file_path = os.path.join(bucket_path, file_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    os.remove(file_path)
    return {"msg": f"File '{file_name}' deleted from bucket '{bucket_name}'"}
