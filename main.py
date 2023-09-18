"""
This script defines a FastAPI POST method for classifying images with PyTorch.
It serves vision transformer as the primary model and mobile net as the fallback.

There are two deployment scenarios for this script:

1. Main Image: Serves the vision transformer as the primary model and mobile net as the fallback.
2. Fallback Image: Serves the mobile net as the primary model for a lightweight alternative.

The fallback image serves requests faster. If the main image times out due to overwhelming requests,
the fallback image can handle additional traffic.
"""
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi import File
from fastapi import HTTPException
from fastapi import UploadFile
from PIL import Image

from utils import get_categories
from utils import get_predictions_with_model
from utils import load_image
from utils import Models
from utils import setup_model

# Constants
MODEL_NAME = os.getenv("MODEL_NAME", default="vit_l_16")
FALLBACK_NAME = Models.get_fallback_model()
BASE_DIR = Path(__file__).parent.absolute()
CATEGORIES = get_categories()

# Initialize FastAPI
app = FastAPI()

# Models and Transformations Setup
main_model, main_transformations = setup_model(MODEL_NAME, BASE_DIR)

# Fallback model setup only if it's different from the main model
fallback_weights_path = None
fallback_model = None
fallback_transformations = None
if MODEL_NAME != FALLBACK_NAME:
    fallback_model, fallback_transformations = setup_model(FALLBACK_NAME, BASE_DIR)


@app.post("/classify")
def classify_image(file: UploadFile = File(...)) -> dict[str, list[str]]:
    """
    This function takes image from POST request and sends a list of top 5 classifications
    """
    img: Image = load_image(file)

    try:
        return {
            "predictions": get_predictions_with_model(
                main_model, main_transformations, img, CATEGORIES
            )
        }
    except HTTPException:
        if fallback_weights_path and fallback_model and fallback_transformations:
            return {
                "predictions": get_predictions_with_model(
                    fallback_model, fallback_transformations, img, CATEGORIES
                )
            }
        raise
