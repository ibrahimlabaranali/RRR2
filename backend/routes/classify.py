from fastapi import APIRouter

router = APIRouter(
    prefix="/classify",
    tags=["Classify"]
)

@router.get("/")
def classify_root():
    return {"message": "Classify endpoint is working."}