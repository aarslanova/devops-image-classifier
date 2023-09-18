"""
This script defines all the necessary util classes and functions for the main.py
"""
import enum
from collections import namedtuple
from enum import Enum
from pathlib import Path

import torch
import torchvision.transforms._presets as P
import torchvision.transforms.functional as F
from fastapi import HTTPException
from fastapi import UploadFile
from PIL import Image
from PIL import UnidentifiedImageError
from torch import nn
from torchvision import models
from torchvision.models import ResNet50_Weights


# Models and PyTorch

ModelInfo = namedtuple(
    "ModelInfo",
    ["model_name", "crop_size", "resize_size", "interpolation", "is_fallback"],
)


# Models and PyTorch

ModelInfo = namedtuple(
    "ModelInfo",
    ["model_name", "crop_size", "resize_size", "interpolation", "is_fallback"],
)


@enum.unique
class Models(Enum):
    """This enum contains implemented models"""

    VIT16 = ModelInfo("wide_resnet", 224, 232, F.InterpolationMode.BILINEAR, False)
    MOBILENET = ModelInfo(
        "mobilenet_v3_large", 224, 232, F.InterpolationMode.BILINEAR, True
    )

    @classmethod
    def get_modelinfo(cls, value: str) -> ModelInfo:
        for member in cls:
            if member.value.model_name == value:
                return member.value
        raise ValueError(f"Model {value} is not supported.")

    @classmethod
    def get_model(cls, value: str) -> nn.Module:
        for member in cls:
            if member.value.model_name == value:
                return models.get_model(value)
        raise ValueError(f"Model {value} is not supported.")

    @classmethod
    def get_fallback_model(cls) -> str:
        for member in cls:
            if member.value.is_fallback:
                return member.value.model_name
        raise AttributeError("No fallback models defined.")


def get_transformations(model_name: str) -> nn.Module:
    """
    Returns image transformations module based on the given model name.
    """
    model_info = Models.get_modelinfo(model_name)
    transformations = P.ImageClassification(
        crop_size=model_info.crop_size,
        resize_size=model_info.resize_size,
        interpolation=model_info.interpolation,
    )
    return transformations


def get_categories() -> list[str]:
    """This function returns names of the categories.
    All models share the same categories, this is why ResNet_Weights class can be used
    """
    return ResNet50_Weights.DEFAULT.meta["categories"]


def prepare_model(model_name: str, weights_path: Path) -> nn.Module:
    """
    Loads and prepares the model for inference.
    """
    model = Models.get_model(model_name)
    model.eval()
    model.load_state_dict(torch.load(weights_path))
    return model


def get_category_preds(
    model: nn.Module, transforms: nn.Module, img: Image, category_list: list[str]
) -> list[str]:
    """
    Returns category predictions for the given image.
    """
    with torch.inference_mode():
        predictions = model(transforms(img).unsqueeze(0))
        class_ids = torch.topk(predictions.squeeze(0).softmax(0), 5).indices
        category_names = [category_list[class_id.item()] for class_id in class_ids]
        return category_names


# FastAPI utilities


def load_image(file: UploadFile) -> Image:
    """
    Opens and returns an image from the uploaded file.
    """
    try:
        return Image.open(file.file).convert("RGB")
    except UnidentifiedImageError:
        raise HTTPException(status_code=422, detail="Supported formats: JPG, PNG.")


def get_predictions_with_model(
    model: nn.Module, transformations: nn.Module, img: Image, categories: list[str]
) -> list[str]:
    """
    Wrapper function to get predictions and handle exceptions.
    """
    try:
        return get_category_preds(model, transformations, img, categories)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def setup_model(model_name: str, base_dir: Path) -> tuple[nn.Module, nn.Module]:
    """Sets up the model based on its name."""
    weights_path = next(base_dir.glob(model_name + "*"))
    model = prepare_model(model_name, weights_path)
    transformations = get_transformations(model_name)
    return model, transformations
