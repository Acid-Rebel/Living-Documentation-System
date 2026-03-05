import pytest
from fastapi.testclient import TestClient
from core.api import app
import json

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Welcome to Streaming API" in data["message"]
    assert "endpoints" in data

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["service"] == "deepwiki-api"

def test_auth_status():
    response = client.get("/auth/status")
    assert response.status_code == 200
    data = response.json()
    assert "auth_required" in data

def test_models_config():
    response = client.get("/models/config")
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    assert "defaultProvider" in data

def test_local_repo_structure_no_path():
    response = client.get("/local_repo/structure")
    assert response.status_code == 400
    assert response.json()["error"] == "No path provided. Please provide a 'path' query parameter."

def test_local_repo_structure_invalid_path():
    response = client.get("/local_repo/structure?path=/invalid/path/that/does/not/exist")
    assert response.status_code == 404
    assert "Directory not found" in response.json()["error"]

def test_get_lang_config():
    response = client.get("/lang/config")
    assert response.status_code == 200
    data = response.json()
    assert "supported_languages" in data
    assert "default" in data
