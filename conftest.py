import os, shutil, pytest, asyncio
from fastapi.testclient import TestClient
from main import app, STORAGE_PATH

@pytest.fixture(scope="session")
def client():
    return TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def clean_storage():
    # isolate tests: wipe storage dir once per session
    if os.path.exists(STORAGE_PATH):
        shutil.rmtree(STORAGE_PATH)
    yield
    if os.path.exists(STORAGE_PATH):
        shutil.rmtree(STORAGE_PATH)
