from pathlib import Path

from fastapi import Response
from fastapi.testclient import TestClient

from main import app

BASE_DIR = Path(__file__).parent.parent.absolute()
client = TestClient(app)


def test_valid_images():
    image_files = ["image_1.jpg", "image_2.jpg", "image_3.jpg"]

    for image_file in image_files:
        image_path: Path = (BASE_DIR / "tests" / "files" / image_file).resolve()
        with open(image_path, "rb") as f:
            response: Response = client.post("/classify", files={"file": f.read()})

        assert response.status_code == 200
        assert "predictions" in response.json()


def test_invalid_files():
    non_image_files = ["non_image_1.jpg"]

    for non_image_file in non_image_files:
        non_image_path: Path = (BASE_DIR / "tests" / "files" / non_image_file).resolve()
        with open(non_image_path, "rb") as f:
            response = client.post("/classify", files={"file": f.read()})

        assert response.status_code != 200


def test_empty_post():
    response = client.post("/classify")
    assert response.status_code != 200
