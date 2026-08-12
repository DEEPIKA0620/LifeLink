from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MedicineCreate(BaseModel):
    medicine_name: str
    generic_name: str
    category: Optional[str] = "General"
    quantity: int
    unit: Optional[str] = "strips"
    price: float
    availability_status: Optional[str] = "in_stock"

class MedicineUpdate(BaseModel):
    medicine_name: Optional[str] = None
    generic_name: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[int] = None
    unit: Optional[str] = None
    price: Optional[float] = None
    availability_status: Optional[str] = None

class MedicineOut(BaseModel):
    id: int
    pharmacy_id: int
    medicine_name: str
    generic_name: str
    category: str
    quantity: int
    unit: str
    price: float
    availability_status: str
    last_updated: datetime
    created_at: datetime

    class Config:
        from_attributes = True
