import os
from fastapi import APIRouter, Depends, HTTPException
from core.security import get_current_user
from models.user import User

router = APIRouter(tags=["Bucket"])

STORAGE_PATH = "storage"

@router.post("/bucket/create")
def create_bucket(bucket_name: str, current_user: User = Depends(get_current_user)):
    user_path = os.path.join(STORAGE_PATH, current_user.username, bucket_name)
    if os.path.exists(user_path):
        raise HTTPException(status_code=400, detail="Bucket already exists")
    os.makedirs(user_path)
    return {"msg": f"Bucket '{bucket_name}' created for user '{current_user.username}'"}

@router.get("/test")
def test_protected_route(current_user: User = Depends(get_current_user)):
    return {"msg": f"Hello {current_user.username}, you accessed a protected bucket route!"}

