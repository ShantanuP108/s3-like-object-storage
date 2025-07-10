import uuid

def test_register_and_login(client):
    username = f"alice_{uuid.uuid4().hex[:6]}"
    password = "pass"

    r = client.post("/auth/register", json={"username": username, "password": password})
    assert r.status_code == 200

    r = client.post(
        "/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert token
