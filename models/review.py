#!/usr/bin/python3 
"""
Review model that inherits from BaseModel
"""
from .base_model import BaseModel


class Review(BaseModel):
    place_id = ""
    user_id = ""
    text = ""
