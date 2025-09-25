#!/usr/bin/python3 
"""
User model that inherits from BaseModel
"""
from .base_model import BaseModel


class User(BaseModel):
    email = ""
    password = ""
    first_name = ""
    last_name = ""
