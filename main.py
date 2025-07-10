STORAGE_PATH = "storage"
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html

from auth.routes import router as auth_router
from bucket.routes import router as bucket_router
from objects.routes import router as object_router

app = FastAPI(
    title="S3-Like Object Storage System",
    version="0.1.0",
    openapi_url=None
)
@app.get("/")
def read_root():
    return {"message": "Welcome to S3-like Object Storage API 🚀"}


# ✅ Add OAuth2PasswordBearer for Swagger Auth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

app.include_router(auth_router, prefix="/auth")
app.include_router(bucket_router, prefix="/bucket")
app.include_router(object_router, prefix="/object")

# Optional: Enable CORS if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description="S3-Like FastAPI Storage",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
