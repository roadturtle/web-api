import asyncio
from os import stat
from fastapi import FastAPI, Path, Query, HTTPException, status
from typing import Optional
from numpy import delete
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    brand: Optional[str] = None

class UpdateItem(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    brand: Optional[str] = None

inventory = {}

@app.get("/")
async def root():
    return {"message": "im awake bitch"}

@app.get("/get-item/{item_id}")
async def get_item(item_id: int = Path(None, description="The ID of the item you'd like to view", gt=0)):
    return inventory[item_id]

@app.get("/get-by-name")
async def get_item(name: str = Query(None, title="Name", description="Name of item", max_length=10, min_length=2)):
    for item_id in inventory:
        if inventory[item_id].name == name:
            return inventory[item_id]
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item name not found.")

@app.post("/create-item/{item_id}")
async def create_item(item_id: Optional[int], item: Item):
    if item_id in inventory:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Item ID already exists.")
    
    inventory[item_id] = item
    return inventory[item_id]

@app.put("/update-item/{item_id}")
async def update_item(item_id: int, item: UpdateItem):
    if item_id not in inventory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item ID does not exist.")
    if item.name != None:
        inventory[item_id].name = item.name
    
    if item.price != None:
        inventory[item_id].price = item.price
    
    if item.brand != None:
        inventory[item_id].brand = item.brand

    return inventory[item_id]

@app.delete("/delete_item")
async def delete_item(item_id: int = Query(..., description="Thw ID of the item to delete", ge=0)):
    if item_id not in inventory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item ID does not exist.")
    
    del inventory[item_id]
    return {"Success": "Item deleted!"}