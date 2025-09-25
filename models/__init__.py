#!/usr/bin/python3 

from .base_model import BaseModel
from .engine.file_storage import FileStorage


storage = FileStorage()
storage.reload()
