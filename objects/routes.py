import os
import json
import shutil
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from core.security import get_current_user
from models.user import User

router = APIRouter(tags=["Object"])
STORAGE_PATH = "storage"


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
    key: str,                               # <── NEW: full object key
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    bucket_root = _abs_path(current_user.username, bucket_name)
    abs_path    = _abs_path(current_user.username, bucket_name, key)
    versions_dir = os.path.join(bucket_root, ".versions")
    metadata_path = os.path.join(bucket_root, ".metadata.json")

    if not os.path.exists(bucket_root):
        raise HTTPException(404, "Bucket does not exist")

    # ensure parent folders exist
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)

    # 1️⃣ save/overwrite latest
    with open(abs_path, "wb") as f:
        f.write(file.file.read())

    # 2️⃣ version copy
    os.makedirs(versions_dir, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    version_name = abs_path.replace(bucket_root + os.sep, "").replace(os.sep, "_")
    shutil.copyfile(abs_path, os.path.join(versions_dir, f"{version_name}_{ts}"))

    # 3️⃣ update metadata
    meta = {}
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as fp:
            meta = json.load(fp)
    meta.setdefault(key, []).append(ts)
    with open(metadata_path, "w") as fp:
        json.dump(meta, fp, indent=2)

    return {"msg": "uploaded", "key": key, "version_id": ts}


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
