import uuid

def test_presigned_link(client):
    username = f"bob_{uuid.uuid4().hex[:6]}"
    password = "pass"

    client.post("/auth/register", json={"username": username, "password": password})
    r = client.post(
        "/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert token
