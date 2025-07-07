![Deploy](https://github.com/ShantanuP108/s3-like-object-storage/actions/workflows/deploy.yml/badge.svg)

cat > README.md << 'EOF'
# 🗂️ S3-like Object Storage System (FastAPI + SQLite + JWT)

A self-hosted object storage system inspired by **Amazon S3**, built with **FastAPI**, **JWT authentication**, and **SQLite**. Supports bucket and object management, secure access, file versioning, and full REST API via Swagger.

🔗 **Live Demo:** [https://s3-like-object-storage.onrender.com/docs](https://s3-like-object-storage.onrender.com/docs)

---

## 🚀 Features

- 🔐 **User Authentication** (JWT-based)
- 🪣 **Bucket Management** (create your own storage space)
- 📦 **File Upload/Download**
- 📄 **Versioning Support** (old uploads retained)
- 🧾 **List & Delete Objects**
- 🧠 **Metadata Tracking** (timestamps for versions)
- 📚 **Interactive API Docs** with Swagger UI

---

## 📂 Folder Structure
s3-like-object-storage/
├── auth/ # Authentication routes
├── bucket/ # Bucket creation route
├── core/ # DB, Security
├── models/ # SQLAlchemy Models
├── objects/ # Upload, download, versioning
├── storage/ # User files saved here
├── main.py # FastAPI entrypoint
├── init_db.py # Optional: DB setup
├── requirements.txt
├── start.sh # For Render deployment
└── .render.yaml # Render service definition



