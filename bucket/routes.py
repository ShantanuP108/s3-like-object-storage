import os
from fastapi import APIRouter, Depends, HTTPException
from models.user import User
from core.security import get_current_user

router = APIRouter(tags=["Bucket"])

STORAGE_PATH = "storage"

@router.post("/create")
def create_bucket(bucket_name: str, current_user: User = Depends(get_current_user)):
    user_path = os.path.join(STORAGE_PATH, current_user.username)
    os.makedirs(user_path, exist_ok=True)

    bucket_path = os.path.join(user_path, bucket_name)
    if os.path.exists(bucket_path):
        raise HTTPException(status_code=400, detail="Bucket already exists")

    os.makedirs(bucket_path)
    return {"msg": f"Bucket '{bucket_name}' created successfully"}

@router.get("/list")
def list_buckets(current_user: User = Depends(get_current_user)):
    user_path = os.path.join(STORAGE_PATH, current_user.username)
    if not os.path.exists(user_path):
        return {"buckets": []}
    
    buckets = [b for b in os.listdir(user_path) if os.path.isdir(os.path.join(user_path, b))]
    return {"buckets": buckets}

@router.delete("/delete")
def delete_bucket(bucket_name: str, current_user: User = Depends(get_current_user)):
    bucket_path = os.path.join(STORAGE_PATH, current_user.username, bucket_name)
    if not os.path.exists(bucket_path):
        raise HTTPException(status_code=404, detail="Bucket not found")
    
    try:
        os.rmdir(bucket_path)
    except OSError:
        raise HTTPException(status_code=400, detail="Bucket is not empty")

    return {"msg": f"Bucket '{bucket_name}' deleted successfully"}

