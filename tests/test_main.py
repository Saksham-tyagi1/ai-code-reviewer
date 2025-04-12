from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to AI Code Reviewer! Visit /docs for API usage."}

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_analyze_file():
    file_content = """
    def example():
        x = 10
        return x
    """
    
    response = client.post(
        "/analyze/file",
        files={"file": ("test_file.py", file_content, "text/x-python")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "filename" in data
    assert "issues" in data
    assert isinstance(data["issues"], list)
