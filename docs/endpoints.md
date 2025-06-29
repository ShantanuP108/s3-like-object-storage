# 📚 API Endpoint Guide

This document outlines the main endpoints in your S3-like Object Storage System.

---

## 🔐 Authentication

- `POST /auth/register`  
  - Request:
    ```json
    { "username": "user", "password": "pass" }
    ```

- `POST /auth/login`  
  - Response:
    ```json
    { "access_token": "...", "token_type": "bearer" }
    ```

---

## 🪣 Bucket Management

- `POST /bucket/create?bucket_name=demo`
- `GET /bucket/test`

---

## 📦 Object Storage

> ⚠️ All routes require:
> `Authorization: Bearer <your_token>`

- `POST /object/upload?bucket_name=demo`  
  - Form Data: file=UploadFile

- `GET /object/list?bucket_name=demo`

- `GET /object/download?bucket_name=demo&file_name=file.txt`

- `DELETE /object/delete?bucket_name=demo&file_name=file.txt`

---

## 🧪 Swagger UI

Visit: [http://localhost:8000/docs](http://localhost:8000/docs)
