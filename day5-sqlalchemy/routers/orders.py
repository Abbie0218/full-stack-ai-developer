from fastapi import APIRouter,Depends
from database import get_db
from sqlalchemy.orm import Session
import models

router=APIRouter()

@router.post("/orders", status_code=201)
async def create_order(db: Session = Depends(get_db)):
    new_order = models.Python_Order(
        user_id=4,
        product_name="Shoes",
        price=499.99,
        status="completed"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order