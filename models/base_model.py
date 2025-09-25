#!/usr/bin/python3 
"""
Contains the BaseModel class
"""
from datetime import datetime
import uuid

class BaseModel:
    def __init__(self, *args, **kwargs):
        from models import storage
        if kwargs:
            for key, value in kwargs.items():
                if key != "__class__":
                    if key in {"created_at", "updated_at"}:
                        value = datetime.fromisoformat(value)
                    setattr(self, key, value)
        else:
            super().__setattr__("id", str(uuid.uuid4()))
            now = datetime.now()
            super().__setattr__("created_at", now)
            super().__setattr__("updated_at", now)
            storage.new(self)
        

    def __str__(self):
        return f"[{self.__class__.__name__}] ({self.id}) {self.__dict__}"
    
    def __setattr__(self, name, value):
        super().__setattr__(name, value)

    def save(self):
        from models import storage
        super().__setattr__("updated_at", datetime.now())
        storage.save()

    def to_dict(self):
        obj_dict = self.__dict__.copy()
        obj_dict["__class__"] = self.__class__.__name__
        obj_dict["created_at"] = self.created_at.isoformat()
        obj_dict["updated_at"] = self.updated_at.isoformat()
        return obj_dict





if __name__ == "__main__":
    test_model = BaseModel()
    print(test_model.to_dict())
