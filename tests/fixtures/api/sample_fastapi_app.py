from fastapi import APIRouter, FastAPI


app = FastAPI()


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/items")
async def create_item(item: dict):
    return item


router = APIRouter(prefix="/v1")


@router.get("/users/{user_id}")
async def get_user(user_id: str):
    return {"id": user_id}


@router.patch("/users/{user_id}")
async def update_user(user_id: str, payload: dict):
    return {"id": user_id, **payload}


app.include_router(router)
