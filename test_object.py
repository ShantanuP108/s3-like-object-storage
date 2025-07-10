def _token(client):
    client.post("/auth/register", json={"username": "bob", "password": "pass"})
    r = client.post(
        "/auth/login",
        data="username=bob&password=pass",
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return r.json()["access_token"]
