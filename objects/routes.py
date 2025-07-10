import os
import json
import shutil
import hmac
import base64
import time
from fastapi import Request
from hashlib import sha256
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from core.security import get_current_user
from models.user import User
from utils.storage import get_directory_size


router = APIRouter(tags=["Object"])
STORAGE_PATH = "storage"

MAX_FILE_SIZE_MB = 100
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


SECRET_KEY = "your-super-secret-key"  # You can store this securely via env

def generate_signature(data: str, secret: str) -> str:
    return hmac.new(secret.encode(), data.encode(), sha256).hexdigest()

@router.get("/generate-link")
def generate_expiring_link(
    bucket_name: str,
    key: str,
    expires_in: int = 300,  # seconds (5 mins)
    current_user: User = Depends(get_current_user)
):
    expiry = int(time.time()) + expires_in
    data = f"{current_user.username}/{bucket_name}/{key}/{expiry}"
    signature = generate_signature(data, SECRET_KEY)

    download_url = f"/object/secure-download?bucket_name={bucket_name}&key={key}&expiry={expiry}&signature={signature}"
    return {"url": download_url, "expires_in": expires_in}
# ---------- helper -----------------------------------------------------------
def _abs_path(user: str, bucket: str, key: str = "") -> str:
    """
    Convert bucket + object key into an absolute filesystem path.
    key may contain nested folders like 'photos/2025/img.jpg'.
    """
    safe_key = key.strip("/")

    return os.path.join(STORAGE_PATH, user, bucket, safe_key)


# ---------- upload (with versioning & nested keys) ---------------------------
@router.post("/upload")
def upload_object(
    bucket_name: str,
    key: str,  # use "folder1/file.txt" format for nested
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    bucket_path = os.path.join(STORAGE_PATH, current_user.username, bucket_name)
    versions_path = os.path.join(bucket_path, ".versions")
    metadata_path = os.path.join(bucket_path, ".metadata.json")

    if not os.path.exists(bucket_path):
        raise HTTPException(status_code=404, detail="Bucket does not exist")

    # ✅ Enforce file size limit
    file_bytes = file.file.read()
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {MAX_FILE_SIZE_MB}MB size limit"
        )

    # Save file
    object_path = os.path.join(bucket_path, key)
    os.makedirs(os.path.dirname(object_path), exist_ok=True)
    with open(object_path, "wb") as f:
        f.write(file_bytes)

    # Save versioned copy
    os.makedirs(versions_path, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    safe_key = key.replace("/", "_")
    versioned_name = f"{safe_key}_{timestamp}"
    shutil.copyfile(object_path, os.path.join(versions_path, versioned_name))

    # Update metadata
    metadata = {}
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

    metadata[key] = metadata.get(key, []) + [timestamp]
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)

    return {"msg": "uploaded", "key": key, "version_id": timestamp}



# ---------- download latest --------------------------------------------------
@router.get("/download")
def download_object(
    bucket_name: str,
    key: str,
    current_user: User = Depends(get_current_user)
):
    abs_path = _abs_path(current_user.username, bucket_name, key)
    if not os.path.isfile(abs_path):
        raise HTTPException(404, "File not found")
    return FileResponse(
        abs_path,
        filename=os.path.basename(key),
        media_type="application/octet-stream"
    )


# ---------- download specific version ----------------------------------------
@router.get("/download-version")
def download_version(
    bucket_name: str,
    key: str,
    version: str,
    current_user: User = Depends(get_current_user)
):
    # Sanitize key to match how it was saved
    sanitized_key = key.replace("/", "_")

    versioned_file = f"{current_user.username}_{bucket_name}_{sanitized_key}_{version}"
    version_path = os.path.join(
        STORAGE_PATH,
        current_user.username,
        bucket_name,
        ".versions",
        versioned_file
    )

    if not os.path.exists(version_path):
        raise HTTPException(status_code=404, detail="Version not found")

    return FileResponse(path=version_path, filename=key.split("/")[-1], media_type='application/octet-stream')



# ---------- list objects -----------------------------------------------------
@router.get("/list")
def list_objects(
    bucket_name: str,
    prefix: str = "",                       # <── optionally list a "folder"
    current_user: User = Depends(get_current_user)
):
    bucket_root = _abs_path(current_user.username, bucket_name)
    target_dir  = _abs_path(current_user.username, bucket_name, prefix)

    if not os.path.isdir(target_dir):
        raise HTTPException(404, "Bucket or folder not found")

    # load version metadata
    meta_path = os.path.join(bucket_root, ".metadata.json")
    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path, "r") as fp:
            meta = json.load(fp)

    objects = []
    for root, _, files in os.walk(target_dir):
        for f in files:
            if f.startswith("."):
                continue
            full_path = os.path.join(root, f)
            rel_key = os.path.relpath(full_path, bucket_root)
            stat = os.stat(full_path)
            objects.append({
                "key": rel_key.replace(os.sep, "/"),
                "size": stat.st_size,
                "versions": len(meta.get(rel_key.replace(os.sep, "/"), []))
            })

    return {"bucket": bucket_name, "objects": objects}


# ---------- delete latest ----------------------------------------------------
@router.delete("/delete")
def delete_object(
    bucket_name: str,
    key: str,
    current_user: User = Depends(get_current_user)
):
    abs_path = _abs_path(current_user.username, bucket_name, key)
    if not os.path.isfile(abs_path):
        raise HTTPException(404, "File not found")
    os.remove(abs_path)
    return {"msg": f"deleted {key}"}


# ---------- list versions ----------------------------------------------------
@router.get("/versions")
def list_versions(
    bucket_name: str,
    key: str,
    current_user: User = Depends(get_current_user)
):
    meta_path = os.path.join(
        _abs_path(current_user.username, bucket_name), ".metadata.json"
    )
    if not os.path.exists(meta_path):
        raise HTTPException(404, "Metadata not found")

    with open(meta_path, "r") as fp:
        meta = json.load(fp)

    versions = meta.get(key)
    if not versions:
        raise HTTPException(404, "No versions for this key")

    return {"key": key, "versions": versions}

@router.get("/secure-download")
def secure_download(
    bucket_name: str,
    key: str,
    expiry: int,
    signature: str,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    expected_data = f"{current_user.username}/{bucket_name}/{key}/{expiry}"
    expected_sig = generate_signature(expected_data, SECRET_KEY)

    if signature != expected_sig:
        raise HTTPException(status_code=403, detail="Invalid signature")

    if time.time() > expiry:
        raise HTTPException(status_code=403, detail="Link expired")

    bucket_path = os.path.join(STORAGE_PATH, current_user.username, bucket_name)
    file_path = os.path.join(bucket_path, key)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=file_path, filename=os.path.basename(key), media_type='application/octet-stream')


@router.get("/usage")
def get_user_storage_usage(current_user: User = Depends(get_current_user)):
    user_path = os.path.join(STORAGE_PATH, current_user.username)
    if not os.path.exists(user_path):
        return {"username": current_user.username, "used_bytes": 0, "used_MB": 0}

    total_bytes = get_directory_size(user_path)
    return {
        "username": current_user.username,
        "used_bytes": total_bytes,
        "used_MB": round(total_bytes / (1024 * 1024), 2)
    }
