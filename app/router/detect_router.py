import requests
from fastapi import APIRouter

from app.core.model import HttpResponse, success_response
from app.core.api import DetectAPI
from app.text_detection import *


router = APIRouter()

@router.get("/detect/test-file", response_model=HttpResponse)
async def test_file():
    card = detect_text_from_base64(
        file_to_base64(r"C:\Users\ADMIN\Pictures\20194060-Trần Công Hoàng.jpg")
    )
    return success_response(data=card)

@router.get("/detect/test-cam", response_model=HttpResponse)
async def test_cam():
    url = "http://192.168.1.13:8080/photo.jpg"
    response = requests.get(url, timeout=2)
    img_data = response.content
    card = detect_text_from_base64(
        byte_to_base64(img_data)
    )
    return success_response(data=card)