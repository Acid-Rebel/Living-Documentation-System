
from fastapi import FastAPI
app = FastAPI()

@app.get("/items/{item_id}")
def read_item(item_id: int):
    """Get item by ID."""
    return {"item_id": item_id}

@app.post("/items")
def create_item():
    """Create a new item."""
    pass
