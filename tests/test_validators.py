import pytest
from fastapi import HTTPException
from app.utils.validators import validate_public_url

def test_rejects_ftp():
    with pytest.raises(HTTPException):
        validate_public_url("ftp://example.com")

def test_rejects_localhost():
    with pytest.raises(HTTPException):
        validate_public_url("http://localhost")

def test_rejects_credentials():
    with pytest.raises(HTTPException):
        validate_public_url("https://user:pass@example.com")
