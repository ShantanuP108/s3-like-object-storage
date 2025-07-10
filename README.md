# ☁️ S3-Like Object Storage System (FastAPI + JWT + CI/CD + Render)

This project is a lightweight S3-inspired object storage API built using **FastAPI**. It supports features like nested folders, versioned file uploads, presigned download links, JWT-based authentication, and more — all deployable on **Render**, with CI/CD support via GitHub Actions.

---

## 🚀 Features

- 🔐 JWT-based Authentication & Authorization
- 🪣 Bucket Management (Create, List, Delete)
- 📂 Object Storage:
  - Upload with version control
  - Download files or specific versions
  - Nested folders via key structure (e.g. `images/avatar.jpg`)
  - Delete objects
- 📜 Object Metadata & Version Listing
- 🔗 Expiring (Presigned) Download Links
- 🧱 File Size Limit (100MB enforced)
- 🧮 Storage Quota Tracking (WIP)
- ✅ Unit Testing with `pytest` + FastAPI TestClient
- ⚙️ CI/CD with GitHub Actions
- 🚢 Live Deployment on [Render](https://s3-like-object-storage.onrender.com)

---

## 🧭 API Routes

| Method   | Endpoint                            | Description                           |
|----------|-------------------------------------|---------------------------------------|
| `POST`   | `/auth/register`                    | Register a new user                   |
| `POST`   | `/auth/login`                       | Login and get JWT token               |
| `POST`   | `/bucket/create`                    | Create a new bucket                   |
| `GET`    | `/bucket/list`                      | List user buckets                     |
| `POST`   | `/object/upload`                    | Upload file (with versioning)         |
| `GET`    | `/object/list`                      | List objects in a bucket/folder       |
| `GET`    | `/object/download`                  | Download a file                       |
| `GET`    | `/object/versions`                  | List versions of a file               |
| `GET`    | `/object/download-version`          | Download a specific version           |
| `GET`    | `/object/presign`                   | Get expiring presigned download URL   |
| `DELETE` | `/object/delete`                    | Delete a file                         |
| `GET`    | `/`                                  | Root route with welcome message       |

> ✅ All routes (except `/` and `/auth/*`) require a valid **Bearer Token**.

---

## 🧪 Run Tests

'''bash 
pytest -q

Unit tests include:

User auth & login

Object upload, list & download

Presigned link verification

🛠 Folder Structure
s3-like-object-storage/
├── auth/                # Auth routes & schemas
├── bucket/              # Bucket management
├── objects/             # File handling logic
├── core/                # Security, DB setup
├── models/              # Pydantic & SQLAlchemy models
├── tests/               # Unit tests
├── storage/             # Local file storage
├── start.sh             # Render startup command
├── .render.yaml         # Render deployment config
├── requirements.txt     # Python dependencies
├── main.py              # FastAPI app entrypoint
└── README.md


🧪 Tech Stack
| Category      | Tools                       |
| ------------- | --------------------------- |
| Web Framework | FastAPI                     |
| Auth          | JWT + OAuth2PasswordBearer  |
| Database      | SQLite + SQLAlchemy         |
| Testing       | Pytest + FastAPI TestClient |
| CI/CD         | GitHub Actions              |
| Deployment    | Render                      |


🚀 Deployment on Render
Project is live at:

🌐 https://s3-like-object-storage.onrender.com


🧑‍💻 Running Locally

# 1. Clone the repo
git clone https://github.com/ShantanuP108/s3-like-object-storage.git
cd s3-like-object-storage

# 2. Create virtualenv
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
uvicorn main:app --reload

Visit: http://127.0.0.1:8000/docs for Swagger UI.


🧪 CI/CD (GitHub Actions)
✅ Linting

✅ Unit Testing

✅ Auto Deploy on main branch push (via Render webhook)

👤 Author
Shantanu Pandey
DevOps Intern • BTech Student • FastAPI Enthusiast

🔗 GitHub: ShantanuP108

✅ Give it a ⭐️ if you liked the project
